import time, helpers, random, asyncio, json
from constants import GameState, STATE, USERS, PLAYERS, AXIS_LETTERS, AXIS_NUMBERS
from logger import game_logger

# Get the board that the user should be attacking
def get_target_board(game_boards, user):
    target_board_index = list(game_boards).index(user.remote_address[1]) + 1
    if target_board_index >= len(game_boards):
        target_board_index = 0
    return list(game_boards)[target_board_index]

# Remove a board from the game
def remove_board(game_boards, user, message = "player disconnect"):
    if game_boards[user.remote_address[1]]:
        game_boards.pop(user.remote_address[1])
        game_logger.debug(f"A game board has been removed due to {message}. The currently active boards are: {game_boards}")

def user_action(data, user):
    # Exit conditions are handled in their own conditional
    if data["action"] == "exit":
        game_logger.debug(f"calling 'exit' action on player from port {str(user.remote_address[1])}")
        PLAYERS.discard(user)
        if (len(PLAYERS) < 2): 
            return
        if STATE["game_state"] == GameState.SETUP_BOARDS:
            remove_board(STATE["game_boards"], user, "player disconnect")
        elif STATE["game_state"] == GameState.TURN_START or STATE["game_state"] == GameState.TURN_END:
            if STATE["game_state"] == GameState.TURN_START:
                # Remove any attack the player has engaged in this turn
                target_board = get_target_board(STATE["game_boards"], user)
                if STATE["attacks"].pop(target_board, None) != None:
                    game_logger.debug(f"A previous attack by the player from port {str(user.remote_address[1])} has been removed from the 'attacks' dictionary")
            # Get the index of the exiting player's board before removing it from the ordered dict so we can determine the identity of their designated attacker
            attacking_player_index = list(STATE["game_boards"]).index(user.remote_address[1]) - 1
            remove_board(STATE["game_boards"], user, "player disconnect")
            if attacking_player_index < 0:
                attacking_player_index = len(STATE["game_boards"]) - 1
            attacking_player_port = list(STATE["game_boards"].keys())[attacking_player_index]
            # Get the designated attacker's websocket
            attacking_player = helpers.get_websocket_from_remote_port(attacking_player_port, PLAYERS)
            # Notify the designated attacker that their previous opponent has left along with the game state so client knows how to respond
            game_logger.debug(f"Notifying player from port {attacking_player_port} that their opponent has left and a new one shall be assigned")
            asyncio.run(helpers.send(attacking_player, json.dumps({"type" : "notification", "content": "opponent left", "state": STATE["game_state"] })))
    else:
    # Other user actions are confined to certain game states
        if STATE["game_state"] == GameState.LOBBY:
            if data["action"] == "ready":
                game_logger.debug(f"Adding user from port {str(user.remote_address[1])} to the list of ready players")
                PLAYERS.add(user)
        if STATE["game_state"] == GameState.TURN_START:
            if data["action"] == "attack":
                target_board = get_target_board(STATE["game_boards"], user)
                target = data["target"]
                STATE["attacks"][target_board] = target

def change_state(gameState):
    STATE["game_state"] = gameState
    STATE["entering_state"] = True

# Basic finite state machine implementation
def update():
    if STATE["game_state"] == GameState.LOBBY:
        # Reset the player count when initializing the lobby
        if STATE["entering_state"]:
            game_logger.info("The game lobby is now open.")
            helpers.message_all(
                USERS,
                {"type": "game_state", "state": GameState.LOBBY}
            )
            PLAYERS.clear()
            STATE["entering_state"] = False
        # If any users are not ready or there are less than 2 users, notify all users every 3 seconds on the lobby status.
        if len(PLAYERS) != len(USERS) or len(USERS) < 2:
            time.sleep(3)
            game_logger.debug(f"{str(len(PLAYERS))} out of {str(len(USERS))} players are ready. Notifying all users on the lobby status.")
            helpers.message_all(
                USERS,
                {"type": "game_state", "state": GameState.LOBBY}
            )
        # If all users are ready, begin the game
        else:
            change_state(GameState.SETUP_BOARDS)
            game_logger.info(f"All users are ready. Now broadcasting the game start message to all players.")
            helpers.message_all(
                USERS,
                {"type": "user_message", "content": "All users are ready! The game will now commence."}
            )

    elif STATE["game_state"] == GameState.SETUP_BOARDS:
        # Initial setup of boards
        if STATE["entering_state"]:
            STATE["game_boards"].clear()
            for player in PLAYERS:
                # Generate a random coordinate to be the player's ship position
                ship_position = str(AXIS_NUMBERS[random.randint(0, 9)]) + AXIS_LETTERS[random.randint(0, 9)]
                STATE["game_boards"][player.remote_address[1]] = ship_position
                asyncio.run(helpers.send(player, json.dumps({"type" : "user_message", "content": f"Your ship is positioned at {ship_position}!"})))
            game_logger.debug(f"Game boards have been set and co-ordinates of player ships have been assigned: {str(STATE['game_boards'])}")
            STATE["entering_state"] = False
        # Ensure there are still more than 2 players in the game before starting
        if len(PLAYERS) < 2:
            helpers.message_all(
                USERS, 
                {"type" : "user_message", "content": f"Insufficient players, returning you to the lobby."}
            )
            game_logger.info(f"Returning to the lobby due to insufficient players in the game")
            change_state(GameState.LOBBY)
        else:
            helpers.message_all(
                USERS, 
                {"type" : "user_message", "content": f"All ships have been placed. Get ready!"}
            )
            game_logger.debug(f"Now commencing the first turn of the game.")
            change_state(GameState.TURN_START)
    elif STATE["game_state"] == GameState.TURN_START:
        if STATE["entering_state"]:
            STATE["attacks"].clear()
            helpers.message_all(
                USERS, 
                {"type" : "game_state", "state" : GameState.TURN_START}
            )
            game_logger.debug(f"Players have been notified that turn has started. Now listening for player attack targets.")
            STATE["entering_state"] = False
        if len(PLAYERS) < 2:
            helpers.message_all(
                USERS, 
                {"type" : "user_message", "content": f"Insufficient players, returning you to the lobby."}
            )
            game_logger.info(f"Returning to the lobby due to insufficient players in the game")
            change_state(GameState.LOBBY)
        elif set(STATE["attacks"].keys()) == set(STATE["game_boards"].keys()):
            game_logger.debug(f"All player targets have been received: {str(STATE['attacks'])}. Proceeding to calculate hits.")
            change_state(GameState.TURN_END)
    elif STATE["game_state"] == GameState.TURN_END:
        if STATE["entering_state"]:
            game_boards_copy = STATE["game_boards"].copy()
            # Check for hits
            sunk_counter = 0
            for key, value in game_boards_copy.items():
                if len(PLAYERS) == 1:
                    break
                if STATE["attacks"][key] == value:
                    sunk_counter += 1
                    player = helpers.get_websocket_from_remote_port(key, PLAYERS)
                    game_logger.info(f"The ship belonging to the player from port {str(player.remote_address[1])} has been hit. Now notifying them and removing them and their board from the game")
                    PLAYERS.discard(player)
                    asyncio.run(helpers.send(player, json.dumps({"type" : "notification", "content": "you lose" })))
                    STATE["game_boards"].pop(key)
            STATE["entering_state"] = False
        if len(PLAYERS) == 1:
            winner = PLAYERS.pop()
            asyncio.run(helpers.send(winner, json.dumps({"type" : "notification", "content": "you win" })))    
            game_logger.info(f"Player from port {str(winner.remote_address[1])} is the sole surviver. Now notifying all users that they have won the game.")
            helpers.message_all(
                USERS, 
                {"type" : "user_message", "content": f"The second last ship has been sunk. Player {winner.remote_address[1]} has won the game! The lobby is now open for the next round"}
            )
            game_logger.info(f"Starting a new game...")
            change_state(GameState.LOBBY)
        else:
            helpers.message_all(
                USERS,
                {"type" : "user_message", "content": f"Turn ended. A total of {sunk_counter} ship(s) has/have been sunk! There are {len(PLAYERS)} players remaining!"}
            )
            game_logger.debug(f"The turn has ended. A status update has been sent to all users: A total of {sunk_counter} ship(s) have been sunk and there are {str(len(PLAYERS))} players remaining.")
            change_state(GameState.TURN_START)

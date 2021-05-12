import asyncio, json, random, helpers
from constants import ClientState, GameState, STATE, AXIS_LETTERS, AXIS_NUMBERS

def server_data(websocket, data):
    # Display any user messages received from the server 
    if data["type"] == "user_message":
        print(data["content"])

    # The server will send a game state message upon changing states (or periodically in the lobby)
    elif data["type"] == "game_state":
        # If the server's lobby is open, place the client in lobby state if they are not already
        if data["state"] == GameState.LOBBY:
            if STATE["client_state"] != (ClientState.LOBBY_READY or ClientState.LOBBY_UNREADY):
                STATE["client_state"] = ClientState.LOBBY_UNREADY
            else:
                print("Waiting on other users to become ready...")

        # If a game is currently running, set client state based on game state
        if STATE["client_state"] == ClientState.DEFAULT:
                STATE["client_state"] = ClientState.OBSERVER
                print("A match is currently in progress, please observe until it is over.")
        elif STATE["client_state"] == ClientState.LOBBY_READY:
            if data["state"] == GameState.TURN_START:
                STATE["client_state"] = ClientState.NEW_OPPONENT
        elif STATE["client_state"] == ClientState.AFTER_MOVE:
            if data["state"] == GameState.TURN_START:
                STATE["client_state"] = ClientState.BEFORE_MOVE

    # The server will send notification messages upon special events occuring 
    elif data["type"] == "notification":
        if data["content"] == "opponent left":
            # Assign to a new opponent if your current opponent has left or has been defeated. This gives players a chance to choose a new attack
            print("Your opponent has left the game. You have been assigned to a new opponent!")
            if data["state"] == GameState.TURN_START:
                STATE["client_state"] = ClientState.NEW_OPPONENT
            else: 
                # If the turn has already finished, clear the previous targets but do not give the player another opportunity to attack
                STATE["previous_targets"].clear()
        elif data["content"] == "you lose":
            print("Your ship has been hit! Please observe until the next game.")
            STATE["client_state"] = ClientState.OBSERVER
        elif data["content"] == "you win":
            print("Congratulations! You are the sole surviver. You win!")

def update():
    # Main client game logic
    if STATE["client_state"] == ClientState.LOBBY_UNREADY:
        print("Welcome to the BattleDot lobby. Type 'R' and press 'Enter' when you are ready to play!")
        val = input()
        if (val == "R" or val == "r"): 
            STATE["client_state"] = ClientState.LOBBY_READY
            print("You are now ready to play!")
            asyncio.run(helpers.send(STATE["websocket"], json.dumps({"type": "action", "action": "ready"})))
        else:
            pass
    elif STATE["client_state"] == ClientState.NEW_OPPONENT:
        STATE["previous_targets"].clear()
        STATE["client_state"] = ClientState.BEFORE_MOVE
    elif STATE["client_state"] == ClientState.BEFORE_MOVE:
        target = str(AXIS_NUMBERS[random.randint(0, 9)]) + AXIS_LETTERS[random.randint(0, 9)]
        while target in STATE["previous_targets"]:
            # Ensure that the player does not attack the same position more than once for the same opponent
            target = str(AXIS_NUMBERS[random.randint(0, 9)]) + AXIS_LETTERS[random.randint(0, 9)]
        asyncio.run(helpers.send(STATE["websocket"], json.dumps({"type": "action", "action": "attack", "target": target })))
        print(f"You chose to attack {target}!")
        STATE["client_state"] = ClientState.AFTER_MOVE
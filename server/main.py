import asyncio, websockets, sys, time, json, os
import helpers, game
from logger import connection_logger

from dotenv import load_dotenv
load_dotenv()

from constants import GameState, STATE, USERS, UPDATE_DELAY_DELTA

import threading

# Handler for client connections
async def connection_handler(websocket,  path):
    connection_logger.info(f"Client connected from remote port {str(websocket.remote_address[1])}")
    print(websocket.local_address)
    await helpers.register(websocket, USERS)
    # Send the current game state to the connecting client so they can adjust their client state accordingly
    await websocket.send(json.dumps({"type": "game_state", "state": STATE["game_state"]}))
    while True:
        try:
            # the websockets package automatically pings the client to determine connection status, so there is no need to implement it here. 
            message = await websocket.recv()
            data = json.loads(message)
            # if the message received is a user action, notify the game
            if data["type"] == "action":
                connection_logger.debug(f"'{data['action']}' action was received from client with remote port {str(websocket.remote_address[1])}, now calling the user_action function.")
                game.user_action(data, websocket)
        except websockets.ConnectionClosed:
            connection_logger.info(f"Client from remote port {str(websocket.remote_address[1])} has closed their connection")
            await helpers.unregister(websocket, USERS)
            break

# Start the websocket server
start_server = websockets.serve(connection_handler, "localhost", os.environ.get("PORT"))
asyncio.get_event_loop().run_until_complete(start_server)

# Continuously run the websocket server on a daemon thread
t1 = threading.Thread(target = asyncio.get_event_loop().run_forever)
t1.daemon = True
t1.start()
connection_logger.info(f"Server is running on port {os.environ.get('PORT')}")

# Start the game's update loop
while True:
    try:
        # Add a predetermined delay between each update
        time.sleep(UPDATE_DELAY_DELTA)
        game.update()
    except KeyboardInterrupt:
        quit()
    except websockets.ConnectionClosed:
        # Ignore connection closed exceptions as disconnected clients will be removed by the connection_handler
        pass
    except:
        connection_logger.error(f"Unexpected error: {sys.exc_info[0]}")
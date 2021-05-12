import asyncio, websockets, json, time, threading, sys
from constants import STATE, UPDATE_DELAY_DELTA
from dotenv import load_dotenv
load_dotenv()
import os
import game

def game_loop():
    while True:
        try:
            # Place a simple limit on the update rate
            time.sleep(UPDATE_DELAY_DELTA)
            game.update()
        except KeyboardInterrupt:
            quit()
        except websockets.ConnectionClosed:
            # Ignore connection closed exceptions as this is handled by the websocket client
            pass
        except:
            print("Unexpected Error:", sys.exc_info[0])

# Run the client game loop on a daemon thread
t1 = threading.Thread(target = game_loop)
t1.daemon = True
t1.start()
print("Game loop running.")

async def client():
    uri = os.environ.get("URL")
    async with websockets.connect(uri) as websocket:
        STATE["websocket"] = websocket
        while True:
            try:
                # The websockets package automatically pings the server to maintain connection status, so there is no need to implement it here. 
                
                # Parse any messages received and notifies the game
                message = await websocket.recv()
                data = json.loads(message)
                game.server_data(websocket, data)
            except websockets.ConnectionClosed:
                print("Disconnected from server")
                break

# Run the websocket client on the main thread
asyncio.get_event_loop().run_until_complete(client())
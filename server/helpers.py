import json, asyncio, websockets, sys
import game
from logger import connection_logger


async def register(websocket, set):
    set.add(websocket)

async def unregister(websocket, set):
    game.user_action( {"action": "exit"} , websocket)
    set.remove(websocket)

async def send(client, data):
    await client.send(data)

def message_all(users, data):
    clients_copy = users.copy()
    for client in clients_copy:
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(send(client, json.dumps(data)))
        except websockets.ConnectionClosed:
            connection_logger.info(f"Could not deliver message to client from remote port {str(client.remote_address[1])} due to closed connection")
        except:
            connection_logger.error(f"Unexpected Error: {sys.exc_info[0]}")
            
def get_websocket_from_remote_port(port, set):
    for websocket in set:
        if websocket.remote_address[1] == port:
            return websocket
import asyncio
import websockets

from dotenv import load_dotenv
load_dotenv()
import os

async def hello(websocket, path):
    name = await websocket.recv()
    print(f"< {name}")

    greeting = f"Hello {name}!"

    await websocket.send(greeting)
    print(f"> {greeting}")

start_server = websockets.serve(hello, "localhost", os.environ.get("PORT"))

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
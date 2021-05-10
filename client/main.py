import asyncio
import websockets

from dotenv import load_dotenv
load_dotenv()
import os

async def hello():
    uri = os.environ.get("URI")
    async with websockets.connect(uri) as websocket:
        name = input("What's your name? ")

        await websocket.send(name)
        print(f"> {name}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(hello())
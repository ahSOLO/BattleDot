async def send(server, data):
    await server.send(data)

def nested_callback(func1, func2):
    return func1(func2())
#!/usr/bin/env python

import asyncio

from websockets.server import serve
from lib.sia import Sia

from handlers.translate import request_handler as translate
from handlers.gen import request_handler as gen

# Ignore all warnings


def makeError(uuid, code):
    return Sia().add_byte_array8(uuid).add_uint64(code).add_byte_array32([]).content


async def handle_ai(uuid, method, sia):
    if method == "Unchained.AI.TextToImage":
        return gen(uuid, sia)
    elif method == "Unchained.AI.Translate":
        return translate(uuid, sia)
    else:
        raise Exception({"reason": "Invalid opcode", "code": 404})


async def ai(websocket):
    async for message in websocket:
        sia = Sia().set_content(message)

        uuid = sia.read_byte_array8()
        signature = sia.read_byte_array8()
        txHash = sia.read_string8()
        method = sia.read_string8()

        try:
            response = await handle_ai(uuid, method, sia)
        except Exception as e:
            if isinstance(e.args[0], dict) and "code" in e.args[0] and isinstance(e.args[0]["code"], int):
                response = makeError(uuid, e.args[0]["code"])
            else:
                response = makeError(uuid, 500)

        await websocket.send(response)


async def main(port=8765):
    print(f"Server started on ws://localhost:{port}")
    async with serve(ai, "0.0.0.0", port):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())

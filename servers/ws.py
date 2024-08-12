#!/usr/bin/env python

import asyncio
import warnings

from websockets.server import serve
from ..handlers.translate import translate
from ..lib.sia import Sia
from ..handlers.gen import gen

# Ignore all warnings
warnings.filterwarnings("ignore")


def makeError(uuid, code):
    return Sia().add_byte_array_n(uuid).add_uint64(code).content


async def handle_ai(uuid, opcode, sia):
    if opcode == 0:
        return gen.request_handler(uuid, sia)
    elif opcode == 1:
        return translate.request_handler(uuid, sia)
    else:
        raise Exception({"reason": "Invalid opcode", "code": 404})


async def ai(websocket):
    async for message in websocket:
        sia = Sia().set_content(bytearray(message))
        opcode = sia.read_uint16()
        uuid = sia.read_byte_array_n(16)

        try:
            response = await handle_ai(uuid, opcode, sia)
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

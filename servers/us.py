#!/usr/bin/env python

import asyncio
import warnings
import socket
import os

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


async def ai(reader, writer):
    peername = writer.get_extra_info('peername')
    print(f"Connection from {peername}")

    try:
        data = bytearray()
        while True:
            chunk = await reader.read(100)
            if not chunk:
                break
            data.extend(chunk)

        sia = Sia().set_content(data)
        opcode = sia.read_uint16()
        uuid = sia.read_byte_array_n(16)

        try:
            response = await handle_ai(uuid, opcode, sia)

        except Exception as e:
            if isinstance(e.args[0], dict) and "code" in e.args[0] and isinstance(e.args[0]["code"], int):
                response = makeError(uuid, e.args[0]["code"])
            else:
                response = makeError(uuid, 500)

        writer.write(response)
        await writer.drain()

    except asyncio.CancelledError:
        print(f"Connection to {peername} cancelled")

    finally:
        print(f"Closing connection to {peername}")
        writer.close()
        await writer.wait_closed()


async def main(socket_file="/tmp/unchained_ai.sock"):
    # Ensure the socket file does not already exist
    if os.path.exists(socket_file):
        os.remove(socket_file)

    server = await asyncio.start_unix_server(ai, path=socket_file)
    print(f"Unix socket server is running on {socket_file}")

    async with server:
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())

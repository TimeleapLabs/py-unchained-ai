#!/usr/bin/env python

import asyncio
import os

from lib.sia import Sia

from handlers.translate import request_handler as translate
from handlers.gen import request_handler as gen


def makeError(uuid, code):
    return Sia().add_byte_array8(uuid).add_uint64(code).add_byte_array32([]).content


async def handle_ai(uuid, method, sia):
    if method == "Unchained.AI.TextToImage":
        return gen(uuid, sia)
    elif method == "Unchained.AI.Translate":
        return translate(uuid, sia)
    else:
        raise Exception({"reason": "Invalid opcode", "code": 404})


async def ai(reader, writer):
    peername = writer.get_extra_info('peername')
    print(f"Connection from {peername}")

    try:
        while True:
            data = bytearray()
            size = 0
            while True:
                chunk = await reader.read(size == 0 and 100 or size)
                if not chunk:
                    break

                data.extend(chunk)

                if size == 0 and len(data) >= 4:
                    size = int.from_bytes(data[:4], byteorder="little")
                    print(f"Expecting {size} bytes")

                if size > 0 and len(data) >= size + 4:
                    break

            print(f"Received {len(data)} bytes from {peername}")

            sia = Sia().set_content(data[4:])

            uuid = sia.read_byte_array8()
            signature_ = sia.read_byte_array8()
            txHash_ = sia.read_string8()
            method = sia.read_string8()

            try:
                response = await handle_ai(uuid, method, sia)

            except Exception as e:
                print(f"Error: {e}")

                if isinstance(e.args[0], dict) and "code" in e.args[0] and isinstance(e.args[0]["code"], int):
                    response = makeError(uuid, e.args[0]["code"])
                else:
                    response = makeError(uuid, 500)

            payload = bytearray()
            payload.extend(len(response).to_bytes(4, byteorder="little"))
            payload.extend(response)

            print(f"Sending {len(payload)} bytes to {peername}")

            writer.write(payload)
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

    print("Server stopped")


if __name__ == "__main__":
    asyncio.run(main())

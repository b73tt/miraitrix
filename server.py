#!/usr/bin/env python3

import asyncio
from websockets.server import serve


async def telnettarpit(reader, writer):
    global queue, conncount
    conncount += 1
    print("new connection: " + str(conncount) + " in total")
	
    ip=writer.get_extra_info('peername')[0]
    try:
        while True:
            writer.write(b'\xff\xfd\x01')
            data = await reader.read(100)
            if data:
                queue.put_nowait((ip, data))
            writer.write(b'login: ')
            data = await reader.read(100)
            if data:
                queue.put_nowait((ip, data))
            await asyncio.sleep(3)
            writer.write(b'password: ')
            data = await reader.read(100)
            if data:
                queue.put_nowait((ip, data))
            await asyncio.sleep(5)
            await writer.drain()
    except Exception as e:
        conncount -= 1


async def echo(websocket):
	while True:
		try:
			(ip,data) = await asyncio.wait_for(queue.get(), timeout=2)
			await websocket.send(data)
		except asyncio.exceptions.TimeoutError:
			pass

async def main():
	global queue, conncount
	conncount = 0
	queue = asyncio.Queue()
	
	tarpitserver = await asyncio.start_server(telnettarpit, '0.0.0.0', 2323)
	async with serve(echo, "0.0.0.0", 8765):
		await asyncio.Future()  # run forever

asyncio.run(main())
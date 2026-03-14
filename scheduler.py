import asyncio


async def schedule(interval, coro, *args):

    while True:

        await coro(*args)

        await asyncio.sleep(interval)

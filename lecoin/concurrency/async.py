import asyncio
import time


async def greet(name, delay):
    await asyncio.sleep(delay)
    print(f'{name}: I wated {delay} seconds before saying "hello"')


async def main():
    task_1 = asyncio.create_task(greet("t1", 3))
    task_2 = asyncio.create_task(greet("t2", 2))
    task_3 = asyncio.create_task(greet("t3", 2))

    start_time = time.time()

    print("0.00s: Program start")

    await task_1
    await task_2
    await task_3

    print(f"{time.time() - start_time:.2f}s: Program end")


asyncio.run(main())

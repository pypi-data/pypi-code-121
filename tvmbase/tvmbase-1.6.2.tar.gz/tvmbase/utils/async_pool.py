import asyncio
from typing import Coroutine


async def async_pool(limit: int, tasks: list[Coroutine]) -> tuple:
    semaphore = asyncio.Semaphore(limit)

    async def semaphore_task(task: Coroutine):
        async with semaphore:
            return await task

    return await asyncio.gather(*(
        semaphore_task(task)
        for task in tasks
    ))

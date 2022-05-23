from typing import AsyncIterator, Collection, Iterator, TypeVar
import asyncio

T = TypeVar("T")


def iter_over_async(async_iter: AsyncIterator[T]) -> Iterator[T]:
    """Synchronous generator over an asynchronous iterator."""
    while True:
        try:
            # async_iter.__anext__() is an awaitable
            next_val = asyncio.run(async_iter.__anext__())
        except StopAsyncIteration:
            break
        else:
            yield next_val


async def async_iter(data_list: Collection[T]) -> AsyncIterator[T]:
    """Convert a collection into an AsyncIterator."""
    for data in data_list:
        yield data


async def decoupled_async_iter(
    source: AsyncIterator[T], buffer_size: int = 1
) -> AsyncIterator[T]:
    """Create a consumer/producer pattern using an asyncio.Queue."""
    queue: asyncio.Queue = asyncio.Queue(maxsize=buffer_size)

    async def producer() -> None:
        async for x in source:
            await queue.put(x)
        await queue.put(None)  # producer finished

    # Launch the iteration of source iterator
    loop = asyncio.get_running_loop()
    loop.create_task(producer())

    while True:
        x = await queue.get()
        if x is None:
            queue.task_done()
            break
        queue.task_done()
        yield x

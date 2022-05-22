import asyncio
import queue
from math import log10
from typing import Union, AsyncIterable, Optional, TypeVar, Iterable, Callable

from .log import logger


async def iterate_queue(q: asyncio.Queue, poll_interval_s: Optional[float] = None, sentry=None) -> AsyncIterable:
    """Iterates over the elements of the queue, waiting for next elements if necessary, until 'sentry' is
       retrieved. If poll_interval_s is not None, also yields a None periodically."""
    while True:
        try:
            item = await asyncio.wait_for(q.get(), poll_interval_s)
        except asyncio.TimeoutError:
            yield None
            continue
        if item is sentry:
            q.task_done()
            return
        yield item
        q.task_done()


def flush_queue(q: Union[asyncio.Queue, queue.Queue]) -> int:
    n = 0
    while not q.empty():
        q.get_nowait()
        q.task_done()
        n += 1
    return n


async def iterate_stream(stream: asyncio.StreamReader, chunk_size: int, timeout: Optional[float] = None) \
        -> AsyncIterable:
    while True:
        try:
            data = await asyncio.wait_for(stream.readexactly(chunk_size), timeout)
        except asyncio.IncompleteReadError:
            data = None
        except ConnectionResetError:
            logger.warning("Connection reset")
            data = None
        if not data:
            return
        yield data


def my_assert(condition: bool, message: str):
    if not condition:
        logger.error(message)
        raise RuntimeError(message)


def to_db(gain) -> float:
    return 20 * log10(float(gain))


def to_gain(db) -> float:
    return 10 ** (float(db) / 20)


def remove_non_ascii(s) -> str:
    return str(s).encode('ascii', errors='replace').decode()


Item = TypeVar("Item")


def find_first(iterable: Iterable[Item], condition: Callable[[Item], bool], default: Optional[Item] = None) -> Item:
    for item in iterable:
        if condition(item):
            return item
    if default is None:
        raise IndexError("no item found")
    return default

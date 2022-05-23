import asyncio
import inspect
from contextlib import asynccontextmanager
from functools import wraps
from pathlib import Path
from typing import Any, Callable, cast

import portalocker
from colorama.ansi import Fore

import beni
import beni.color as bprint


@asynccontextmanager
async def key(*keys: str, timeout: float = 0, quite: bool = False):
    lock_list: list[portalocker.Lock] = []
    keyfile_list: list[Path] = []
    for key in keys:
        lock, keyfile = _lock_acquire(key, timeout, quite)
        lock_list.append(lock)
        keyfile_list.append(keyfile)
    try:
        yield
    finally:
        for lock in lock_list:
            lock.release()
        for keyfile in keyfile_list:
            try:
                beni.remove(keyfile)
            except:
                pass


# @asynccontextmanager
# async def async_key(*keys: str, timeout: float = 0, quite: bool = False):
#     with key(*keys, timeout=timeout, quite=quite):
#         yield


# def w_key(*keys: str, timeout: float = 0, quite: bool = False):
#     def wraperfun(func: beni.Fun) -> beni.Fun:
#         @wraps(func)
#         def wraper(*args: Any, **kwargs: Any):
#             with key(*keys, timeout=timeout, quite=quite):
#                 return func(*args, **kwargs)
#         return cast(Any, wraper)
#     return wraperfun


# def wa_key(*keys: str, timeout: float = 0, quite: bool = False):
#     def wraperfun(func: beni.AsyncFun) -> beni.AsyncFun:
#         @wraps(func)
#         async def wraper(*args: Any, **kwargs: Any):
#             async with async_key(*keys, timeout=timeout, quite=quite):
#                 return await func(*args, **kwargs)
#         return cast(Any, wraper)
#     return wraperfun


class _Limit():

    _queue: asyncio.Queue[Any]
    _running: int

    def __init__(self, limit: int):
        self._limit = limit
        self._queue = asyncio.Queue()
        self._running = 0
        while self._queue.qsize() < self._limit:
            self._queue.put_nowait(True)

    async def wait(self):
        await self._queue.get()
        self._running += 1

    async def release(self):
        if self._queue.qsize() < self._limit:
            await self._queue.put(True)
        self._running -= 1

    async def set_limit(self, limit: int):
        self._limit = limit
        while self._running + self._queue.qsize() < self._limit:
            await self._queue.put(True)
        while self._running + self._queue.qsize() > self._limit:
            if self._queue.empty():
                break
            await self._queue.get()


async def setLimit(func: Callable, limit: int):
    funid = id(inspect.unwrap(func))
    if funid not in _limit_dict:
        _limit_dict[funid] = _Limit(limit)
    await _limit_dict[funid].set_limit(limit)

_limit_dict: dict[int, _Limit] = {}


def limit(limit: int = 1):
    def wraperfun(func: beni.AsyncFun) -> beni.AsyncFun:
        @wraps(func)
        async def wraper(*args: Any, **kwargs: Any):
            funid = id(inspect.unwrap(func))
            if funid not in _limit_dict:
                _limit_dict[funid] = _Limit(limit)
            try:
                await _limit_dict[funid].wait()
                return await func(*args, **kwargs)
            finally:
                await _limit_dict[funid].release()
        return cast(Any, wraper)
    return wraperfun


def _lock_acquire(key: str, timeout: float = 0, quite: bool = False):
    '''不对外部提供，只提供给 async_keylock 方法使用'''
    keyfile = beni.getPathWorkspace(f'.lock/{beni.crcStr(key)}.lock')
    beni.makeDir(keyfile.parent)
    while True:
        try:
            lock = portalocker.Lock(keyfile, timeout=timeout, fail_when_locked=timeout == 0)
            f = lock.acquire()
            f.write(key)
            f.flush()
            break
        except:
            if quite:
                raise Exception(f'资源被锁定无法继续操作 key={key} keyfile={keyfile}')
            else:
                bprint.printx(f'资源被锁定无法继续操作 key={key} keyfile={keyfile}', colorList=[Fore.LIGHTRED_EX])
                inputvalue = beni.hold(f'重试（retry）或退出（exit）', False, 'retry', 'exit')
                match inputvalue:
                    case 'retry':
                        print('正在重试...')
                    case 'exit':
                        raise Exception(f'资源被锁定无法继续操作 - {key}')
                    case _:
                        pass
    return lock, keyfile

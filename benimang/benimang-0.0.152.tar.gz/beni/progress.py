
import asyncio
from contextlib import asynccontextmanager
from typing import Any, Coroutine, Sequence, TypeVar

from tqdm import tqdm

import beni.lock as block


@asynccontextmanager
async def show(total: int):
    print()
    with tqdm(total=total, ncols=70) as progress:
        yield progress.update
    print()

_ReturnType = TypeVar('_ReturnType')


async def run(
    taskList: Sequence[Coroutine[Any, Any, _ReturnType]],
    itemLimit: int = 999999,
) -> Sequence[_ReturnType]:
    print()
    with tqdm(total=len(taskList), ncols=70) as progress:
        @block.limit(itemLimit)
        async def task(x: Coroutine[Any, Any, _ReturnType]):
            result = await x
            progress.update()
            return result
        resultList = await asyncio.gather(*[task(x) for x in taskList])
    print()
    return resultList

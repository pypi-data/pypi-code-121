import asyncio
import functools
from typing import (
    Any,
    Callable,
    Coroutine,
    Generator,
    Generic,
    Optional,
    ParamSpec,
    TypeVar,
    Union,
)

from .base import GenericBaseRepository, _Create, _Id, _Item, _Replace, _Update

_Params = ParamSpec("_Params")
_FuncOut = TypeVar("_FuncOut")


def _task(
    func: Callable[
        _Params, Union[Generator[Any, None, _FuncOut], Coroutine[Any, Any, _FuncOut]]
    ]
):
    @functools.wraps(func)
    def decorated(
        *args: _Params.args, **kwargs: _Params.kwargs
    ) -> asyncio.Task[_FuncOut]:
        return asyncio.create_task(func(*args, **kwargs))

    return decorated


class CacheRepository(
    GenericBaseRepository[_Id, _Create, _Update, _Replace, _Item],
    Generic[_Id, _Create, _Update, _Replace, _Item],
):
    """A cached repository implementation.

    This implements caching for an underlying repository, provided in the constructor.

    For simplisity, the implementation relies in the functool's caching functionality.

    Note that modify operations are not cached and clear the caches.
    """

    def __init__(
        self, repository: GenericBaseRepository[_Id, _Create, _Update, _Replace, _Item]
    ) -> None:
        super().__init__()
        self.repository = repository

    def clear_cache(self):
        self.get_list.cache_clear()
        self.get_count.cache_clear()
        self.get_by_id.cache_clear()

    @functools.cache
    @_task
    async def get_list(
        self,
        *,
        offset: Optional[int] = None,
        size: Optional[int] = None,
        **query_filters: Any
    ) -> list[_Item]:
        return await self.repository.get_list(offset=offset, size=size, **query_filters)

    @functools.cache
    @_task
    async def get_count(self, **query_filters: Any) -> int:
        return await self.repository.get_count()

    @functools.cache
    @_task
    async def get_by_id(self, id: _Id) -> _Item:
        return await self.repository.get_by_id(id)

    async def update(self, id: _Id, payload: _Update, **kwargs: Any) -> _Item:
        result = await self.repository.update(id, payload, **kwargs)
        self.clear_cache()
        return result

    async def replace(self, id: _Id, payload: _Replace, **kwargs: Any) -> _Item:
        result = await self.repository.replace(id, payload, **kwargs)
        self.clear_cache()
        await self.get_by_id(id)
        return result

    async def remove(self, id: _Id, **kwargs: Any):
        await self.repository.remove(id, **kwargs)
        self.clear_cache()

import asyncio
from collections import defaultdict
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, Generic, OrderedDict, TypeVar

from typing_extensions import ParamSpec

P = ParamSpec("P")
T = TypeVar("T")


class LRUCache(Generic[T]):
    def __init__(self, max_size: int = 1024) -> None:
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        self._cache: OrderedDict[int, T] = OrderedDict()

    def __getitem__(self, key: int) -> T:
        try:
            value = self._cache[key]
            self._cache.move_to_end(key)
            self.hits += 1
            return value

        except:
            self.misses += 1
            raise

    def __setitem__(self, key: int, value: T) -> None:
        self._cache[key] = value
        self._cache.move_to_end(key)
        if len(self) > self.max_size:
            self._cache.popitem(False)

    def __len__(self) -> int:
        return len(self._cache)


def cache(function: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    """Decorate function to cache return values.

    Implements a LRU cache with a default cache size of 1024 recent calls per function
    (approximately 1 MB per resource). We acquire a mutex lock while accessing the
    cache or awaiting the wrapped callable to optimize for cache hits and prevent
    redundant executions.
    """
    _cache: LRUCache[T] = LRUCache()
    _locks: Dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)

    @wraps(function)
    async def cached_function(*args: Any, **kwargs: Any) -> T:
        cache_key = hash(repr(args) + repr(sorted(kwargs.items())))
        lock = _locks[cache_key]

        async with lock:
            try:
                result = _cache[cache_key]
            except KeyError:
                result = await function(*args, **kwargs)
                _cache[cache_key] = result

        return result

    # pylint: disable=protected-access
    cached_function._cache = _cache  # type: ignore
    return cached_function

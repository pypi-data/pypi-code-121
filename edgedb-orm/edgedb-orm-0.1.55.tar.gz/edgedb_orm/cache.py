import typing as T
import time
import orjson
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder


class Cache(BaseModel):
    val: T.Any
    resolver: T.Any  # circular unfortunately
    timestamp: float
    raw_d_bytes: bytes


class CacheManager(BaseModel):
    cache: T.Dict[str, Cache] = {}

    def remove(self, key: str) -> None:
        if key in self.cache:
            del self.cache[key]

    def add(self, *, key: str, resolver, val: T.Any, raw_d: dict) -> None:
        self.cache[key] = Cache(
            val=val,
            resolver=resolver,
            timestamp=time.time(),
            raw_d_bytes=orjson.dumps(jsonable_encoder(raw_d)),
        )

    def replace(self, key: str, cache: Cache) -> None:
        self.cache[key] = cache

    def get(self, key: str) -> T.Optional[Cache]:
        if key not in self.cache:
            return None
        return self.cache[key]

    def exists(self, key: str) -> bool:
        return key in self.cache

    def get_val(self, key: str) -> T.Optional[T.Union["NodeType", T.List["NodeType"]]]:
        if c := self.cache[key]:
            return c.val

    def clear(self) -> None:
        self.cache = {}

    def is_empty(self) -> bool:
        return len(self.cache) == 0

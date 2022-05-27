#!/usr/bin/env python3

# standards
from datetime import timedelta
from pathlib import Path
from typing import Optional, Union

# 3rd parties
from requests import PreparedRequest, Response
from requests.cookies import MockRequest

# hublot
from ..logs import LogEntry
from ..utils import MockResponse
from .key import CacheKey, UserSpecifiedCacheKey
from .storage import DiskStorage, Storage


class Cache:

    def __init__(self, storage: Storage, max_age: Optional[timedelta] = None):
        self.storage = storage
        self.max_age = max_age
        self.needs_pruned = (max_age is not None)

    def get(
        self,
        preq: PreparedRequest,
        log: LogEntry,
        key: Optional[UserSpecifiedCacheKey] = None,
        max_age: Optional[timedelta] = None,
    ) -> Optional[Response]:
        """
        Looks up the given `PreparedRequest`, and returns the corresponding `Response` if it was in cache, or `None` otherwise.
        """
        key = CacheKey.parse(key) if key else CacheKey.compute(preq)
        if self.needs_pruned and self.max_age is not None:
            self.storage.prune(self.max_age)
            self.needs_pruned = False
        if max_age is None or (self.max_age is not None and max_age > self.max_age):
            # The `max_age` passed to the method can't be greater than that given to the constructor, that would be inconsistent
            # with the cache pruning that happens and which is always based on the constructor-given `self.max_age`
            max_age = self.max_age
        res = self.storage.read(key, max_age)
        if res is not None:
            res.request = preq  # the storage doesn't need to store and recreate the request
            res.cookies.extract_cookies(MockResponse(res), MockRequest(preq))  # type: ignore[arg-type]
            log.cached = True
        else:
            res = None
            log.cached = False
        log.cache_key_str = key.unique_str
        return res

    def put(
        self,
        preq: PreparedRequest,
        log: LogEntry,
        res: Response,
        key: Optional[UserSpecifiedCacheKey] = None,
    ) -> None:
        key = CacheKey.parse(key) if key else CacheKey.compute(preq)
        log.cache_key_str = key.unique_str
        self.storage.write(key, res)

    @classmethod
    def load(
        cls,
        cache: Union['Cache', Path, str, None] = None,
        max_age: Optional[timedelta] = None,
    ) -> Optional['Cache']:
        """
        Takes the `cache` param given to the `Client` constructor, and returns a `Cache` instance, or `None`
        """
        if cache is None or isinstance(cache, Cache):
            if max_age is not None:
                raise Exception("You can't specify a max_age if passing in an already instantiated `Cache`")
            return cache
        elif isinstance(cache, Path):
            return cls(
                storage=DiskStorage(root_path=cache),
                max_age=max_age,
            )
        elif isinstance(cache, str) and cache.startswith('s3://'):  # pragma: no cover
            raise NotImplementedError  # some day
        else:
            raise ValueError(repr(cache))

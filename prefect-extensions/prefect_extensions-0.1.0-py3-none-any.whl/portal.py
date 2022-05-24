import datetime
import asyncio
import gc
from threading import Lock
from queue import Queue
from memory_profiler import profile
from pydantic import BaseModel, Field
from typing import ClassVar, List, TypeVar, Generic, Optional, Dict


class PortalClosedException(Exception):
    def __init__(self, message: Optional[str] = None):
        message = message or "Portal has already been marked as closed."
        super().__init__(message)


class PortalPayload(BaseModel):
    pass


P = TypeVar("P", bound=PortalPayload)


class PortalCache(Queue, Generic[P]):
    def __init__(self, maxsize: Optional[int] = 0):
        super().__init__(maxsize=maxsize)
        self.updated = None
        self.lock = Lock()
        self.reading = 0
        self.writing = 0
        self.closed = False

    def __has_writing__(self):
        with self.lock:
            return self.writing > 0

    def __num_reading__(self):
        with self.lock:
            return self.reading

    def finalize(self):
        with self.lock:
            self.closed = True
        for _ in range(2):
            while self.__has_writing__():
                try:
                    t = super().get(block=False)
                    print(t)
                    del t
                except Exception:
                    pass
            last_reading = self.__num_reading__() + 1
            while self.__num_reading__() > 0:
                while self.__num_reading__() == last_reading:
                    asyncio.sleep(0.1)
                try:
                    super().put(
                        item=None,
                        block=False,
                    )
                except Exception:
                    pass
        try:
            while True:
                t = super().get(block=False)
                del t
        except Exception:
            pass
        gc.collect()

    def put(self, item: P, block: bool = True, timeout: Optional[float] = None) -> None:
        with self.lock:
            if self.closed:
                raise PortalClosedException()
            self.writing += 1
        try:
            super().put(item, block=block, timeout=timeout)
            self.updated = datetime.datetime.now()
        finally:
            with self.lock:
                self.writing -= 1

    def get(self, block: bool = True, timeout: Optional[float] = None) -> P:
        with self.lock:
            if self.closed:
                raise PortalClosedException()
            self.reading += 1
        try:
            payload = super().get(block=block, timeout=timeout)
            self.updated = datetime.datetime.now()
            if payload is None:
                raise PortalClosedException()
            return payload
        finally:
            with self.lock:
                self.reading -= 1


class Portal(BaseModel, Generic[P]):
    _cache: ClassVar[Dict[str, PortalCache[P]]] = {}
    _lock: ClassVar[Lock] = Lock()
    _closed: ClassVar[List[str]] = []

    @classmethod
    def __get_cache__(cls, signature: str) -> PortalCache[P]:
        with cls._lock:
            if signature in cls._closed:
                raise PortalClosedException()
            if signature not in cls._cache:
                cls._cache[signature] = PortalCache()
            cache = cls._cache[signature]
        return cache

    @classmethod
    def __finalize__(cls, signature: str) -> None:
        with cls._lock:
            if signature not in cls._cache:
                cls._closed.append(signature)
                return
            cache = cls._cache[signature]
            cache.finalize()
            del cache
            del cls._cache[signature]
            cls._closed.append(signature)
            gc.collect()

    @classmethod
    def __remove_expired__(cls, timedelta: datetime.timedelta) -> None:
        to_remove = []
        with cls._lock:
            for key, cache in cls._cache.items():
                if cache.updated < datetime.datetime.now() - timedelta:
                    to_remove.append(key)
        for key in to_remove:
            cls.__finalize__(key)

    def close(self):
        self.__class__.__finalize__(self.__str__())

    def put(
        self, payload: P, block: bool = True, timeout: Optional[float] = None
    ) -> None:
        self.__class__.__get_cache__(self.__str__()).put(
            item=payload,
            block=block,
            timeout=timeout,
        )

    def get(self, block: bool = True, timeout: Optional[float] = None) -> P:
        return self.__class__.__get_cache__(self.__str__()).get(
            block=block,
            timeout=timeout,
        )

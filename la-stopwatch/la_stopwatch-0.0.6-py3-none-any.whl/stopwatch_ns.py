from asyncio import iscoroutinefunction
from copy import deepcopy
from time import time_ns
from typing import Awaitable, Callable

from la_stopwatch.abstraction import StopwatchABS


class StopwatchNS(StopwatchABS):
    def __init__(
        self, callback: Callable[[int], None | Awaitable] = ..., *args, **kwargs
    ):
        self._records: dict[int | str, int] = {}
        self._nameless_records: int = 0

        self._callback = callback
        self._args = args
        self._kwargs = kwargs

        self.reset()

    def __enter__(self):
        return self.reset()

    def __exit__(self, type, value, traceback) -> bool:
        if self._kwargs:
            self._kwargs |= {"duration": self.duration()}
        else:
            self._args = self._args + (self.duration(), )
        
        if callable(self._callback):
            self._callback(*self._args, **self._kwargs)

        return False

    def __call__(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            self._args = args + self._args
            self._kwargs = kwargs | self._kwargs
            
            with self:
                return func(*args, **kwargs)

        async def awrapper(*args, **kwargs):
            self._args = args + self._args
            self._kwargs = kwargs | self._kwargs

            async with self:
                return await func(*args, **kwargs)

        if iscoroutinefunction(func):
            return awrapper
        return wrapper

    async def __aenter__(self):
        return self.reset()

    async def __aexit__(self, type, value, traceback) -> bool:
        if self._kwargs:
            self._kwargs |= {"duration": self.duration()}
        else:
            self._args = self._args + (self.duration(), )

        if callable(self._callback) and iscoroutinefunction(self._callback):
            await self._callback(*self._args, **self._kwargs)
        elif callable(self._callback):
            self._callback(*self._args, **self._kwargs)

        return False

    def __str__(self) -> str:
        return str(self.duration())

    def __repr__(self) -> str:
        return str(self.duration())

    def reset(self):
        self._start = time_ns()
        return self

    def duration(self) -> int:
        return time_ns() - self._start

    def get_record(self, name: int | str) -> int | None:
        return self._records.get(name)

    def get_records(self) -> dict[int | str, int]:
        return deepcopy(self._records)

    def record(self, name: str = ...):
        if not isinstance(name, str):
            name = self._nameless_records
            self._nameless_records += 1

        self._records[name] = self.duration()

        return self

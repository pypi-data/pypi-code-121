# -*- coding: utf-8 -*-

import weakref
from typing import Iterator, Callable

from .config import Config

FilterFunction = Callable[[Config], bool]


class Filter:
    """Matrix filter"""
    _instances = set()

    def __init__(self, fn: FilterFunction):
        self._fn = fn
        self._instances.add(weakref.ref(self))

    def __del__(self):
        self._instances.discard(weakref.ref(self))

    def __call__(self, config: Config) -> bool:
        return self._fn(config)

    @classmethod
    def get_instances(cls) -> Iterator[Callable[[Config], bool]]:
        """Retrieve all instances"""
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

    @classmethod
    def match(cls, config: Config) -> bool:
        """Matcher"""
        return any(f(config) for f in cls.get_instances())

from __future__ import annotations

import time
import typing as ty


class Timer:
    def __init__(self, parent: Stopwatch, name: str):
        self._parent = parent
        self._name = name
        self._entered: float = 0

    def __enter__(self):
        self._entered = time.monotonic()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        d = time.monotonic() - self._entered
        self._parent[self._name] = d


class Stopwatch:
    def __init__(self):
        self._started: float = time.monotonic()
        self._times: ty.Dict[str, float] = {}

    @property
    def times(self):
        return {**self._times, 'total': time.monotonic() - self._started}

    def __getitem__(self, item):
        return Timer(self, item)

    def __setitem__(self, name: str, duration: float):
        self._times[name] = duration

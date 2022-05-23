from __future__ import absolute_import

import itertools
from typing import (
    Iterable,
    List,
)


def chunks(list: List, n: int):
    for i in range(0, len(list), n):
        yield list[i:i + n]


def ichunks(iterable: Iterable, n: int):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk

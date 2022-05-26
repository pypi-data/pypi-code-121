from functools import reduce
from typing import Callable, Iterable

from .curry import BoundCurriedFunction, curry


def cmap(fn: Callable) -> Callable:
    return BoundCurriedFunction(map, (fn,))


def cfilter(fn: Callable) -> Callable:
    return BoundCurriedFunction(filter, (fn,))


@curry
def creduce(initial, fn: Callable, seq: Iterable):
    return reduce(fn, seq, initial)

import datetime
from typing import Generator, Generic, TypeVar


EPOCH = datetime.datetime(1970, 1, 1)


def epoch_from_iso(date: str):
    return (
        datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ") - EPOCH
    ).total_seconds()


T = TypeVar("T")
R = TypeVar("R")


class _GeneratorWithReturn(Generic[T, R]):
    def __init__(self, generator: Generator[T, None, R]):
        self.generator = generator

    def __iter__(self):
        self.return_value = yield from self.generator


def collect_from_generator(gen: Generator[T, None, R]):
    _gen = _GeneratorWithReturn(gen)
    yielded: "list[T]" = list(_gen)
    return yielded, _gen.return_value

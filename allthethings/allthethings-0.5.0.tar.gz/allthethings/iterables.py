from itertools import takewhile, islice, repeat
from typing import TypeVar, Dict, List, Iterable, Callable, Iterator

U = TypeVar('U')
R = TypeVar('R')


def grouper(iterable: Iterable[U], n) -> Iterator[List[U]]:
    it = iter(iterable)
    yield from takewhile(bool, ([*islice(it, n)] for _ in repeat(None)))


def groupby(f: Callable[[U], R], xs: Iterable[U]) -> Dict[R, List[U]]:
    r = dict()
    for x in xs:
        k = f(x)
        if k not in r:
            r[k] = []
        r[k].append(x)
    return r


def dedup(xs: Iterable[U], on=lambda x: x) -> Iterator[U]:
    """
    Deduplicates an iterable. Any item is guaranteed to only occur once in the result.
    """

    seen = set()
    for x in xs:
        identity = on(x)
        if identity in seen:
            continue
        seen.add(identity)
        yield x

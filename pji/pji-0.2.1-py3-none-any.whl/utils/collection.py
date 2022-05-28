import collections
from typing import Iterable, TypeVar, Set

_T = TypeVar('_T')


def duplicates(array: Iterable[_T]) -> Set[_T]:
    return {item for item, count in collections.Counter(array).items() if count > 1}

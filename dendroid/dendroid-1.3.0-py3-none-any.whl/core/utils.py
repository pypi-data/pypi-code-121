import weakref
from collections import deque
from itertools import (count,
                       groupby)
from typing import (Any,
                    Iterable,
                    List,
                    Optional,
                    Sequence,
                    Tuple)

from .hints import (Item,
                    Key,
                    Value)


class AntisymmetricKeyIndex:
    __slots__ = 'key', 'index'

    def __init__(self, key_index: Tuple[Key, int]) -> None:
        self.key, self.index = key_index

    def __eq__(self, other: 'AntisymmetricKeyIndex') -> bool:
        return are_keys_equal(self.key, other.key)


def are_keys_equal(left: Key, right: Key) -> bool:
    return not (left < right or right < left)


def capacity(iterable: Iterable[Any]) -> int:
    """
    Returns number of elements in iterable.

    >>> capacity(range(0))
    0
    >>> capacity(range(10))
    10
    """
    counter = count()
    # order matters: if `counter` goes first,
    # then it will be incremented even for empty `iterable`
    deque(zip(iterable, counter),
          maxlen=0)
    return next(counter)


def to_balanced_tree_height(size: int) -> int:
    return size.bit_length() - 1


def dereference_maybe(maybe_reference: Optional[weakref.ref]
                      ) -> Optional[Value]:
    return (maybe_reference
            if maybe_reference is None
            else maybe_reference())


def maybe_weakref(object_: Optional[Value]
                  ) -> Optional[weakref.ReferenceType]:
    return (object_
            if object_ is None
            else weakref.ref(object_))


def to_unique_sorted_items(keys: Sequence[Key], values: Sequence[Value]
                           ) -> Sequence[Tuple[Key, Value]]:
    return [(index_key.key, values[-index_key.index])
            for index_key, _ in groupby(
                sorted([(key, -index) for index, key in enumerate(keys)]),
                key=AntisymmetricKeyIndex)]


def to_unique_sorted_values(values: List[Value]) -> List[Value]:
    values.sort()
    return [value for value, _ in groupby(values)]


def split_items(items: Sequence[Item]) -> Tuple[Sequence[Key],
                                                Sequence[Value]]:
    return tuple(zip(*items)) if items else ((), ())

"""
AIML sets.

This module contains implementation of standard AIML sets as defined
by https://sites.google.com/a/techmaru.com/techmaruhome/technology/aiml-2-1
"""

from typing import Callable, Iterator, Any, Set


_PREDICATE_SET_LENGTH: int = 0
"""Length of a set that based on a _predicate decides if it contains value."""


class _PredicateSet(Set[str]):
    """
    A set-like object based on a characteristic function.

    Set that given a predicate as its characteristic function behave like
    standard python set, except it does not allow iteration (it leads to
    empty sequence).
    """

    def __init__(self, predicate: Callable[[str], bool]):
        super().__init__()
        self._predicate = predicate

    def __contains__(self, x: Any) -> bool:
        return self._predicate(x)

    def __len__(self) -> int:
        return _PREDICATE_SET_LENGTH

    def __iter__(self) -> Iterator[str]:
        raise StopIteration()


def _is_natural_number(x: str):
    return x.isdecimal()


IS_NUMBER: Set[str] = _PredicateSet(_is_natural_number)
"""AIML 2.x set representing natural numbers."""


__all__ = ["IS_NUMBER"]

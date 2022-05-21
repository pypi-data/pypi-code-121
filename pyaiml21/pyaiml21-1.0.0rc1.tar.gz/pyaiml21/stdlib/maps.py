"""
AIML maps.

This module contains implementation of standard AIML maps as defined
by https://sites.google.com/a/techmaru.com/techmaruhome/technology/aiml-2-1
"""

from typing import Callable, Iterator, Dict, TypeVar, overload
import inflect


_inflector = inflect.engine()
"""Static variable we use to create singulars and plurals"""


T = TypeVar("T")
S = TypeVar("S")


PREDICATE_MAP_LENGTH: int = 0
"""Length of a map that maps using a mapping function."""


class _PredicateMap(Dict[T, S]):
    """
    A map-like object based on a mapping function.

    Map that given a function behave like a standard python map, mapping the
    objects using the function.
    """

    def __init__(self, mapper: Callable[[T], S]):
        self.mapper = mapper

    @overload
    def get(self, k):
        ...

    @overload
    def get(self, k, default):
        ...

    def get(self, k, *args):
        try:
            return self.__getitem__(k)
        except Exception:
            if args:
                return args[0]
            return None

    def __getitem__(self, k: T) -> S:
        return self.mapper(k)

    def __len__(self) -> int:
        return PREDICATE_MAP_LENGTH

    def __iter__(self) -> Iterator[T]:
        raise StopIteration()


def _map_succ(x: str) -> str:
    return str(1 + int(x))


def _map_pred(x: str) -> str:
    return str(int(x) - 1)


def _singularize(x: str) -> str:
    res = _inflector.singular_noun(x)
    if res is False:
        return x  # we passed in singular
    assert isinstance(res, str)
    return res


def _pluralize(x: str) -> str:
    res = _inflector.plural(x)
    assert isinstance(res, str)
    return res


SUCCESSOR = _PredicateMap(_map_succ)
PREDECESSOR = _PredicateMap(_map_pred)
SINGULAR = _PredicateMap(_singularize)
PLURAL = _PredicateMap(_pluralize)


__all__ = ["SUCCESSOR", "PREDECESSOR", "SINGULAR", "PLURAL"]

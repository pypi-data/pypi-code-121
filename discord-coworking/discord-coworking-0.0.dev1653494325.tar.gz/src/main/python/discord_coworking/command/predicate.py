from dataclasses import dataclass
from typing import Callable, TypeVar, Generic, Dict, Iterable, Optional, List

E = TypeVar('E')


class Predicate(Generic[E]):

    def __call__(self, e: E) -> bool:
        raise NotImplementedError()

    def filter(self, iterable: Iterable[E]) -> Iterable[E]:
        for e in iterable:
            if self(e):
                yield e

    def any(self, iterable: Iterable[E]) -> Optional[E]:
        for e in iterable:
            if self(e):
                return e
        return None

    def __neg__(self) -> 'Predicate':
        return NotPredicate(self)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        if other is None:
            return False
        if self.__class__ != other.__class__:
            return False
        return self.__dict__ == other.__dict__

    def __or__(self, other: 'Predicate') -> 'Predicate':
        return OrPredicate([self, other])

    def __and__(self, other: 'Predicate') -> 'Predicate':
        return AndPredicate([self, other])


@dataclass()
class FnPredicate(Predicate[E]):
    fn: Callable[[E], bool]

    def __call__(self, e: E) -> bool:
        return self.fn(e)


@dataclass()
class OrPredicate(Predicate[E]):
    predicates: List[Predicate[E]]

    def __call__(self, e: E) -> bool:
        for predicate in self.predicates:
            if predicate(e):
                return True
        return False

    def __or__(self, other: 'Predicate') -> 'Predicate':
        return OrPredicate(self.predicates + [other])


@dataclass()
class AndPredicate(Predicate[E]):
    predicates: List[Predicate[E]]

    def __call__(self, e: E) -> bool:
        for predicate in self.predicates:
            if not predicate(e):
                return False
        return True

    def __and__(self, other: 'Predicate') -> 'Predicate':
        return AndPredicate(self.predicates + [other])


@dataclass()
class NotPredicate(Predicate[E]):
    predicate: Predicate[E]

    def __call__(self, e: E) -> bool:
        return not self.predicate(e)

    def __not__(self) -> 'Predicate':
        return self.predicate


class AnyPredicate(Predicate):

    def __call__(self, *args, **kwargs) -> bool:
        return True

    def __not__(self) -> 'Predicate':
        return NONE


class NonePredicate(Predicate):
    def __call__(self, *args, **kwargs) -> bool:
        return False

    def filter(self, iterable: Iterable[E]) -> Iterable[E]:
        return []

    def any(self, iterable: Iterable[E]) -> Optional[E]:
        return None

    def __not__(self) -> 'Predicate':
        return ANY


ANY = AnyPredicate()

NONE = NonePredicate()


@dataclass()
class ByAttributesPredicate(Predicate[E]):
    attr: Dict

    def __call__(self, e: E) -> bool:
        for k, v in self.attr.items():
            if getattr(e, k) != v:
                return False
        return True

    @classmethod
    def create(cls, **attr):
        return cls(attr)

    @classmethod
    def parse(cls, query: str):
        return cls()

    def __hash__(self):
        return id(self)

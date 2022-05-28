from typing import Any, Callable


class Proposition:
    def __init__(self, f: Callable[[Any], bool]):
        self._f = f

    def __call__(self, x: Any) -> bool:
        return self._f(x)

    def __and__(self, other: 'Proposition') -> 'Proposition':
        return Proposition(lambda x: self._f(x) & other._f(x))

    def __or__(self, other: 'Proposition') -> 'Proposition':
        return Proposition(lambda x: self._f(x) | other._f(x))

    def __invert__(self) -> 'Proposition':
        return Proposition(lambda x: not self._f(x))

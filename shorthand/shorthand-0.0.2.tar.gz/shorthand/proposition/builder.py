from typing import Any, Callable, Collection

from shorthand.proposition.proposition import Proposition


_EMPTY = type("_EMPTY", (), {})()


class PropositionBuilder:
    def __init__(self, key: Any = _EMPTY):
        self._key = key

    def is_(self, x: Any) -> Proposition:
        return self._build(lambda t: t is x)

    def is_not(self, x: Any) -> Proposition:
        return self._build(lambda t: t is not x)

    def eq(self, x: Any) -> Proposition:
        return self._build(lambda t: t == x)

    def neq(self, x: Any) -> Proposition:
        return self._build(lambda t: t != x)

    def lt(self, x: Any) -> Proposition:
        return self._build(lambda t: t < x)

    def le(self, x: Any) -> Proposition:
        return self._build(lambda t: t <= x)

    def gt(self, x: Any) -> Proposition:
        return self._build(lambda t: t > x)

    def ge(self, x: Any) -> Proposition:
        return self._build(lambda t: t >= x)

    def is_in(self, x: Collection) -> Proposition:
        return self._build(lambda t: t in x)

    def is_not_in(self, x: Collection) -> Proposition:
        return self._build(lambda t: t not in x)

    def check(self, t: Callable[[Any], Any], f: Callable[[Any], bool]) -> Proposition:
        return self._build(lambda x: f(t(x)))

    def between(self, start: Any, end: Any, *, left: bool = True, right: bool = True) -> Proposition:
        if left and right:
            return self._build(lambda x: start <= x <= end)
        if not left:
            if not right:
                return self._build(lambda x: start < x < end)
            return self._build(lambda x: start < x <= end)
        return self._build(lambda x: start <= x < end)

    def not_(self) -> Proposition:
        return self._build(lambda t: not t)

    def _build(self, f: Callable[[Any], bool]) -> Proposition:
        if self._key is _EMPTY:
            return Proposition(f)
        return Proposition(lambda x: f(x[self._key]))

    def __getitem__(self, key: Any) -> 'PropositionBuilder':
        return PropositionBuilder(key)

    def bool(self) -> Proposition:
        return self._build(bool)


P: PropositionBuilder = PropositionBuilder()

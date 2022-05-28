from typing import Any, Callable

from shorthand.transformation.transformation import Transformation


class Aggregation:
    def __init__(self, f: Callable[[Any, Any], Any]):
        self._f = f

    def __call__(self, current: Any, new: Any) -> Any:
        return self._f(current, new)

    def __or__(self, other: Callable[[Any, Any], Any]) -> 'Aggregation':
        f = self._f
        g = other._f if isinstance(other, Aggregation) else other

        def _f(current: Any, new: Any) -> Any:
            return g(f(current, new), new)

        return Aggregation(_f)

    def __lshift__(self, other: Callable[[Any], Any]) -> 'Aggregation':
        f = self._f
        g = other._f if isinstance(other, Transformation) else other

        return Aggregation(lambda current, new: f(current, g(new)))

    def __rshift__(self, other: Callable[[Any], Any]) -> 'Aggregation':
        f = self._f
        g = other._f if isinstance(other, Transformation) else other

        return Aggregation(lambda current, new: g(f(current, new)))

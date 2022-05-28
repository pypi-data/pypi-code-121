from typing import Any, Callable


class Transformation:
    def __init__(self, f: Callable[[Any], Any]):
        self._f = f

    def __call__(self, x: Any) -> Any:
        return self._f(x)

    def __rshift__(self, other: Callable[[Any], Any]):
        if isinstance(other, Transformation):
            other = other._f
        return Transformation(lambda x: other(self._f(x)))

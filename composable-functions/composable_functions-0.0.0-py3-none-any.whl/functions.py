from typing import Any, Callable, Tuple


def _identity(x: Any) -> Any:
    return x


class _ComposableFunction:

    __slots__ = "_head", "_tail"

    def __init__(self, head: Callable, tail: Tuple[Callable] = ()):
        self._head = head
        self._tail = tail

    def __call__(self, *args, **kwargs):
        result = self._head(*args, **kwargs)
        for fn in self._tail:
            result = fn(result)
        return result

    def compose(self, other: Callable) -> "_ComposableFunction":
        """
        Being self => f and other => g, compose f & g
        in forward direction: f o g => f(g(x)).
        """
        if isinstance(other, _ComposableFunction):
            return _ComposableFunction(
                other._head, (*other._tail, self._head, *self._tail)
            )
        return _ComposableFunction(other, (self._head, *self._tail))

    def rcompose(self, other: Callable) -> "_ComposableFunction":
        """
        Being self => f and other => g, compose f & g in
        backwards direction: g o f => g(f(x)).
        """
        if isinstance(other, _ComposableFunction):
            return _ComposableFunction(
                self._head, (*self._tail, other._head, *other._tail)
            )
        return _ComposableFunction(self._head, (*self._tail, other))

    def __rshift__(self, other: Callable) -> "_ComposableFunction":
        """
        f >> g
        Output of f is set as infput of g => g o f = g(f(x))
        """
        return self.rcompose(other)

    def __lshift__(self, other: Callable) -> "_ComposableFunction":
        """
        f << g
        Output of g is set as input of f => f o g = f(g(x))
        """
        return self.compose(other)

    def __ror__(self, value):
        return self.__call__(value)


composable = _ComposableFunction
identity = _ComposableFunction(_identity)
I = identity


def rcompose(*args: Callable) -> Callable:
    """
    compose(f, g, h) in backwards direction => h o g o f => h(g(f(x)))
    """
    if not args:
        return I
    if len(args) == 1:
        return composable(args[0])
    return _ComposableFunction(args[0], args[1:])


def compose(*args: Callable) -> Callable:
    """
    compose(f, g, h) in forward direction => f o g o h => f(g(h(x)))
    """
    return rcompose(*list(reversed(args)))


__all__ = ["identity", "I", "composable", "compose", "rcompose"]

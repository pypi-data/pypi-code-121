from inspect import Parameter, signature
from typing import Callable, Tuple
import abc

_INVALID_ARITIES = (
    Parameter.VAR_KEYWORD,
    Parameter.KEYWORD_ONLY,
    Parameter.VAR_POSITIONAL,
)

class CurriedFunction(abc.ABC):

    __slots__ = ["_fn", "_bindings"]

    def __init__(self, fn: Callable, bindings: Tuple):
        self._fn = fn
        self._bindings = bindings
    
    @abc.abstractmethod
    def __call__(self, x):
        raise NotImplementedError()


class BoundCurriedFunction(CurriedFunction):

    def __call__(self, x):
        return self._fn(*self._bindings, x)


class UnboundCurriedFunction(CurriedFunction):

    def __call__(self, x) -> Callable:
        sig = signature(self._fn)
        bindings = (*self._bindings, x)
        if len(bindings) == len(sig.parameters) - 1:
            return BoundCurriedFunction(self._fn, bindings)
        return UnboundCurriedFunction(self._fn, bindings)


def _has_invalid_arity(fn: Callable) -> bool:
    return any(
        param.kind in _INVALID_ARITIES for param in signature(fn).parameters.values()
    )


def _should_bypass_currying(fn: Callable) -> bool:
    return len(signature(fn).parameters) < 2 or isinstance(fn, CurriedFunction)

def curry(fn: Callable) -> Callable:
    if _should_bypass_currying(fn):
        return fn
    if _has_invalid_arity(fn):
        raise TypeError(
            "Currying functions with *args or keyword-only args is not supported"
        )
    return UnboundCurriedFunction(fn, ())

import functools
from typing import TypeVar, Callable

_T = TypeVar("_T")
_FUNC_T = TypeVar("_FUNC_T", bound=Callable)


def run_once(func: _FUNC_T) -> _FUNC_T:
    computed = False
    result = None

    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        nonlocal result
        nonlocal computed

        if not computed:
            result = func(*args, **kwargs)
            computed = True

        return result

    return func_wrapper


def identity(x: _T) -> _T:
    return x


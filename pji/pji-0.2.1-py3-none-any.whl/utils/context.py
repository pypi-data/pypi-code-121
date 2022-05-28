from contextlib import contextmanager
from typing import TypeVar

_T = TypeVar('_T')


@contextmanager
def eclosing(obj: _T, close: bool = True) -> _T:
    try:
        yield obj
    finally:
        if close:
            obj.close()

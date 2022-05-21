from abc import abstractmethod, ABC
from typing import TypeVar, Optional, Callable, Type, Union

_T = TypeVar("_T")
# noinspection PyTypeChecker
_C = TypeVar('_C', bound=Type)


def unone(v: Optional[_T], on_none: Callable[[], _T]) -> _T:
    """
    :param v: the value to check
    :param on_none: callable to execute in the case where v is None
    :return:  `v` if `v` is not None otherwise `on_none()`
    """
    if v is None:
        return on_none()
    return v


def unone_raise(v: Optional[_T], on_none: Callable[[], Exception] = lambda: ValueError('unexpected None')) -> _T:
    """
    :param v: the value to check
    :param on_none: callable to execute in the case where v is None
    :return:  `v` if `v` is not None otherwise raises the exception returned by `on_none()`
    """
    if v is None:
        raise on_none()
    return v


def take_if(value: _T, predicate: Union[Callable[[_T], bool], bool]) -> Optional[_T]:
    """
    :param value: the value to check
    :param predicate: predicate accepting the value or a boolean indicating if accepting the value
    :return: `value` if `predicate(value)` is `True` otherwise `None`
    """

    if callable(predicate):
        if predicate(value):
            return value
    elif predicate:
        return value
    return None


# Common Exceptions

class IllegalStateException(Exception):
    ...


class UnsupportedOperationException(Exception):
    ...


class NoSuchElementException(Exception):
    ...


# Common classes

class Closeable(ABC):
    @abstractmethod
    def close(self): ...

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

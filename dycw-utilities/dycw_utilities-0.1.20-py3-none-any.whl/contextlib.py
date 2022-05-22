from contextlib import AbstractContextManager
from contextlib import contextmanager as _contextmanager
from typing import Callable
from typing import Iterator
from typing import TypeVar

from typing_extensions import ParamSpec

from dycw_utilities.typeguard import typeguard_ignore


_P = ParamSpec("_P")
_T = TypeVar("_T")


def contextmanager(
    func: Callable[_P, Iterator[_T]], /
) -> Callable[_P, AbstractContextManager[_T]]:
    """Lift an iterator returning a single value into a context manager. Also
    disable typeguard for such functions.
    """

    return typeguard_ignore(_contextmanager(func))

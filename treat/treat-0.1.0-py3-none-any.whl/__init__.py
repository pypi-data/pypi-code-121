from functools import wraps
from typing import TYPE_CHECKING
from typing import Callable
from typing import Type
from typing import TypeVar


__version__ = "0.1.0"


T = TypeVar("T")


if TYPE_CHECKING:
    from _pytest.python_api import RaisesContext


def it(description: str) -> Callable[..., T]:
    return test(f"it {description}")


def test(description: str) -> Callable[..., T]:
    def _test(func: Callable[..., T]) -> Callable[..., T]:
        func.__treat_description__ = description

        @wraps(func)
        def _wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return _wrapper

    return _test


def raises(
    expected_exception: Type[BaseException], **kwargs
) -> "RaisesContext[BaseException]":
    from treat.pytest._augmentations import RaisesContext

    return RaisesContext(expected_exception, **kwargs)

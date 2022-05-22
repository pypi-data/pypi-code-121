from collections.abc import Callable
from typing import Any
from typing import TypeVar


try:
    from typeguard import typeguard_ignore as _typeguard_ignore
except ImportError:  # pragma: no cover

    _T = TypeVar("_T", bound=Callable[..., Any])

    def typeguard_ignore(x: _T, /) -> _T:
        return x

else:
    typeguard_ignore = _typeguard_ignore  # type: ignore

from typing import Tuple, TypeVar

__all__ = (
    'pass_through_any',
    'pass_through_one'
)

_T = TypeVar('_T')


def pass_through_any(*args: _T) -> Tuple[_T, ...]:
    """Passes through any positional arguments."""
    return args


def pass_through_one(arg: _T) -> _T:
    """Passes through one argument."""
    return arg

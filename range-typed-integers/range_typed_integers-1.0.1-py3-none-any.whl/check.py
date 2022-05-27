from __future__ import annotations

import warnings
from typing import Type, Tuple, Union, Optional, Any
try:
    # We prefer this version since it has include_extras for sure.
    from typing_extensions import get_type_hints  # type: ignore
except ImportError:
    from typing import get_type_hints  # type: ignore

from range_typed_integers.types import *


def u8_checked(value: int) -> u8:
    r = get_range(u8)
    assert r
    if r.min <= value <= r.max:
        return u8(value)
    raise IntegerBoundError(f'Value {value} is out of range for u8 (must be between {r.min} and {r.max})')


def i8_checked(value: int) -> i8:
    r = get_range(i8)
    assert r
    if r.min <= value <= r.max:
        return i8(value)
    raise IntegerBoundError(f'Value {value} is out of range for i8 (must be between {r.min} and {r.max})')


def u16_checked(value: int) -> u16:
    r = get_range(u16)
    assert r
    if r.min <= value <= r.max:
        return u16(value)
    raise IntegerBoundError(f'Value {value} is out of range for u16 (must be between {r.min} and {r.max})')


def i16_checked(value: int) -> i16:
    r = get_range(i16)
    assert r
    if r.min <= value <= r.max:
        return i16(value)
    raise IntegerBoundError(f'Value {value} is out of range for i16 (must be between {r.min} and {r.max})')


def u32_checked(value: int) -> u32:
    r = get_range(u32)
    assert r
    if r.min <= value <= r.max:
        return u32(value)
    raise IntegerBoundError(f'Value {value} is out of range for u32 (must be between {r.min} and {r.max})')


def i32_checked(value: int) -> i32:
    r = get_range(i32)
    assert r
    if r.min <= value <= r.max:
        return i32(value)
    raise IntegerBoundError(f'Value {value} is out of range for i32 (must be between {r.min} and {r.max})')


def u64_checked(value: int) -> u64:
    r = get_range(u64)
    assert r
    if r.min <= value <= r.max:
        return u64(value)
    raise IntegerBoundError(f'Value {value} is out of range for u64 (must be between {r.min} and {r.max})')


def i64_checked(value: int) -> i64:
    r = get_range(i64)
    assert r
    if r.min <= value <= r.max:
        return i64(value)
    raise IntegerBoundError(f'Value {value} is out of range for i64 (must be between {r.min} and {r.max})')


class CheckIntWarning(UserWarning):
    """This warning is emitted when check_int could not find a type annotation for the given type."""
    pass


class IntegerBoundError(OverflowError):
    """Raised when an integer did not fit into its declared type."""


V = TypeVar('V', bound=Type[Any])


def check_int(typ: Union[V, Tuple[object, str]], value: Any, *, suppress_warning_for_unresolved_hints: bool = False) -> bool:
    """
    Checks if the specified integer fits into the type typ.

    typ can either be a type or an object and an attribute name as a tuple. In the second case,
    the type info is extracted from the object using typing.get_type_info and the type annotation for the
    given attribute by name is used.

    If the type is an integer type and the value is an integer, this checks the range of the integer and returns
    whether it fits. If the integer type is not annotated with a range, this returns True.

    This will raise a ValueError if the type passed in is a valid integer type, but the value is not an integer.

    If the type is not a subclass of int, this always returns True.
    """
    if isinstance(typ, tuple):
        try:
            typ = get_type_hints(typ[0], include_extras=True)[typ[1]]  # type: ignore
        except (IndexError, KeyError) as ex:
            if not suppress_warning_for_unresolved_hints:
                warnings.warn(
                    f"The type {typ[0]} does not have a type hint for {typ[1]}. "  # type: ignore
                    f"Make sure the hint is present on the class (!).",
                    CheckIntWarning
                )

    if is_optional(typ) and value is None:
        return True

    r = get_range(typ)

    if not isinstance(value, int):
        try:
            if r is not None or issubclass(typ, int):  # type: ignore
                raise ValueError(f"The value {value} must be an int.")
        except TypeError:
            # TypeError: issubclass() arg 1 must be a class
            # In that case the type doesn't seem to be an integer or any subclass, so we continue.
            pass

    if r is not None:
        return r.min <= value <= r.max
    return True


def get_range(typ: Any) -> Optional[ValueRange]:
    """Returns the ValueRange object that ``typ`` is annotated with. If it's not annotated, None is returned."""
    if is_optional(typ):
        try:
            typ = next((arg for arg in typ.__args__ if not isinstance(arg, type(None))))
        except StopIteration:
            return None

    if hasattr(typ, '__supertype__'):
        typ = typ.__supertype__

    if hasattr(typ, '__metadata__') and hasattr(typ, '__origin__'):
        if not issubclass(typ.__origin__, (int,)):
            raise ValueError(f"The type {typ} must be a subclass of {int}.")
        r = typ.__metadata__[0]
        if isinstance(r, ValueRange):
            return r
    return None


def is_optional(typ: Any) -> bool:
    if hasattr(typ, '__origin__') and typ.__origin__ == Union and \
        hasattr(typ, '__args__') and type(None) in typ.__args__ and len(typ.__args__) == 2:
        return True
    return False

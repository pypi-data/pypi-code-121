"""Module with functions for 'type_hints' subpackage."""

from __future__ import annotations
from typing import Any, Union
import sys

from typeguard import typechecked  # , check_type
from typing_extensions import Literal, get_origin, get_args, get_type_hints

import mylogging


def typechecked_compatible(function):
    """Turns off type checking for old incompatible python versions.

    Mainly for new syntax like list[str] which raise TypeError.
    """
    if sys.version_info.minor < 9:
        return function
    return typechecked(function)


class ValidationError(TypeError):
    """To know that error is because of bad config type and not some TypeError from the inside."""

    pass


def validate_sequence(value, variable):
    """Ensure, that defined sequence is not just a string.

    Usually with Sequence we means for example tuple or list of items. String in some cases is not valid type
    then. This ensure, that this is Sequence, but not just string.

    Args:
        value (Sequence): Variable where we want to ensure Sequence type.
        variable (_type_): If it is just string, this will raise an error with name of variable with
            incorrect type.

    Raises:
        TypeError: If it is just a string.
    """
    if isinstance(value, str):
        raise TypeError(
            f"Variable '{variable}' must not be string, but Sequence. It can be tuple or list for example. "
            "Beware that if you use tuple with just one member like this ('string'), it's finally parsed as "
            "string. If this is the case, add coma like this ('string',)."
        )


# def validate(value, allowed_type: Any, name: str) -> None:
#     """Type validation. It also works for Union and validate Literal values.

#     Instead of typeguard validation, it define just subset of types, but is simplier
#     and needs no extra import, therefore can be faster.

#     Args:
#         value (Any): Value that will be validated.
#         allowed_type (Any, optional): For example int, str or list. It can be also Union
#             or Literal. If Literal, validated value has to be one of Literal values.
#             Defaults to None.
#         name (str | None, optional): If error raised, name will be printed. Defaults to None.

#     Raises:
#         ValidationError: Type does not fit.

#     Examples:
#         >>> from typing_extensions import Literal
#         ...
#         >>> validate(1, int)
#         >>> validate(None, list | None)
#         >>> validate("two", Literal["one", "two"])
#         >>> validate("three", Literal["one", "two"])
#         Traceback (most recent call last):
#         ValidationError: ...
#     """
#     check_type(value=value, expected_type=allowed_type, argname=name)

# TODO Wrap error with colors and remove stack only to configuration line...
# try:
#     check_type(value=value, expected_type=allowed_type, argname=name)
# except TypeError:

#     # ValidationError(mylogging.format_str("validate"))

#     raise


def small_validate(value, allowed_type: None | Any = None, name: str | None = None) -> None:
    """Type validation. It also works for Union and validate Literal values.

    Instead of typeguard validation, it define just subset of types, but is simplier
    and needs no extra import, therefore can be faster.

    Args:
        value (Any): Value that will be validated.
        allowed_type (Any, optional): For example int, str or list. It can be also Union or Literal.
            If Literal, validated value has to be one of Literal values. If None, it's skipped.
            Defaults to None.
        name (str | None, optional): If error raised, name will be printed. Defaults to None.

    Raises:
        TypeError: Type does not fit.

    Examples:
        >>> from typing_extensions import Literal
        ...
        >>> small_validate(1, int)
        >>> small_validate(None, Union[list, None])
        >>> small_validate("two", Literal["one", "two"])
        >>> small_validate("three", Literal["one", "two"])
        Traceback (most recent call last):
        ValidationError: ...
    """
    if allowed_type:
        # If Union
        if get_origin(allowed_type) == Union:

            if type(value) in get_args(allowed_type):
                return
            else:
                raise ValidationError(
                    mylogging.format_str(
                        f"Allowed type for variable '{name}' are {allowed_type}, but you try to set an {type(value)}"
                    )
                )

        # If Literal - parse options
        elif get_origin(allowed_type) == Literal:
            options = getattr(allowed_type, "__args__")
            if value in options:
                return
            else:
                raise ValidationError(
                    f"New value < {value} > for variable < {name} > is not in allowed options {options}."
                )

        else:
            if isinstance(value, allowed_type):  # type: ignore
                return
            else:
                raise ValidationError(
                    f"Allowed allowed_type for variable < {name} > is {allowed_type}, but you try to set an {type(value)}"
                )

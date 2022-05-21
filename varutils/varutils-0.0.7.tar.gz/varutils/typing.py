from typing import Any, Union, Type, Tuple, Optional, Iterable, Iterator

from varname import argname

from varutils.errors import IncompatibleTypeError

__all__ = (
    'get_fully_qualified_name',
    'get_fully_qualified_names',
    'check_type_compatibility'
)


def get_fully_qualified_name(typ: Type) -> str:
    """Returns fully qualified name of a type."""
    name = typ.__name__
    type_module = typ.__module__
    if type_module != 'builtins':
        name = f"{type_module}.{name}"
    return name


def get_fully_qualified_names(types: Iterable[Type]) -> Iterator[str]:
    """Returns fully qualified names of type objects."""
    return map(get_fully_qualified_name, types)


def check_type_compatibility(var: Any,
                             expected_type: Union[Type, Tuple[Type, ...]],
                             expected_msg: Optional[str] = None) -> None:
    """
    Checks type compatibility between a variable and the expected type.

    Args:
        var:            variable ot attribute to check.
        expected_type:  expected type.
        expected_msg:   error message suffix.
    """
    if not isinstance(expected_type, tuple):
        expected_type = (expected_type,)

    if not isinstance(var, expected_type):
        if expected_msg is None:
            expected_msg = ', '.join(get_fully_qualified_names(expected_type))
            if len(expected_type) != 1:
                expected_msg = f'[{expected_msg}]'
        typename = get_fully_qualified_name(type(var))
        raise IncompatibleTypeError(
            f"Incompatible type for argument '{argname('var')}': "
            f"{typename}. Expected: {expected_msg}"
        )

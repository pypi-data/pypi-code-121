"""
Functional interface to code representations.
"""
from enum import Enum
from typing import Optional, Any

from ._builtins import type_code_repr, enum_code_repr
from ._CodeRepresentable import CodeRepresentable
from ._error import IsNotCodeRepresentableType, CodeRepresentationError, IsNotCodeRepresentableValue
from ._honorary_members import get_honorary_code_repr_function
from ._typing import CodeReprFunction, CodeRepresentation


def get_code_repr_function(cls: type) -> Optional[CodeReprFunction]:
    """
    Gets the code_repr function for the given type.

    :param cls:     The type to get the function for.
    :return:        The code_repr function, or None if none available.
    """
    # Check for honorary members
    honorary_code_repr_function = get_honorary_code_repr_function(cls)
    if honorary_code_repr_function is not None:
        return honorary_code_repr_function

    # Check for CodeRepresentable sub-types
    if issubclass(cls, CodeRepresentable):
        return cls.code_repr

    # Types are also code-representable
    if issubclass(cls, type):
        return type_code_repr

    # Enumerations are also code representable
    if issubclass(cls, Enum):
        return enum_code_repr

    return None


def code_repr(obj: Any) -> CodeRepresentation:
    """
    Gets the code representation of the object.

    :return:                                The code representation.
    :raises IsNotCodeRepresentableType:     If the value's type is not a code-representable type.
    :raises IsNotCodeRepresentableValue:    If the value is not code-representable.
    """
    # Get the object's type
    cls = type(obj)

    # Get the code_repr function
    code_repr_function = get_code_repr_function(cls)

    # If it doesn't have a function, it's not code-representable
    if code_repr_function is None:
        raise IsNotCodeRepresentableType(cls)

    # Try to get the code-representation of the object
    try:
        return code_repr_function(obj)

    # If it fails, the value is not code-representable
    except CodeRepresentationError as e:
        raise IsNotCodeRepresentableValue(obj) from e

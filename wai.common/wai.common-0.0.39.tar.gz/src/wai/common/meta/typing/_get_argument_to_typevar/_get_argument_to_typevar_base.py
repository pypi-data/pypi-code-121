"""
Module for common functionality for get_argument_to_typevar between Python versions.
"""
from typing import Type, TypeVar, Tuple

import typing_inspect


def check_args(cls: Type, generic_base_class: Type, typevar: TypeVar) -> int:
    """
    Performs argument-validation for get_argument_to_typevar.

    :param cls:                 The sub-class specifying the argument.
    :param generic_base_class:  The generic base-class specifying the type variable.
    :param typevar:             The type variable to get the argument for.
    :return:                    The index of the typevar in the base class' parameters.
    """
    # Make sure the class derives from the base-class
    if not issubclass(cls, generic_base_class):
        raise ValueError(f"{cls.__name__} does not derive from {generic_base_class.__name__}")

    # Make sure the base class is generic
    if not typing_inspect.is_generic_type(generic_base_class):
        raise TypeError(f"{generic_base_class.__name__} is not a generic type")

    # Get the type parameters to the generic base class
    parameters = typing_inspect.get_parameters(generic_base_class)

    # Make sure the type variable is a parameter to the base class
    if typevar not in parameters:
        raise ValueError(f"{typevar} is not a generic parameter of {generic_base_class.__name__}")

    return parameters.index(typevar)

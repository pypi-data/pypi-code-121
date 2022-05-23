"""
Module for code_repr functions for builtin types.
"""
from enum import Enum
from typing import Tuple, Iterator, Callable, Any

from .._import_code import get_import_code
from ._typing import CodeRepresentation


def type_code_repr(cls: type) -> CodeRepresentation:
    """
    The code_repr function for types.

    :param cls:     The type to get the code representation for.
    :return:        The code representation of the type.
    """
    # Get the import code for the class
    import_code = get_import_code(cls, alias_inner_class=False)

    return {cls.__qualname__: import_code}, cls.__qualname__


def primitive_code_repr(primitive) -> CodeRepresentation:
    """
    Gets the code representation for a primitive (float, str, etc.).

    :param primitive:   A primitive value.
    :return:            The value's code representation.
    """
    # No imports required, and code can be got from repr
    return {}, repr(primitive)


def container_code_repr(open_brace: str,
                        close_brace: str,
                        element_iterator: Iterator[Tuple],
                        formatter: Callable[[Any], str]) -> CodeRepresentation:
    """
    Base functionality for getting the code-representation
    of one of the container types.

    :param open_brace:                  The start of the code representation.
    :param close_brace:                 The end of the code representation.
    :param element_iterator:            An iterator over tuples containing the elements of the container.
    :param formatter:                   A formatter which formats the code of an element
                                        into its container representation.
    :return:                            The code representation of the container.
    :raises CodeRepresentationError:    If the container can't be represented.
    """
    # Local imports to avoid circularity errors
    from ._functional import code_repr
    from ._utilities import combine_import_dicts, get_import_dict, get_code

    # Initialise the code representation with an open bracket and empty imports
    import_dict = {}
    code = open_brace

    # Process each element in turn
    first = True
    for element in element_iterator:
        # Get the code-representation for the element
        element_reprs = tuple(map(code_repr, element))

        # Add the element imports to our own
        import_dict = combine_import_dicts(import_dict, *map(get_import_dict, element_reprs))

        # Insert a comma for every item after the first
        if first:
            first = False
        else:
            code += ", "

        # Add the key-value pair representation
        code += formatter(*map(get_code, element_reprs))

    # Close out the braces
    code += close_brace

    return import_dict, code


def dict_code_repr(value: dict) -> CodeRepresentation:
    """
    The code_repr function for dictionaries.

    :param value:   The dictionary.
    :return:        The code-representation of the dictionary.
    """
    return container_code_repr("{",
                               "}",
                               map(tuple, value.items()),
                               lambda key, val: f"{key}: {val}")


def list_code_repr(value: list) -> CodeRepresentation:
    """
    Gets the code representation for a list.

    :param value:   The list.
    :return:        It's code representation.
    """
    return container_code_repr("[",
                               "]",
                               ((el,) for el in value),
                               lambda el: el)


def tuple_code_repr(value: tuple) -> CodeRepresentation:
    """
    Gets the code representation for a tuple.

    :param value:   The tuple.
    :return:        It's code representation.
    """
    return container_code_repr("(",
                               ")",
                               ((el,) for el in value),
                               lambda el: el)


def set_code_repr(value: set) -> CodeRepresentation:
    """
    Gets the code representation for a set.

    :param value:   The set.
    :return:        It's code representation.
    """
    return container_code_repr("{",
                               "}",
                               ((el,) for el in value),
                               lambda el: el)


def frozenset_code_repr(value: frozenset) -> CodeRepresentation:
    """
    Gets the code representation for a frozenset.

    :param value:   The frozenset.
    :return:        It's code representation.
    """
    return container_code_repr("frozenset({",
                               "})",
                               ((el,) for el in value),
                               lambda el: el)


def enum_code_repr(value: Enum):
    """
    The code_repr function for enumerations.

    :param value:   The enum being represented.
    :return:        The code representation of the enum.
    """
    # Get the enum type
    enum_type = type(value)

    # Get the import code for the enumeration
    import_code = get_import_code(enum_type, alias_inner_class=False)

    return {enum_type.__qualname__: import_code}, f"{enum_type.__qualname__}.{value.name}"

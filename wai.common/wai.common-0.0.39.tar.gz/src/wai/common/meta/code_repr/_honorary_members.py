"""
Module defining the honorary members of the CodeRepresentable class.
"""
from typing import Optional, Dict

from ._builtins import (
    primitive_code_repr,
    dict_code_repr,
    list_code_repr,
    tuple_code_repr,
    set_code_repr,
    frozenset_code_repr
)
from ._typing import CodeReprFunction

# The honorary code-representable types, and their code_repr methods.
HONORARY_MEMBERS: Dict[type, CodeReprFunction] = {
    str: primitive_code_repr,
    bytes: primitive_code_repr,
    bytearray: primitive_code_repr,
    complex: primitive_code_repr,
    float: primitive_code_repr,
    int: primitive_code_repr,
    bool: primitive_code_repr,
    type(None): primitive_code_repr,
    range: primitive_code_repr,
    slice: primitive_code_repr,
    dict: dict_code_repr,
    list: list_code_repr,
    tuple: tuple_code_repr,
    set: set_code_repr,
    frozenset: frozenset_code_repr
}


def get_honorary_code_repr_function(cls: type) -> Optional[CodeReprFunction]:
    """
    Gets the code_repr function for an honorary type.

    :param cls:     The type.
    :return:        The code_repr function if it exists, otherwise None.
    """
    return HONORARY_MEMBERS.get(cls, None)

from enum import Enum
from typing import List, Type, TypeVar

T = TypeVar("T", bound=Enum)


def enum_value_list(enum_class: Type[T]) -> List[str]:
    """
    Returns a list with all the values in the enum
    """

    return [item.value for item in enum_class]


def enum_value_list_as_string(enum_class: Type[T], separator: str = ", ") -> str:
    """
    Returns a string with all the values of an Enum separated by a separator
    """

    return separator.join(enum_value_list(enum_class))


__all__ = ["enum_value_list", "enum_value_list_as_string"]

from enum import Enum
from typing import Optional, Type, TypeVar

# Generic that can only be an Enum or a sub class of Enum
T = TypeVar("T", bound=Enum)


def enum_type_guard(value: str, enum_class: Type[T]) -> Optional[T]:
    """
    Takes a string and an Enum class or a sub class of Enum and returns the typed value or None.
    """

    return (
        enum_class(value) if value in set(item.value for item in enum_class) else None
    )


__all__ = ["enum_type_guard"]

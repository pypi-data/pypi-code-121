from enum import Enum
from typing import Any


class StrEnum(str, Enum):
    """An enum whose elements are themselves strings."""

    @staticmethod
    def _generate_next_value_(
        name: str, start: Any, count: int, last_values: Any
    ) -> str:
        _ = start, count, last_values
        return name

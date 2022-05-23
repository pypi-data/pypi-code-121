from typing import Any

from ._AbstractField import AbstractField
from ._Field import Field
from ._PrefixOnlyField import PrefixOnlyField
from ._DataType import DataType


class PrefixField(Field, PrefixOnlyField):
    """
    A compound field that only displays the first half of the name.
    """
    # The dummy suffix
    DUMMY_SUFFIX: str = "DUMMY"

    def __init__(self, *args):
        if len(args) == 0:
            args = (None, DataType.NUMERIC)
        elif len(args) > 2:
            raise ValueError("PrefixField only takes 0, 1 or 2 arguments to __init__")

        super().__init__(*args)

        if self.name is not None:
            if not self.is_compound():
                self.name = self.name + self.SEPARATOR + self.DUMMY_SUFFIX
            else:
                self.name = self.get_prefix() + self.SEPARATOR + self.DUMMY_SUFFIX

    def compare_to(self, other: Any) -> int:
        if other is None:
            return 1

        if not isinstance(other, AbstractField):
            return -1

        if self.get_prefix() is None and other.get_prefix() is None:
            return 0

        if self.get_prefix() is None:
            return -1

        if other.get_prefix() is None:
            return 1

        return (-1 if self.get_prefix().lower() < other.get_prefix().lower() else
                0 if self.get_prefix().lower() == other.get_prefix().lower() else
                1)

    def to_string(self) -> str:
        if self.name is None:
            return ""

        return self.get_prefix()

    def to_display_string(self) -> str:
        return self.to_string()

    @staticmethod
    def parse_field(string: str) -> Field:
        return PrefixField(Field.parse_field(string))

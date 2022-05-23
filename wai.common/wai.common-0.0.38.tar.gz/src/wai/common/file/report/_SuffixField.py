from typing import Any

from ._AbstractField import AbstractField
from ._Field import Field
from ._SuffixOnlyField import SuffixOnlyField
from ._DataType import DataType


class SuffixField(Field, SuffixOnlyField):
    """
    A compound field that only displays the second half of the name.
    """
    # The dummy suffix
    DUMMY_PREFIX: str = "DUMMY"

    def __init__(self, *args):
        if len(args) == 0:
            args = (None, DataType.UNKNOWN)
        elif len(args) > 2:
            raise ValueError("PrefixField only takes 0, 1 or 2 arguments to __init__")

        super().__init__(*args)

        if self.name is not None:
            if not self.is_compound():
                self.name = self.DUMMY_PREFIX + self.SEPARATOR + self.name
            else:
                self.name = self.DUMMY_PREFIX + self.SEPARATOR + self.get_suffix()

    def compare_to(self, other: Any) -> int:
        if other is None:
            return 1

        if not isinstance(other, AbstractField):
            return -1

        if self.get_suffix() is None and other.get_suffix() is None:
            return 0

        if self.get_suffix() is None:
            return -1

        if other.get_suffix() is None:
            return 1

        return (-1 if self.get_suffix().lower() < other.get_suffix().lower() else
                0 if self.get_suffix().lower() == other.get_suffix().lower() else
                1)

    def to_string(self) -> str:
        if self.name is None:
            return ""

        return self.get_suffix()

    def to_display_string(self) -> str:
        return self.to_string()

    @staticmethod
    def parse_field(string: str) -> Field:
        return SuffixField(Field.parse_field(string))

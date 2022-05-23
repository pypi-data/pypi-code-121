from enum import Enum, unique
from numbers import Real
from typing import Optional, Any, Union


@unique
class DataType(Enum):
    """
    The type of a field in a report.
    """
    STRING = "S"
    NUMERIC = "N"
    BOOLEAN = "B"
    UNKNOWN = "U"

    def to_display(self) -> str:
        """
        Returns the display string.

        :return:    The display string.
        """
        return self.value

    def to_raw(self) -> str:
        """
        Returns the raw enum string.

        :return:    The raw enum string.
        """
        return self.name

    def __str__(self) -> str:
        return self.to_display()

    @classmethod
    def value_of(cls, string: str) -> "DataType":
        """
        Gets the enum constant with the given name.

        :param string:  The name of the enum member.
        :return:        The enum instance.
        """
        return cls[string]

    @classmethod
    def parse(cls, string: str) -> Optional["DataType"]:
        """
        Parses the given string and returns the associated enum.

        :param string:  The string to parse.
        :return:        The enum, or None if not found.
        """
        # Attempt to parse enum name first
        try:
            return cls.value_of(string)
        except Exception:
            pass

        # Then try one-letter code
        try:
            return DataType(string)
        except Exception:
            pass

        return None

    @classmethod
    def guess_type(cls, obj: Any) -> "DataType":
        """
        Guesses the datatype from the object. In the case of string, checks
        if the string represents a number, then a boolean, then defaults to
        string.

        :param obj: The object to inspect.
        :return:    The datatype.
        """
        # If the object is a string, try to convert it
        if isinstance(obj, str):
            for datatype in (DataType.NUMERIC, DataType.BOOLEAN):
                try:
                    obj = datatype.convert(obj)
                except Exception:
                    pass

        # If the object is a number, return NUMERIC
        if isinstance(obj, Real):
            return DataType.NUMERIC

        # If the object is a bool, return BOOLEAN
        if isinstance(obj, bool):
            return DataType.BOOLEAN

        # Default to string
        return DataType.STRING

    def convert(self, obj: Any) -> Union[str, float, bool]:
        """
        Converts a value into the correct internal type for this
        datatype.

        :param obj:     The value to convert.
        :return:        The converted value.
        """
        if self is DataType.BOOLEAN:
            return bool(obj)
        elif self is DataType.NUMERIC:
            return float(obj)
        else:
            return str(obj)

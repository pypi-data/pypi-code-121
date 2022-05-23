from ._AbstractField import AbstractField
from ._DataType import DataType
from ._RegularField import RegularField


class Field(RegularField, AbstractField):
    """
    A single report field identifier.
    """
    @staticmethod
    def is_valid(string: str) -> bool:
        """
        Checks whether the field is valid.

        :param string:  The string to check.
        :return:        True if valid format
        """
        # Must be long enough to have a type-string
        if len(string) <= 3:
            return False

        # Get the type string characters
        string = string[-3:]

        # Make sure the type-string is wrapped in []
        if not string.startswith("[") or not string.endswith("]"):
            return False

        # Get the type-string letter
        string = string[1]

        # Make sure it's a valid type-string letter
        return DataType.parse(string) is not None

    @staticmethod
    def parse_field(string: str) -> "Field":
        """
        Parses the given string and returns the field. The type of the field
        can be append with parentheses: name[type]. Otherwise, UNKNOWN is used
        as type.

        :param string:  The string to parse.
        :return:        The parsed field.
        """
        name: str = string
        datatype: DataType = DataType.UNKNOWN
        if len(string) > 3 and string.endswith("]"):
            type_string: str = string[-3:]
            if type_string.startswith("["):
                type_string = type_string[1]
                datatype = DataType.parse(type_string)
                if datatype is None:
                    datatype = DataType.UNKNOWN
                else:
                    name = name[:-3]

        return Field(Field.unescape(name), datatype)

from abc import ABC
from typing import Optional, List, Any

from ._DataType import DataType


class AbstractField(ABC):
    """
    A single report field identifier.
    """
    # The separator
    SEPARATOR: str = "\t"

    # The escaped separator
    SEPARATOR_ESCAPED: str = "\\t"

    # The replacement for tabs in the fields when displaying in the GUI.
    SEPARATOR_DISPLAY: str = " | "

    def __init__(self, *args):
        # Infer arguments
        if len(args) == 0:
            name = None
            datatype = DataType.UNKNOWN
        elif len(args) == 1 and isinstance(args[0], AbstractField):
            name = args[0].name
            datatype = args[0].datatype
        elif len(args) == 2 and isinstance(args[0], (str, type(None))) and isinstance(args[1], (DataType, type(None))):
            name = args[0]
            datatype = args[1]
        elif len(args) == 3 and isinstance(args[0], str) and isinstance(args[1], str) and \
                isinstance(args[2], (DataType, type(None))):
            name = args[0] + AbstractField.SEPARATOR + args[1]
            datatype = args[2]
        else:
            raise ValueError("Bad arguments to initialise AbstractField")

        self.name: Optional[str] = self.fix_string(self.unescape(name)) if name is not None else None
        self.datatype: DataType = datatype if datatype is not None else DataType.UNKNOWN
        self.prefix: Optional[str] = None
        self.suffix: Optional[str] = None

    def is_compound(self) -> bool:
        """
        Checks whether the name is a compound one, i.e., contains a SEPARATOR.

        :return:    True if the name is a compound one.
        """
        return self.name is not None and AbstractField.SEPARATOR in self.name

    def split(self) -> List[str]:
        """
        Returns the name split up into its single parts.

        :return:    The parts of the compound name.
        """
        if self.name is None:
            return []

        return self.name.split(AbstractField.SEPARATOR)

    def to_parseable_string(self) -> str:
        """
        Returns the name and the type (format: name[type]). Can be restored with parseField.

        :return:    The name and type.
        """
        if self.name is None:
            return ""

        return self.escape(self.name, AbstractField.SEPARATOR_ESCAPED) + f"[{self.datatype}]"

    def to_string(self) -> str:
        """
        Returns the name of the field.

        :return:    The name.
        """
        if self.name is None:
            return ""

        return self.escape(self.name, AbstractField.SEPARATOR_ESCAPED)

    def to_display_string(self) -> str:
        """
        Returns the name of the field.

        :return:    The name.
        """
        if self.name is None:
            return ""

        return self.escape(self.name, AbstractField.SEPARATOR_DISPLAY)

    def value_of(self, string: str) -> Any:
        """
        Parse string to appropriate datatype.

        :param string:  The string to parse.
        :return:        The parsed object: STRING, NUMERIC or BOOLEAN.
        """
        try:
            return self.datatype.convert(self.fix_string(string))
        except Exception:
            return None

    @staticmethod
    def escape(name: str, separator: str) -> str:
        """
        Escapes the name.

        :param name:        The name to escape.
        :param separator:   The separator to use.
        :return:            The escaped name.
        """
        return (
            name.replace(AbstractField.SEPARATOR, separator)
                .replace("[", "\\[")
                .replace("]", "\\]")
        )

    @staticmethod
    def unescape(name: str) -> str:
        """
        Unescapes the name.

        :param name:    The name to unescape.
        :return:        The unescaped name.
        """
        return (
            name.replace(AbstractField.SEPARATOR_ESCAPED, AbstractField.SEPARATOR)
                .replace("\\[", "[")
                .replace("\\]", "]")
        )

    def get_clone(self) -> "AbstractField":
        """
        Returns a cloned copy of itself.

        :return:    The clone.
        """
        return self.__class__(self.name, self.datatype)

    def compare_to(self, other: Any) -> int:
        """
        Compares this object with the specified object for order.  Returns a
        negative integer, zero, or a positive integer as this object is less
        than, equal to, or greater than the specified object.

        :param other:   The object to be compared.
        :return:        A negative integer, zero, or a positive integer as this object
                        is less than, equal to, or greater than the specified object.
        """
        if other is None:
            return 1

        if not isinstance(other, AbstractField):
            return -1

        if self.name is None and other.name is None:
            return 0

        if self.name is None:
            return -1

        if other.name is None:
            return 1

        return (-1 if self.name.lower() < other.name.lower() else
                0 if self.name.lower() == other.name.lower() else
                1)

    def equals(self, other: Any) -> bool:
        """
        The equals method (uses only the name).

        :param other:   The object to compare with.
        :return:        True if the same name.
        """
        return self.compare_to(other) == 0

    def hash_code(self) -> int:
        """
        Hashcode so can be used as hashtable key. Returns the hashcode of the
        name.

        :return:    The hashcode.
        """
        if self.name is None:
            return -1

        return hash(self.name)

    def get_prefix(self) -> Optional[str]:
        """
        Returns the prefix for compound fields.

        :return:    The prefix, None if not compound field.
        """
        if not self.is_compound():
            return None

        if self.prefix is None:
            self.prefix = self.split()[0]

        return self.prefix

    def get_suffix(self) -> Optional[str]:
        """
        Returns the suffix for compound fields.

        :return:    The suffix, None if not compound field.
        """
        if not self.is_compound():
            return None

        if self.suffix is None:
            self.suffix = self.split()[1]

        return self.suffix

    @staticmethod
    def fix_string(string: str) -> str:
        """
        Replace ' with `.

        :param string:  The string to process.
        :return:        The processed string.
        """
        return string.replace("'", "`")

    def __str__(self) -> str:
        return self.to_string()

    def __hash__(self) -> int:
        return self.hash_code()

    def __eq__(self, other) -> bool:
        return self.equals(other)

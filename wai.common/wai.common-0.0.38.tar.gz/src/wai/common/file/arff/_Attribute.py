from abc import ABC, abstractmethod
from typing import Optional, Union, Type, List, Tuple, Iterator

from ._save_helper import quoted
from ._error import ARFFError
from ..._TwoWayDict import TwoWayDict
from . import constants
from ._load_helper import remove_keyword, consume, is_whitespace_only, NAME_PATTERN, UnrecognisedContentError, \
    ATTRIBUTE_TYPE_PATTERN, DATE_FORMAT_PATTERN, NOMINAL_VALUE_PATTERN, remove_quotes


class Attribute(ABC):
    def __init__(self, name: str):
        self.name: str = name

    @abstractmethod
    def copy(self) -> 'Attribute':
        """
        Creates a copy of this attribute.
        """
        pass

    @classmethod
    @abstractmethod
    def type_string(cls) -> str:
        """
        Returns the type-string for this attribute type.
        """
        pass

    @classmethod
    def is_type(cls, *types: Union[str, Type['Attribute']]) -> bool:
        """
        Returns whether this attribute is one of the given types.

        :param types:   The types to check for, each as a string or class.
        :return:        True if the attribute is one of the given types,
                        False if not.
        """
        if len(types) == 0:
            return False
        else:
            for t in types:
                if isinstance(t, str) and cls.type_string() == t:
                    return True
                elif issubclass(cls, t):
                    return True

        return False

    def parse_string(self, string: str):
        """
        Parses a string into the correct internal type for this attribute.

        :param string:  The string to parse.
        :return:        The value for this attribute.
        """
        # Treat the missing value symbol as None
        if string == constants.MISSING_VALUE_SYMBOL:
            return None

        # Otherwise defer to the sub-type
        return self._parse_value(string)

    @abstractmethod
    def _parse_value(self, value):
        """
        Parses an object into the correct type for this attribute.

        :param value:    The value to parse.
        :return:         The internal type representation of the value.
        """
        pass

    @staticmethod
    def from_string(line: str) -> 'Attribute':
        """
        Parses an attribute definition string in ARFF format into an
        attribute object.

        :param line:    The string to parse.
        :return:        An attribute object.
        """
        return parse_line(line)

    def to_string(self) -> str:
        """
        Returns the ARFF format string specification of this attribute.
        """
        additional: str = self.to_string_additional()

        if additional != "":
            additional = " " + additional

        return constants.ATTRIBUTE_SECTION_KEYWORD + " " + quoted(self.name) + additional

    @abstractmethod
    def to_string_additional(self) -> str:
        """
        Returns any additional part of the string representation of this attribute
        after the attribute label and the attribute's name.
        """
        pass

    def __call__(self, value):
        # Missing value is valid for any attribute type
        if value is None:
            return None

        # Otherwise defer to the sub-type
        return self._parse_value(value)

    def __str__(self) -> str:
        return self.to_string()


class NumericAttribute(Attribute):
    """
    Class for numeric attributes.
    """
    def __init__(self, name: str, sub_type: Optional[str] = None):
        super().__init__(name)

        # Check the sub-type is valid
        if sub_type not in {None, constants.REAL_ATTRIBUTE_KEYWORD, constants.INTEGER_ATTRIBUTE_KEYWORD}:
            raise InvalidNumericSubTypeError(sub_type)

        self.sub_type: Optional[str] = sub_type

    def copy(self) -> 'NumericAttribute':
        return NumericAttribute(self.name, self.sub_type)

    @classmethod
    def type_string(cls) -> str:
        return constants.NUMERIC_ATTRIBUTE_KEYWORD

    def _parse_value(self, value) -> float:
        try:
            return float(value)
        except Exception as e:
            raise InvalidValueTypeError(value, self) from e

    def to_string_additional(self) -> str:
        return self.sub_type if self.sub_type is not None else self.type_string()


class NominalAttribute(Attribute):
    """
    Class for nominal attributes.
    """
    def __init__(self, name: str, values: List[str]):
        super().__init__(name)

        self.values: TwoWayDict[int, str] = TwoWayDict[int, str]()
        for index, value in enumerate(values):
            self.values[index] = value

    def copy(self) -> 'NominalAttribute':
        return NominalAttribute(self.name, self.ordered_values())

    def ordered_values(self) -> List[str]:
        """
        Gets a list of the nominal values in specification order.
        """
        return list(self.value_iterator())

    def value_iterator(self) -> Iterator[str]:
        """
        Gets an iterator over the nominal values.
        """
        return (self.values[index] for index in range(len(self.values)))

    def quoted_value_iterator(self) -> Iterator[str]:
        """
        Gets an iterator over the nominal values, quoting as necessary.
        """
        return (quoted(value) for value in self.value_iterator())

    @classmethod
    def type_string(cls) -> str:
        return constants.NOMINAL_ATTRIBUTE_KEYWORD

    def _parse_value(self, value) -> str:
        if isinstance(value, int):
            return self.values[value]
        elif isinstance(value, str):
            if value not in self.values:
                raise InvalidNominalValueError(value, self)

            return value
        else:
            raise InvalidValueTypeError(value, self)

    def to_string_additional(self) -> str:
        return "{" + ",".join(self.quoted_value_iterator()) + "}"

    def __iter__(self):
        return self.value_iterator()

    def __len__(self) -> int:
        return len(self.values)

    def __contains__(self, item: str) -> bool:
        return item in self.values


class StringAttribute(Attribute):
    """
    Class for string attributes.
    """
    def copy(self) -> 'StringAttribute':
        return StringAttribute(self.name)

    @classmethod
    def type_string(cls) -> str:
        return constants.STRING_ATTRIBUTE_KEYWORD

    def _parse_value(self, value) -> str:
        return str(value)

    def to_string_additional(self) -> str:
        return constants.STRING_ATTRIBUTE_KEYWORD


class DateAttribute(Attribute):
    """
    Class for date attributes.
    """
    def __init__(self, name: str, format_string: str):
        super().__init__(name)

        self.format: str = format_string

    def copy(self) -> 'DateAttribute':
        return DateAttribute(self.name, self.format)

    @classmethod
    def type_string(cls) -> str:
        return constants.DATE_ATTRIBUTE_KEYWORD

    def _parse_value(self, value) -> str:
        # TODO
        return value

    def to_string_additional(self) -> str:
        return constants.DATE_ATTRIBUTE_KEYWORD + " " + self.format


def parse_line(line: str) -> 'Attribute':
    """
    Parses an attribute line in ARFF file format into an attribute
    of the correct type.

    :param line:    The attribute line.
    :return:        The attribute.
    """
    # Save the original line for error messages
    original_line = line

    # Remove the @attribute keyword
    line = remove_keyword(line, constants.ATTRIBUTE_SECTION_KEYWORD)

    # Extract the attribute name
    name, line = consume(line, NAME_PATTERN)

    # Check we found a name
    if name is None:
        raise AttributeNameNotFoundError(original_line)

    # Extract the attribute type
    attribute_type, additional, line = consume_attribute_type_information(line)

    # Check we found a type
    if attribute_type is None:
        raise AttributeTypeNotFoundError(original_line)

    # If the line has not been entirely consumed, raise an error
    if not is_whitespace_only(line):
        raise UnrecognisedContentError(line, original_line)

    # Return the attribute and its type (with any additional info)
    return type_string_lookup[attribute_type](name, *additional)


def consume_attribute_type_information(line: str) -> \
        Tuple[Optional[str], Optional[Tuple[Union[str, List[str]]]], str]:
    """
    Extracts the type of an attribute from the beginning of a line.

    :param line:    The line to extract the attribute type from.
    :return:        The attribute type, any additional type information, and the remainder of the line.
    """
    # Find the attribute type
    attribute_type, line = consume(line, ATTRIBUTE_TYPE_PATTERN)

    # Abort if no match found
    if attribute_type is None:
        return None, None, line

    # Initialise no additional information
    additional = None

    # Add explicit nominal type
    if attribute_type.startswith('{'):
        additional = parse_nominal_values(attribute_type)
        attribute_type = constants.NOMINAL_ATTRIBUTE_KEYWORD

    # Lower-case the type
    attribute_type = attribute_type.lower()

    # Keep the date format string as additional
    if attribute_type == constants.DATE_ATTRIBUTE_KEYWORD:
        additional, line = consume(line, DATE_FORMAT_PATTERN)
    # Normalise numeric types
    elif attribute_type == constants.REAL_ATTRIBUTE_KEYWORD or \
            attribute_type == constants.INTEGER_ATTRIBUTE_KEYWORD:
        additional = attribute_type
        attribute_type = constants.NUMERIC_ATTRIBUTE_KEYWORD

    # Return the type information and the rest of the line
    return attribute_type, (additional,) if additional is not None else tuple(), line


def parse_nominal_values(string: str) -> List[str]:
    """
    Parses the string of nominal values into a Python list.

    :param string:  The string specification of nominal values (including braces).
    :return:        The list of nominal values.
    """

    # Save the original string for error messages
    original_string = string

    # Create the list
    values = []

    # Remove the leading brace
    string = string[1:]

    # Keep reading values until all are consumed
    while string != '}':
        # Remove any leading whitespace
        string = string.lstrip()

        # Get the name of the next value
        value, string = consume(string, NOMINAL_VALUE_PATTERN)

        # Make sure a value was found
        if value is None:
            raise NominalValuesError(original_string)

        # Put it in the list
        values.append(remove_quotes(value))

        # Remove any trailing whitespace after the value
        string = string.lstrip()

        # Remove the next delimiter
        if string[0] == ',':
            string = string[1:]
        elif string[0] != '}':
            raise NominalValuesError(original_string)

    # Return the list
    return values


# Create a lookup table between type-strings and Attribute classes
type_string_lookup: TwoWayDict[str, Type[Attribute]] = TwoWayDict[str, Type[Attribute]]()
for attribute_class in {NumericAttribute, NominalAttribute, StringAttribute, DateAttribute}:
    type_string_lookup[attribute_class] = attribute_class.type_string()


class InvalidNominalValueError(ARFFError):
    """
    Exception for when a nominal data value isn't one of the pre-specified
    values from the attribute declaration.
    """
    def __init__(self, value_string: str, attribute: NominalAttribute):
        super().__init__('Illegal nominal value for attribute \'' + attribute.name + '\': ' + value_string + '\n' +
                         'Allowed values are: ' + ', '.join(attribute.ordered_values()))


class AttributeNameNotFoundError(ARFFError):
    """
    Exception when a name for an attribute cannot be parsed.
    """
    def __init__(self, line: str):
        super().__init__("Couldn't parse attribute name from: " + line)


class AttributeTypeNotFoundError(ARFFError):
    """
    Exception for when an attribute's type cannot be determined.
    """
    def __init__(self, line: str):
        super().__init__("Couldn't determine attribute type from: " + line)


class NominalValuesError(ARFFError):
    """
    Exception for when the set of nominal values can't be parsed.
    """
    def __init__(self, string: str):
        super().__init__("Error parsing nominal values from: " + string)


class InvalidNumericSubTypeError(ARFFError):
    """
    Exception for using an invalid string as the sub-type of a numeric attribute.
    """
    def __init__(self, sub_type: str):
        super().__init__("'" + sub_type + "' is not a valid numeric sub-type.\n" +
                         "Allowed sub-types are: " + ", ".join((constants.REAL_ATTRIBUTE_KEYWORD,
                                                                constants.INTEGER_ATTRIBUTE_KEYWORD)))


class InvalidValueTypeError(ARFFError):
    """
    Exception for when a value can't be parsed into a value of the correct
    type for an attribute.
    """
    def __init__(self, value, attribute: Attribute):
        super().__init__("Attribute '" + attribute.name + "' of type '" + attribute.type_string() + "' can't " +
                         "convert value '" + str(value) + "' of type '" + str(value.__class__) + "'")

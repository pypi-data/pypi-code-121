from typing import Optional, Tuple

# Datatypes
DATATYPE_STRING = 'S'
DATATYPE_NUMERIC = 'N'
DATATYPE_BOOLEAN = 'B'
DATATYPE_UNKNOWN = 'U'

# Separator between parts of a compound name
SEPARATOR = '\t'


class Field:
    """
    Class representing a report field. Has a name and a datatype.
    Can be a compound name, where the prefix and suffix parts of
    the name are separated by a tab.
    """
    def __init__(self, name, datatype=DATATYPE_UNKNOWN):
        # Placeholders for computed properties
        self.prefix: Optional[str] = None
        self.suffix: Optional[str] = None

        self.name: str = name
        self.datatype: str = datatype

    def value_of(self, value: str):
        """
        Converts a string into a value of the correct type for
        this field.

        :param value:   The string value to convert.
        :return:        The typed value.
        """
        if self.datatype == DATATYPE_STRING:
            return fix_string(value)
        elif self.datatype == DATATYPE_BOOLEAN:
            return bool(value)
        elif self.datatype == DATATYPE_NUMERIC:
            return float(value)
        else:
            raise ValueError('Cannot convert value as field type is unknown')

    def __setattr__(self, key, value):
        # Validation of datatype
        if key == 'datatype' and not is_valid_datatype(value):
            raise ValueError('datatype must be S, N, B or U')

        super().__setattr__(key, value)

    def __getattribute__(self, item):
        # Lazy calculation of prefix/suffix
        if item == 'prefix' or item == 'suffix':
            self.prefix, self.suffix = split_name(self.name)

        return super().__getattribute__(item)


def split_name(name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Splits a compound name into its prefix and suffix parts.

    :param name:    TODO
    :return:        TODO
    """
    # If there's no separator, it's not a compound name
    if SEPARATOR not in name:
        return None, None

    # Split around the tab character
    split = name.split(SEPARATOR, 1)

    prefix = split[0]
    suffix = split[1]

    return prefix, suffix


def is_valid_datatype(datatype: str) -> bool:
    """
    Checks if the given datatype string is one of the
    allowable values.

    :param datatype:    The datatype string to check.
    :return:            True if the datatype string is valid,
                        False if not.
    """
    return datatype in {DATATYPE_STRING,
                        DATATYPE_NUMERIC,
                        DATATYPE_BOOLEAN,
                        DATATYPE_UNKNOWN}


def fix_string(string: str) -> str:
    """
    Replaces apostrophes with back-ticks.

    :param string:  The string to fix.
    :return:        The fixed string.
    """
    return string.replace("'", "`")

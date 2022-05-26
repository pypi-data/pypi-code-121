from enum import Enum, IntEnum


class PortType(Enum):
    """Enumeration for the port type.

    A `Port` can be either `IN` or `OUT` depending if its variables are needed for calculating the
    `System` (`IN`) or results of the calculation (`OUT`).
    """

    IN = "in"
    OUT = "out"


class Scope(IntEnum):
    """Enumeration of variable scope."""

    PRIVATE = 1
    PROTECTED = 0
    PUBLIC = -1


class Validity(IntEnum):
    """Enumeration for the validity of a variable value.
    
    A valid variable value is `OK`.
    If the value is outside the limits, status is `ERROR`.
    If the value falls between the validity range and the limits, status is `WARNING`.
    """
    ERROR = -1
    WARNING = 0
    OK = 1


class RangeType(IntEnum):
    """Enumeration for the type of valid_range and limit of variable.
    
    If the value is a (lower, upper) tuple, type is `VALUE`.
    If the value is a tuple of tuples, type is `TUPLE`.
    Tf the value is None, type is `NONE`.
    """
    NONE = 0
    VALUE = 1
    TUPLE = 2


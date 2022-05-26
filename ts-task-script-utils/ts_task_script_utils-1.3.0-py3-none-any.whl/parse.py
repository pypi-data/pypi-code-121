"""A collection of useful functions to parse raw values into a more useable form."""
import math
from collections import defaultdict

from decimal import Decimal, InvalidOperation
from typing import DefaultDict, Optional, Set


def to_int(value: str) -> Optional[int]:
    """
    Converts given value to its equivalent integer.

    :param value: A string to convert
    :return: The int value of the input string or None if the string could not be parsed to int
    """

    if "_" in value:
        return None
    if "e" in value.lower() or "." in value:
        try:
            float_val = float(value)
            int_val = int(float_val)
            if int_val == float_val:
                return int_val
            return None
        except ValueError:
            return None
    try:
        return int(value)
    except ValueError:
        return None


def to_float(value: str) -> Optional[float]:
    """
    Converts given value to its equivalent float.

    :param value: A string to convert
    :return: The float value of the input string. None if the string could not be parsed to float
    """
    if "_" in value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def to_decimal(value: str) -> Optional[Decimal]:
    """
    Converts the given value to its equivalent python Decimal type

    :param value: The value to convert
    :return: The decimal value of the input string.  None if the string could not be converted to Decimal
    """
    if "_" in value:
        return None

    if value.lower() in ("infinity", "-infinity"):
        return None

    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def to_boolean(
    value: str, true_set: Set[str], false_set: Set[str], case_sensitive: bool = False
) -> Optional[bool]:
    """
    Convert given string to a boolean value based on whether it is in either of the sets provided

    :param value: A string to convert
    :param true_set: A set of strings which represent True values
    :param false_set: A set of strings which represent False values

    :return: The boolean value of the input string or None if the string could not be parsed to boolean
    :raises ValueError: If the sets overlap or if either set is empty
    """
    if not true_set or not false_set:
        raise ValueError(
            f"The set of 'true' values and 'false' values cannot be empty. "
            f"true_set: ({', '.join(true_set)}). "
            f"false_set: ({', '.join(true_set)})"
        )

    if not case_sensitive:

        def to_lowercase(string):
            return string.casefold()

    else:

        def to_lowercase(string):
            return string

    # Map original values to the lowercase'd version. If there are values in common
    # between true_set and false_set, we can recover the original values and display
    # them in an error message.
    true_set_compare: DefaultDict[str, Set[str]] = defaultdict(set)
    for original_value in true_set:
        lowercase_value = to_lowercase(original_value)
        true_set_compare[lowercase_value].add(original_value)
    false_set_compare: DefaultDict[str, Set[str]] = defaultdict(set)
    for original_value in false_set:
        lowercase_value = to_lowercase(original_value)
        false_set_compare[lowercase_value].add(lowercase_value)

    true_and_false_intersection = set(true_set_compare) & set(false_set_compare)
    if true_and_false_intersection:
        true_intersection: Set[str] = set()
        for value in true_and_false_intersection:
            true_intersection.update(true_set_compare[value])
        false_intersection: Set[str] = set()
        for value in true_and_false_intersection:
            false_intersection.update(false_set_compare[value])

        raise ValueError(
            f"'true_set' and 'false_set' have values in common. "
            f"true_set: ({', '.join(true_intersection)}). "
            f"false_set: ({', '.join(false_intersection)})."
        )

    value_compare = to_lowercase(value.strip())
    if value_compare in true_set_compare:
        return True
    if value_compare in false_set_compare:
        return False
    return None

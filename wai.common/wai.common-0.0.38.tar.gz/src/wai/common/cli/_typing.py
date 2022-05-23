"""
Module containing types to do with option parsing.
"""
from typing import List, Any

# The type of a list of options
OptionsList = List[str]


def is_options_list(options_list: Any) -> bool:
    """
    Checks whether the given value is an options list.

    :param options_list:    The value to check.
    :return:                True if it is an options list.
    """
    return (
        isinstance(options_list, list) and
        all(isinstance(element, str) for element in options_list)
    )

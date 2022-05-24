"""
Module for utilities for dealing with flags.
"""
from typing import Optional

from ..constants import SHORT_FLAG_PREFIX, LONG_FLAG_PREFIX


def is_flag(flag: str) -> bool:
    """
    Checks if the given string is a valid short/long flag.

    :param flag:    The string to check.
    :return:        True if it is a valid flag,
                    False if not.
    """
    return is_short_flag(flag) or is_long_flag(flag)


def is_flag_reason(flag: str) -> Optional[str]:
    """
    Checks if the given string is a valid flag.

    :param flag:    The string to check.
    :return:        None if it is a valid short flag,
                    or the reason if not.
    """
    short_flag_reason = is_short_flag_reason(flag)

    if short_flag_reason is None:
        return None

    long_flag_reason = is_long_flag_reason(flag)

    if long_flag_reason is None:
        return None

    return (f"Not a short flag because: {short_flag_reason}\n"
            f"Not a long flag because: {long_flag_reason}")


def is_short_flag(flag: str) -> bool:
    """
    Checks if the given string is a valid short flag.

    :param flag:    The string to check.
    :return:        True if it is a valid short flag,
                    False if not.
    """
    return is_short_flag_reason(flag) is None


def is_short_flag_reason(flag: str) -> Optional[str]:
    """
    Checks if the given string is a valid short flag.

    :param flag:    The string to check.
    :return:        None if it is a valid short flag,
                    or the reason if not.
    """
    # Short flags must start with '-'
    if not flag.startswith(SHORT_FLAG_PREFIX):
        return f"'{flag}' does not start with '{SHORT_FLAG_PREFIX}'"

    # Must be exactly 2 characters
    if len(flag) > 2:
        return f"'{flag}' is too long (can only be one character after {SHORT_FLAG_PREFIX})"
    elif len(flag) < 2:
        return f"'{flag}' is too short (must be a single letter after {SHORT_FLAG_PREFIX})"

    # The flag character must be a letter
    if not flag[1].isalpha():
        return f"Flag character must be a letter (got '{flag[1]}')"

    return None


def is_long_flag(flag: str) -> bool:
    """
    Checks if the given string is a valid long flag.

    :param flag:    The string to check.
    :return:        True if it is a valid long flag,
                    False if not.
    """
    return is_long_flag_reason(flag) is None


def is_long_flag_reason(flag: str) -> Optional[str]:
    """
    Checks if the given string is a valid long flag.

    :param flag:    The string to check.
    :return:        None if it is a valid long flag,
                    or the reason if not.
    """
    # Long flags must start with '--'
    if not flag.startswith(LONG_FLAG_PREFIX):
        return f"'{flag}' does not start with {LONG_FLAG_PREFIX}"

    # Must have at least 3 characters ('--' followed by at least 1 letter)
    if len(flag) < 3:
        return f"'{flag}' requires at least one character after {LONG_FLAG_PREFIX}"

    # The character after '--' must be a letter
    if not flag[2].isalpha():
        return f"First character after {LONG_FLAG_PREFIX} must be a letter"

    # All other characters must be alpha-numeric or '-'
    if not flag.replace('-', '').isalnum():
        return "All characters must be '-' or alpha-numeric"

    return None


def flag_from_name(name: str) -> str:
    """
    Creates a flag from the given name.

    :param name:    The name, which must be a valid identifier.
    :return:        A flag similar to the name.
    """
    # Name must be an identifier
    if not name.isidentifier() or name.startswith("_"):
        raise ValueError(f"Name ({name}) must be an identifier not starting with an underscore")

    # Create a short flag from single-character names
    if len(name) == 1:
        return SHORT_FLAG_PREFIX + name

    return f"--{name.replace('_', '-')}"

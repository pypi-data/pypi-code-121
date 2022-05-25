"""Contains utility functions for working with expressions"""

import json
from typing import Any, Sequence


def escape_identifier(s: str) -> str:
    """Escape a SAQL identifier

    Args:
        s: Input string

    Returns:
        escaped identifier

    """
    return "'" + s.replace("'", "\\'") + "'"


def escape_string(s: str) -> str:
    """Escape a SAQL string literal

    Args:
        s: Input string

    Returns:
        escaped string

    """
    return '"' + s.replace('"', '\\"') + '"'


def stringify(obj: Any) -> str:
    """Cast an object into a SAQL string

    This handles internal objects as well as literals.

    Args:
        obj: Object to cast

    Returns:
        stringified object

    """
    if hasattr(obj, "to_string"):
        return obj.to_string()
    elif isinstance(obj, (str, int, float, list, tuple, type(None))):
        return json.dumps(obj)
    else:
        return obj


def stringify_list(seq: Sequence) -> str:
    """Cast a list into a string

    This will separate list items with commas and wrap the output in parenthesis if
    there is more than one item.

    Args:
        seq: Sequence to cast

    Returns:
        stringified list

    """
    seq = [seq] if not isinstance(seq, (list, tuple, set)) else seq
    return f"({', '.join(str(s) for s in seq)})" if len(seq) > 1 else str(seq[0])


def flatten(seq: list) -> list:
    """Recursively flatten a list

    Args:
        seq: Sequence of items

    Returns:
        flatten list of items

    """
    if not seq:
        return seq
    if isinstance(seq[0], list):
        return flatten(seq[0]) + flatten(seq[1:])
    return seq[:1] + flatten(seq[1:])

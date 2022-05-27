"""References and constants for transformations.

Contains regular expressions and methods for matching transformation and
column references.
"""
import re
from typing import cast

from bitfount.transformations.exceptions import (
    IncorrectReferenceError,
    NotColumnReferenceError,
    NotTransformationReferenceError,
)

_TRANSFORMATION_REFERENCE = re.compile("(?:t|tran|transformation):(.*)", re.IGNORECASE)
_COLUMN_REFERENCE = re.compile("(?:c|col|column):(.*)", re.IGNORECASE)


def _extract_ref_regex(s: str, ref_regex: re.Pattern) -> str:
    """Extracts a reference based on a pattern.

    Args:
        s: The potential reference.
        ref_regex: The regex pattern to match against.

    Returns:
        The name being referenced.

    Raises:
        IncorrectReferenceError:
            If no reference was found according to the pattern.
        TypeError:
            If `s` type cannot be matched.
    """
    match = ref_regex.fullmatch(s)
    if match:
        return cast(str, match.group(1))
    else:
        raise IncorrectReferenceError


def _extract_transformation_ref(t_str: str) -> str:
    """Extracts the transformation name being referenced if possible.

    Args:
        t_str: The potential transformation reference.

    Returns:
        The name of the transformation being referenced.

    Raises:
        NotTransformationReferenceError:
            Raised if this is not a transformation reference by type or
            content.
    """
    try:
        return _extract_ref_regex(t_str, _TRANSFORMATION_REFERENCE)
    except IncorrectReferenceError:
        raise NotTransformationReferenceError(
            "Incorrect format for transformation reference; transformation references"
            'should start with "t:", "tran:" or "transformation:"'
        )
    except TypeError:
        raise NotTransformationReferenceError(
            f"Incorrect type for transformation reference; "
            f"expected str, got {type(t_str)}"
        )


def _extract_col_ref(col_str: str) -> str:
    """Extracts the column name being referenced if possible.

    Args:
        col_str: The potential column reference.

    Returns:
        The name of the column being referenced.

    Raises:
        NotColumnReferenceError:
            Raised if this is not a column reference by type or content.
    """
    try:
        return _extract_ref_regex(col_str, _COLUMN_REFERENCE)
    except IncorrectReferenceError:
        raise NotColumnReferenceError(
            "Incorrect format for column reference; column references should "
            'start with "c:", "col:" or "column:"'
        )
    except TypeError:
        raise NotColumnReferenceError(
            f"Incorrect type for column reference; expected str, got {type(col_str)}"
        )


def _extract_ref(r_str: str) -> str:
    """Extracts the column or transformation name being referenced if possible.

    Args:
        r_str: The potential column or transformation reference.

    Returns:
        The name of the column or transformation being referenced.

    Raises:
        IncorrectReferenceError:
            Raised if this is not a column or transformation reference by type
            or content.
    """
    # Try transformation reference first
    try:
        return _extract_transformation_ref(r_str)
    except NotTransformationReferenceError:
        pass
    # Otherwise try column reference
    try:
        return _extract_col_ref(r_str)
    except NotColumnReferenceError:
        pass
    raise IncorrectReferenceError(
        "Argument is not a transformation or column reference."
    )

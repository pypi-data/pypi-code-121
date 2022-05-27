#
# Copyright 2021 Simple Machines Pty Ltd - All Rights Reserved.
#
# This file is part of Anaml.
#
# Unauthorized copying and/or distribution of this file, via any medium is
# strictly prohibited.
#
"""Utility functions, mostly for internal use."""

from datetime import datetime, timezone
from typing import Callable, Optional, TypeVar

from .serialisation import INSTANT_FORMAT


def parse_bool(t: str) -> bool:
    """Parse case insensitive "true" and "false" strings to bool."""
    if isinstance(t, bool):
        return t
    elif isinstance(t, str):
        s = t.lower()
        if s == "true":
            return True
        elif s == "false":
            return False
    else:
        raise ValueError(f"Invalid boolean value: {t}")


def parse_instant(t: str) -> datetime:
    """Parse a Scala Instant to a datetime."""
    dt_from_str = datetime.strptime(t, INSTANT_FORMAT)
    dt_from_str = dt_from_str.replace(tzinfo=timezone.utc)
    return dt_from_str


def parse_instant_optional(t: Optional[str]) -> Optional[datetime]:
    """Parse an optional Scala Instant to an optional datetime."""
    if t is None:
        return None
    return parse_instant(t)


_X = TypeVar('_X')
_Y = TypeVar('_Y')


def map_opt(o: Optional[_X], f: Callable[[_X], _Y]) -> Optional[_Y]:
    """If a value is non-None, apply the function to it."""
    return f(o) if o is not None else None

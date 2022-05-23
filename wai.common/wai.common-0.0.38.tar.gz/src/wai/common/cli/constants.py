"""
Module for constant values related to CLI functionality.
"""
from typing import Set as _Set

# The quote characters
QUOTES: _Set[str] = {"'", '"'}

# The prefix characters for a short flag
SHORT_FLAG_PREFIX: str = '-'

# The prefix characters for a long flag
LONG_FLAG_PREFIX: str = '--'

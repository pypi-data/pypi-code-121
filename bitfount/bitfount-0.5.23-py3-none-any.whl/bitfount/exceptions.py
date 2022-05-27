"""Custom exceptions for the Bitfount codebase."""
from typing import List

__all__: List[str] = [
    "BitfountEngineError",
    "BitfountError",
]


class BitfountError(Exception):
    """Base exception class that all others should inherit from."""

    pass


class BitfountEngineError(BitfountError):
    """Exception for any issues relating to the backend engine."""

    pass

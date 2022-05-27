"""Exceptions related to the transformations package."""
from typing import List, Union

from bitfount.exceptions import BitfountError


class _BitfountTransformationsError(BitfountError):
    """Base class for transformations errors."""


class TransformationRegistryError(_BitfountTransformationsError):
    """Exceptions related to the Transformations registry."""

    pass


class TransformationParsingError(_BitfountTransformationsError):
    """Base exception for transformation parsing."""

    def __init__(self, errors: Union[str, List[str]]):
        """Initialises TransformationParsingError with 1+ error messages.

        Args:
            errors: The parsing error(s) that have occurred.
        """
        if isinstance(errors, str):
            errors = [errors]
        self.errors = errors

    def __str__(self) -> str:
        str_errors = "\n".join(self.errors)
        return f"Errors: \n{str_errors}"


class TransformationProcessorError(_BitfountTransformationsError):
    """Base class for all errors related to transformation processing."""

    def __init__(self, errors: Union[str, List[str]]):
        """Initialises TransformationProcessorError with 1+ error messages.

        Args:
            errors: The parsing error(s) that have occurred.
        """
        if isinstance(errors, str):
            errors = [errors]
        self.errors = errors

    def __str__(self) -> str:
        str_errors = "\n".join(self.errors)
        return f"Errors: \n{str_errors}"


class MissingColumnReferenceError(TransformationProcessorError):
    """Exception for when a column is referenced that doesn't exist."""

    pass


class InvalidBatchTransformationError(TransformationProcessorError):
    """Exception for when a non-batch transformation is attempted with a batch."""

    pass


class TransformationApplicationError(TransformationProcessorError):
    """Exception for when applying the transformation to the data is impossible."""

    pass


class IncorrectReferenceError(_BitfountTransformationsError):
    """Raised when a str is not a column or transformation reference."""

    pass


class NotTransformationReferenceError(IncorrectReferenceError):
    """Raised when a str is not a transformation reference."""

    pass


class NotColumnReferenceError(IncorrectReferenceError):
    """Raised when a str is not a column reference."""

    pass

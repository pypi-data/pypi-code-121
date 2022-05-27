"""Custom exceptions for the data package."""
from bitfount.exceptions import BitfountError


class BitfountSchemaError(BitfountError):
    """Errors related to BitfountSchema."""

    pass


class DataStructureError(BitfountError):
    """Errors related to Datastructure."""

    pass


class DatasetSplitterError(BitfountError):
    """Errors related to DatasetSplitter."""

    pass


class DatabaseSchemaNotFoundError(BitfountError):
    """Raised when a specified database schema is not found."""

    pass


class DatabaseMissingTableError(BitfountError):
    """Raised when a specified database table is not found."""

    pass


class DatabaseUnsupportedQueryError(BitfountError):
    """Raised when an unsupported database query is provided."""

    pass


class DataNotLoadedError(BitfountError):
    """Raised if a data operation is attempted prior to data loading.

    This is usually raised because `load_data` has not been called yet.
    """

    pass


class DuplicateColumnError(BitfountError):
    """Raised if the column names are duplicated in the data.

    This can be raised by the sql algorithms with multi-table pods.
    """

    pass

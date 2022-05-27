# -*- coding: UTF-8 -*-

class BaseVaultError(Exception):
    """Base exception class for backends module."""


class PasswordGetError(BaseVaultError):
    """Exception for password getter."""


class BaseLockException(Exception):
    """Base exception class."""

    # Error codes:
    LOCK_FAILED = 1

    def __init__(self, *args, **kwargs):
        self.handle = kwargs.pop("handle")
        super(BaseLockException, self).__init__(*args)


class LockException(BaseLockException):
    """Lock exception."""


class BaseConfigError(Exception):
    """Base exception for all configuration errors."""


class BadParameterError(BaseConfigError):
    """Exception class used to signal parameters parsing errors."""


class DatabaseError(Exception):
    """Base class for all database related exceptions."""


class MissingColumnsError(DatabaseError):
    """Exception class raised for missing table columns."""


class MissingEngineError(DatabaseError):
    """Exception class raised for missing SQL engine."""


class ArgumentError(DatabaseError):
    """Exception class raised for argument related errors."""


class SqlExecutionError(DatabaseError):
    """Exception raised for missing execution method."""

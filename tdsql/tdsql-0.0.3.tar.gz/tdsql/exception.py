class InvalidInputError(Exception):
    """Raised when sql or yaml file has a problem"""


class TdsqlAssertionError(Exception):
    """Raised when actual result and expected result do not match"""


class TdsqlInternalError(Exception):
    """Raised when unnexpected error is detected"""

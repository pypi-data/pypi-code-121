"""The exceptions used by lupulib."""

class LupusecError(Exception):
    """Base error class for all pyavanza errors."""


class LupusecRequestError(LupusecError):
    """Raised when there is a request error."""


class LupusecResponseError(LupusecError):
    """Raised when there is a response error."""


class LupusecParseError(LupusecError):
    """Raised when there is a parse error."""

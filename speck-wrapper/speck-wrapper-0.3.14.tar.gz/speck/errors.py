"""
All exceptions that can be raised during handling of a weatherapi request.
"""

# Functions that make a request to weatherapi.com have the possibility
# of raising one of these errors depending on the response.
# We use these custom error classes to make the error code more readable
# and easier to handle.

__all__ = [
    'WeatherApiError',
    'NoApiKey',
    'InvalidApiKey',
    'QuotaExceeded',
    'ApiKeyDisabled',
    'QueryNotProvided',
    'InvalidRequestUrl',
    'InvalidLocation',
    'InternalError'
]

class WeatherApiError(Exception):
    """
    Raised when an unknown weatherapi error is encountered.

    :var internal_code: :class:`int`
        The error code returned by weatherapi.
    :var message: :class:`str`
        A more detailed description of the error.
    """

    def __init__(self, message, internal_code):
        self.internal_code = internal_code
        self.message = message
        super().__init__(message)

class NoApiKey(WeatherApiError):
    """Raised when no weatherapi key has been provided in a request."""

class InvalidApiKey(WeatherApiError):
    """Raised when an invalid weatherapi key has been used for a request."""

class QuotaExceeded(WeatherApiError):
    """Raised when monthly requests limit has been reached."""

class ApiKeyDisabled(WeatherApiError):
    """Raised when weatherapi key used for a request has been disabled."""

class QueryNotProvided(WeatherApiError):
    """Raised when a query parameter has not been provided for a request."""

class InvalidRequestUrl(WeatherApiError):
    """Raised when weatherapi request url is invalid."""

class InvalidLocation(WeatherApiError):
    """Raised when location request is not found."""

class InternalError(WeatherApiError):
    """Raised when an internal weatherapi error is encountered."""

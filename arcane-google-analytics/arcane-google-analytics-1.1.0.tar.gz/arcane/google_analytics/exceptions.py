
import socket

from arcane.core import GOOGLE_EXCEPTIONS_TO_RETRY

from http.client import HTTPException
from urllib.error import HTTPError, ContentTooShortError

class GoogleAnalyticsAccountLostAccessException(Exception):
    """ Raised when we cannot access to an account """
    pass

class GoogleAnalyticsServiceDownException(Exception):
    """ Raised when we cannot access to an account """
    pass


GA_EXCEPTIONS_TO_RETRY = GOOGLE_EXCEPTIONS_TO_RETRY + (
    socket.timeout,
    HTTPException,
    HTTPError,
    NotImplementedError,
    ContentTooShortError
)

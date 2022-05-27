class IOPoolError(Exception):
    """Base class for IOPool errors"""

class WrongApiKeyError(IOPoolError):
    """Raised when the API key is wrong"""

class BadCheckOrAction(Exception):
    """
    Generic exception for a badly written check or library.
    __init__ takes some string error message
    """
    def __init__(self, message=None):
        # default error message if none provided
        if message is None:
            message = "Check or action function seems to be malformed."
        super().__init__(message)


class BadCheckSetup(Exception):
    """
    Generic exception for an issue with a check setup.
    __init__ takes some string error message
    """
    def __init__(self, message=None):
        # default error message if none provided
        if message is None:
            message = "Malformed check setup found."
        super().__init__(message)


class MissingFoursightPrefixException(Exception):
    """
    Generic exception for an issue with foursight prefix
    not defined or initialized before using a method that
    requires it.
    __init__ takes some string error message
    """
    def __init__(self, message=None):
        # default error message if none provided
        if message is None:
            message = "Foursight prefix is missing."
        super().__init__(message)

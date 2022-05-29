class NotValidDirectoryError(Exception):
    """Raise exception when directory doesn't exist

    Arguments:
    ----
    Exception (Exception): The base python exception class
    """

    def __init__(self, message):
        """Print out message for this exception.

        Arguments:
        ----
        message (str): Pass in the message returned by the server.
        """
        self.message = message
        super().__init__(self.message)


class NotEqualLengthError(Exception):
    """Raise exception when two lists doesn't have the same length

    Arguments:
    ----
    Exception (Exception): The base python exception class
    """

    def __init__(self, message):
        """Print out message for this exception.

        Arguments:
        ----
        message (str): Pass in the message returned by the server.
        """
        self.message = message
        super().__init__(self.message)


class NotValidArgumentError(Exception):
    """Raise exception when arguments passed are not valid

    Arguments:
    ----
    Exception (Exception): The base python exception class
    """

    def __init__(self, message):
        """Print out message for this exception.

        Arguments:
        ----
        message (str): Pass in the message returned by the server.
        """
        self.message = message
        super().__init__(self.message)


class MissingFilename(Exception):
    """Raise exception when filename is passed as empty string

    Arguments:
    ----
    Exception (Exception): The base python exception class
    """

    def __init__(self, message):
        """Print out message for this exception.

        Arguments:
        ----
        message (str): Pass in the message returned by the server.
        """
        self.message = message
        super().__init__(self.message)

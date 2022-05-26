"""Port exceptions"""

class ScopeError(Exception):
    """Raised if an port variable out of user scope is set.

    Parameters
    ----------
    message : str
        Error message

    Attributes
    ----------
    message : str
        Error message
    """

    def __init__(self, message: str):
        """Instantiate a error object from the error descriptive message.

        Parameters
        ----------
        message : str
            Error message
        """
        self.message = message

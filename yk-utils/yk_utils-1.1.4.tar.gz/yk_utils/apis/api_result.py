"""API result module"""


class ApiResult:
    """This class stores data from API operations."""
    def __init__(self, status: str = None, message_class: str = None, message: str = None):
        """Class initializer.
        :param status:
            Status.
        :param message_class:
            Message class (for UI purposes).
        :param message:
            Result message.
        """
        self.status = status
        self.message_class = message_class
        self.message = message

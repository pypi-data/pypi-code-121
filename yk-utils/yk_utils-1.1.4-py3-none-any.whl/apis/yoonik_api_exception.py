"""YoonikApiException module
"""


class YoonikApiException(Exception):
    """Custom Exception for the YooniK APIs."""
    def __init__(self, status_code: int, message: str):
        """ Class initializer.
        :param status_code: HTTP response status code.
        :param message: Error message.
        """
        super().__init__()
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return 'Error when calling YooniK API:\n' + \
            f'\tstatus_code: {self.status_code}\n' + \
            f'\tmessage: {self.message}\n'

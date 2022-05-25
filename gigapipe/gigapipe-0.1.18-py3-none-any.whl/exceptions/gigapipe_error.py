class GigapipeError(Exception):
    """
    Gigapipe Generic Errors
    """
    def __init__(self, status_code: int, message: str):
        super(GigapipeError, self).__init__(message)
        self.status_code = status_code
        self.message = message


class GigapipeServerError(GigapipeError):
    """
    Gigapipe Server (5xx Errors)
    """
    pass


class GigapipeClientError(GigapipeError):
    """
    Invalid input (4xx errors)
    """
    pass

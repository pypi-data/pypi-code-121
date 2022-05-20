from typing import Any


class UnauthenticatedApiAccessError(RuntimeError):
    """ Raised when the access to the API requires an authentication. """

    def __init__(self, message: str):
        super(UnauthenticatedApiAccessError, self).__init__(f'Unauthenticated Access: {message}')


class UnauthorizedApiAccessError(RuntimeError):
    """ Raised when the access to the API is denied. """

    def __init__(self, message: str):
        super(UnauthorizedApiAccessError, self).__init__(f'Unauthorized Access: {message}')


class MissingResourceError(RuntimeError):
    """ Raised when the requested resource is not found. """


class ServerApiError(RuntimeError):
    """ Raised when the server response """


class ApiError(RuntimeError):
    """ Raised when the server responds an error for unexpected reason. """

    def __init__(self, url: str, response_status: int, response_body: Any):
        super(ApiError, self).__init__(f'HTTP {response_status} from {url}: {response_body}')

        self.__url = url
        self.__status = response_status
        self.__details = response_body

    @property
    def url(self):
        return self.__url

    @property
    def status(self):
        return self.__status

    @property
    def details(self):
        return self.__details

class VgsApiException(Exception):
    def __init__(
        self,
        message=None,
    ):
        super(VgsApiException, self).__init__(message)

        self._message = message

    def __str__(self):
        return self._message or "<empty message>"


class UnauthorizedException(VgsApiException):
    pass


class NotFoundException(VgsApiException):
    pass


class ForbiddenException(VgsApiException):
    pass

__all__ = ["RequestException", "BadRequest", "NotFound", "NotAuthorized"]


class RequestException(Exception):
    pass


class BadRequest(RequestException):
    pass


class NotFound(RequestException):
    pass


class UnexpectedError(RequestException):
    pass


class NotAuthorized(RequestException):
    pass

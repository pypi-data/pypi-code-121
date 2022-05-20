import json

import requests


class HTTPError(Exception):
    """Base of all other errors"""

    def __init__(self, error: requests.HTTPError):
        response = error.response
        self.status_code = error.response.status_code
        self.reason = response.reason
        self.body = response.content
        self.headers = response.headers

    def __reduce__(self):
        return (HTTPError, (self.status_code, self.reason, self.body, self.headers))

    @property
    def to_dict(self):
        """
        :return: dict of response error from the API
        """
        return json.loads(self.body.decode('utf-8'))


class BadRequestsError(HTTPError):
    pass


class UnauthorizedError(HTTPError):
    pass


class ForbiddenError(HTTPError):
    pass


class NotFoundError(HTTPError):
    pass


class MethodNotAllowedError(HTTPError):
    pass


class PayloadTooLargeError(HTTPError):
    pass


class UnsupportedMediaTypeError(HTTPError):
    pass


class TooManyRequestsError(HTTPError):
    pass


class InternalServerError(HTTPError):
    pass


class ServiceUnavailableError(HTTPError):
    pass


class GatewayTimeoutError(HTTPError):
    pass


err_dict = {
    400: BadRequestsError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    405: MethodNotAllowedError,
    413: PayloadTooLargeError,
    415: UnsupportedMediaTypeError,
    429: TooManyRequestsError,
    500: InternalServerError,
    503: ServiceUnavailableError,
    504: GatewayTimeoutError,
}


def handle_error(error: requests.HTTPError):
    try:
        status_code = error.response.status_code
        exc = err_dict[status_code](error)
    except KeyError:
        return HTTPError(error)
    return exc

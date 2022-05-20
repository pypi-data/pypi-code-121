from collections import namedtuple
from http import HTTPStatus
from typing import List, NamedTuple

from fiddler.libs.http_client.exceptions import HTTPError
from fiddler.utils import logging

logger = logging.getLogger(__name__)


class ErrorResponseHandler:
    def __init__(self, http_error: HTTPError) -> None:
        self.http_error = http_error
        self.ErrorResponse = namedtuple(
            'ErrorResponse', ['status_code', 'error_code', 'message', 'errors']
        )

    def get_error_details(self) -> NamedTuple:
        status_code = self.http_error.status_code
        error_details = self.http_error.to_dict.get('error', {})
        error_code = error_details.get('code')
        message = error_details.get('message')
        errors = error_details.get('errors')
        return self.ErrorResponse(status_code, error_code, message, errors)


class BaseException(Exception):
    pass


class FiddlerException(BaseException):
    '''
    Exception class to handle non API response exceptions
    '''


class FiddlerAPIException(BaseException):
    '''
    Exception class to specifically handle Fiddler's API error responses structure.
    This is a generic API response exception class
    '''

    # @TODO: Handle standard API error response.
    # How to surface error messages coming form the server. Server responds error messages in a list. Which error to surface?
    def __init__(
        self, status_code: int, error_code: int, message: str, errors: List[str]
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.errors = errors
        super().__init__(self.message)


class FiddlerAPIBadRequestException(FiddlerAPIException):
    pass


class FiddlerAPINotFoundException(FiddlerAPIException):
    pass


class FiddlerAPIForbiddenException(FiddlerAPIException):
    pass


class FiddlerAPIInternalServerErrorException(FiddlerAPIException):
    pass


map_except_resp_code = {
    HTTPStatus.BAD_REQUEST: FiddlerAPIBadRequestException,
    HTTPStatus.NOT_FOUND: FiddlerAPINotFoundException,
    HTTPStatus.FORBIDDEN: FiddlerAPIForbiddenException,
    HTTPStatus.INTERNAL_SERVER_ERROR: FiddlerAPIInternalServerErrorException,
}


def handle_api_error_response(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPError as error:
            logger.error(f'Error occured at {func.__name__}')
            error_response = ErrorResponseHandler(error).get_error_details()
            # raise status_code specific exceptions else raise generic FiddlerAPIException
            exec_class = map_except_resp_code.get(
                error_response.status_code, FiddlerAPIException
            )
            raise exec_class(
                error_response.status_code,
                error_response.error_code,
                error_response.message,
                error_response.errors,
            ) from None
            # disabling automatic exception chaining
            # ref: https://docs.python.org/3/tutorial/errors.html#exception-chaining

    return wrapper

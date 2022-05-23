import functools
from typing import Optional, List

from requests import Response

from api_manager.async_response.utils import ASYNC_COMMAND_IGNORE_CODES, async_response
from api_manager.constants import Entities


def lazy_request(entity: Entities, check_message: Optional[str] = None, ignore_codes: List[int] = None):
    """
    :param ignore_codes: List of status codes which will be ignored to check completion
    :param entity: Entity name
    :param check_message: Overrides default check message
    :return:

    Decorator which used for requests that are not returning
    response directly. Usually such response return 202 status code,
    this means request was "accepted" for processing but not
    completed yet. This decorator expects api return something like:
    {
        "id": <some_uuid>,
        "url": <url_where_we_should_check_status>,
        "message": <some_message>
    }
    Then decorator takes "url" param and checking it for completion and
    only after request completed, returns response.

    Example usage:

    @lazy_request(message='Some allure message', is_lazy=False)
    def my_async_request():
        ...
    """

    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            response: Response = func(*args, **kwargs)

            if response.status_code in (ignore_codes or ASYNC_COMMAND_IGNORE_CODES):
                return response

            if kwargs.get('is_lazy'):
                return response

            return async_response(response, entity, check_message, **kwargs)

        return wrapper

    return inner

import json
import logging
import re
from http import HTTPStatus
from typing import Optional

import allure
from requests import Response
from waiting import wait as wait_lib

from api_manager.constants import Entities, HttpActions, APIState
from api_manager.exceptions import NotConfiguredException
from api_manager.methods import get

ASYNC_COMMAND_IGNORE_CODES = [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN, HTTPStatus.INTERNAL_SERVER_ERROR]


def wait(*args, **kwargs):
    """
    Wrapping 'wait()' method of 'waiting' library with default parameter values.
    WebDriverException is ignored in the expected exceptions by default.
    """
    from api_manager.settings import WAIT_TIMEOUT

    if WAIT_TIMEOUT is None:
        raise NotConfiguredException('You should define "WAIT_TIMEOUT" setting in your settings file')

    kwargs.setdefault('sleep_seconds', (1, None))
    kwargs.setdefault('timeout_seconds', WAIT_TIMEOUT)

    return wait_lib(*args, **kwargs)


def parse_uuid_from_string(string: str) -> Optional[str]:
    """
    :param string: Any string
    :return: If string contains uuid, then return uuid else None

    Example:
        some_url = 'https://some.domain.com/api/v1/create-activities/fdee2394-2aec-4af7-bb97-a6bdab88c9e5'
        parse_uuid_from_string(some_url) -> 'fdee2394-2aec-4af7-bb97-a6bdab88c9e5'
    """
    result = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}', string)
    if result is None:
        return

    return result.group()


def get_request(url, message, user=None):
    """Wrapper to check lazy request"""
    from api_manager.settings import ALMS_USERS_API  # no qa

    if ALMS_USERS_API is None:
        raise NotConfiguredException('You should define "ALMS_USERS_API" setting in your settings file')

    with allure.step(message):
        return get(ALMS_USERS_API + url, user=user)


def async_response(response: Response, entity: Entities, check_message: Optional[str] = None, **kwargs) -> Response:
    """
    Wrapper around async request processing. Mostly to abstract autotest from this async logic
    and focus only on business logic.

    Flow:
    1. Creating entity and getting command endpoint
    {
        "id": "55c71154-bfcc-46c7-8747-50354bdcdd45",
        "url": "/api/v1/some-url/55c71154-bfcc-46c7-8747-50354bdcdd45", <- here
        "message": "Request accepted for processing"
    }
    2. Go to "/api/v1/some-url/55c71154-bfcc-46c7-8747-50354bdcdd45" and wait until command completed
    3. If command success, then will be following response
    {
        "id": "c5a0ad21-c157-47ba-9ad0-35925a4f3596",
        "entityId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "created": "2021-12-20T12:46:56.081087Z",
        "completed": {
            "url": "/api/v1/activities/3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "completed": "2021-12-20T12:46:56.104712Z",
            "state": 1,
            "errors": "null"
        }
    }
    4. Go to "/api/v1/activities/3fa85f64-5717-4562-b3fc-2c963f66afa6" and get created entity
    """
    url = response.json().get('url')

    # if no url returned in response then probable it is not async request
    if url is None:
        return response

    action = HttpActions[response.request.method].value  # action depends on request method
    safe_entity = Entities.to_human_readable(entity).lower()  # entity name to process

    wait_message = check_message or f'Checking while {safe_entity} successfully {action}'

    # ensure that we can check this command, if not, it makes no sense to go further
    command_response = get_request(url, wait_message, **kwargs)
    if command_response.status_code in ASYNC_COMMAND_IGNORE_CODES:
        return command_response

    # waiting for async command to be completed on the server
    wait(lambda: get_request(url, wait_message, **kwargs).json()['completed'], waiting_for=wait_message)

    # getting completed command response
    command_response = get_request(url, wait_message, **kwargs)

    try:
        command_response_json = command_response.json()
    except json.decoder.JSONDecodeError as error:
        # if we did not receive json then it makes no sense to go further
        logging.error(error)
        raise AssertionError(f'Unable to get json from {command_response.content}')

    # if command completion failed then it makes no sense to go further
    if command_response_json['completed']['state'] == APIState.FAILED.value:
        # returning failed response
        return command_response

    try:
        entity_url = command_response_json['completed']['url']
    except KeyError as error:
        # if we could not get url from completed, for example completed always null
        # then it makes no sense to go further
        logging.error(error)
        raise AssertionError(f'Async command not success. Unable to get entity url from {command_response_json}')

    entity_message = f'Getting {safe_entity} with id "{parse_uuid_from_string(entity_url)}"'
    entity = get_request(entity_url, entity_message, **kwargs)
    entity.request.method = response.request.method  # override to actual request method
    return entity

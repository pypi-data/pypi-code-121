import logging

import requests

from . import SETTINGS
from .exceptions import ServerError

logger = logging.getLogger(__name__)


def send_request(
        method,
        url,
        data=None,
        json=None,
        params=None,
        files=None,
        headers=None,
        expected_content_types=None,
        expected_error_statuses=None,
        timeout=None,
        **kwargs
):
    timeout = timeout or SETTINGS['DEFAULT_REQUEST_TIMEOUT']
    if isinstance(method, str):
        method = getattr(requests, method.lower())

    try:
        response = method(url, headers=headers, data=data, json=json, files=files, params=params, timeout=timeout,
                          **kwargs)
    except requests.Timeout:
        logger.exception('API call timed out')
        raise ServerError()

    check_response_for_errors(response, expected_content_types, expected_error_statuses)
    return response


def check_response_for_errors(
        response,
        expected_content_types=None,
        expected_error_statuses=None):

    expected_content_types = expected_content_types or ['application/json']
    if response.headers.get('content-type') not in expected_content_types:
        logger.error('Invalid content-type returned: {}'.format(response.headers.get('content-type')),
                     extra={
                         'url': response.url,
                         'status_code': response.status_code,
                         'request_body': response.request.body,
                     })
        raise ServerError()

    if response.status_code >= 400 and response.status_code not in (expected_error_statuses or []):
        logger.error('Unexpected status code returned: {}'.format(response.status_code),
                     extra={
                         'url': response.url,
                         'request_body': response.request.body,
                     })
        raise ServerError()

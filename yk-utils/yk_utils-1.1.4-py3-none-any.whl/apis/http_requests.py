"""HTTP requests module.
"""
import requests
from .key import Key
from .base_url import BaseUrl
from .yoonik_api_exception import YoonikApiException


def request(method: str, url: str, data=None, json: dict = None, headers: dict = None, params=None):
    # pylint: disable=too-many-arguments
    """ Universal interface for request."""
    json_content_type = 'application/json'

    url = BaseUrl.get() + url

    # Setup the headers with default Content-Type and Subscription Key.
    headers = headers or {}
    if 'Content-Type' not in headers and method != 'GET':
        headers['Content-Type'] = json_content_type
    api_key = Key.get()
    if api_key:
        headers['x-api-key'] = api_key

    response = requests.request(
        method,
        url,
        params=params,
        data=data,
        json=json,
        headers=headers)

    if not response.ok:
        raise YoonikApiException(response.status_code, response.text)

    if json_content_type in response.headers['Content-Type']:
        return response.json() if response.text else {}
    return response.text

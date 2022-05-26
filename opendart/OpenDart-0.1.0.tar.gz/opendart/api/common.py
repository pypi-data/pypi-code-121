from typing import TYPE_CHECKING
from requests import Response, get


if TYPE_CHECKING:
    from opendart.models.common import ApiParams


def __check_status_code(response: Response):
    if response.status_code != 200:
        raise Exception(response.status_code, response.reason)


def __check_status(result: dict):
    if result['status'] != '000':
        raise Exception(result['status'], result['message'])


def fetch(url: str, params: 'ApiParams') -> Response:
    response = get(url, params)
    __check_status_code(response)
    return response


def parse_json(response: Response) -> dict:
    result: dict = response.json()
    __check_status(result)
    result.pop('status')
    result.pop('message')
    return result

import json
from enum import Enum

from api_manager.settings import ALMS_USER, LABS_USER
from api_manager.token import get_alms_token, get_labs_token
from api_manager.constants import Project


class HeadersTemplates(Enum):
    JSON = {'Content-type': 'application/json'}
    FORM_DATA = {'Content-type': 'multipart/form-data'}
    DEFAULT = {}


def alms_headers(user=None, with_auth=True, headers_type: HeadersTemplates = HeadersTemplates.DEFAULT):
    """
    :param headers_type:
    :param with_auth:
    :param user:
    :return:
    """
    if isinstance(user, dict):
        # for lru_cache user always should be hashable
        # overriding user credentials with insomnia
        user = json.dumps({**ALMS_USER, **user})

    if with_auth:
        token = get_alms_token(user)
        return {**headers_type.value, 'Authorization': f'Bearer {token}'}

    return headers_type.value


def labs_headers(user=None, with_auth=True, headers_type: HeadersTemplates = HeadersTemplates.DEFAULT):
    """
    :param headers_type:
    :param with_auth:
    :param user:
    :return:
    """
    if isinstance(user, dict):
        # for lru_cache user always should be hashable
        # overriding user credentials with insomnia
        user = json.dumps({**LABS_USER, **user})

    if with_auth:
        token = get_labs_token(user)
        return {**headers_type.value, 'Authorization': f'Token {token}'}

    return headers_type.value


PROJECT_HEADERS = {
    Project.LABS: labs_headers,
    Project.ALMS: alms_headers
}

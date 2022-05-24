from typing import Dict
from typing_extensions import Protocol
import json

import requests

from factro_client.core.exceptions import UnauthorizedException

class IsDataclass(Protocol):
    __dataclass_fields__: Dict

class BaseHandler(object):

    def __init__(self, url: str, api_key: str):
        self._url = url
        self._api_key = api_key


    def do_get(self, path: str, options: Dict={}):
        headers = self.__get_default_headers()
        headers.update(options.get('headers', {}))
        headers.update(self.__get_auth_headers())

        request_url = f"{self._url}{path}"

        response = requests.get(request_url, headers=headers)

        self.__check_response(response)

        json_body = response.json()

        return json_body

    def do_delete(self, path: str, options: Dict={}):
        headers = self.__get_default_headers()
        headers.update(options.get('headers', {}))
        headers.update(self.__get_auth_headers())

        request_url = f"{self._url}{path}"

        response = requests.delete(request_url, headers=headers)

        self.__check_response(response)

    def do_post(self, path: str, payload: IsDataclass, options: Dict={}):
        headers = self.__get_default_headers()
        headers.update(options.get('headers', {}))
        headers.update(self.__get_auth_headers())

        request_url = f"{self._url}{path}"

        json_payload = json.dumps(payload)

        response = requests.post(request_url, json_payload, headers=headers)

        self.__check_response(response)

        if response.status_code == 200:
            json_body = response.json()
        else:
            json_body = {}

        return json_body

    def do_put(self, path: str, payload: IsDataclass, options: Dict={}):
        headers = self.__get_default_headers()
        headers.update(options.get('headers', {}))
        headers.update(self.__get_auth_headers())

        request_url = f"{self._url}{path}"

        json_payload = json.dumps(payload)

        response = requests.put(request_url, json_payload, headers=headers)
        
        self.__check_response(response)

        if response.status_code == 200:
            json_body = response.json()
        else:
            json_body = {}

        return json_body

    def __check_response(self, response):
        if response.status_code == 401:
            raise UnauthorizedException()
        else:
            response.raise_for_status()

    def __get_auth_headers(self):
        return {'Authorization': self._api_key}

    def __get_default_headers(self):
        return {'Content-Type': 'application/json'}

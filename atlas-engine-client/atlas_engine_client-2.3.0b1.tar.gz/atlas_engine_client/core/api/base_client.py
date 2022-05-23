from dataclasses import dataclass
from typing import Callable, Dict, Type
from requests.api import request
from typing_extensions import Protocol
import json

import requests

class IsDataclass(Protocol):
    __dataclass_fields__: Dict

class BaseClient(object):

    def __init__(self, url: str, identity: Callable=None):
        self._url = url

        if identity is not None:
            self._identity = identity
        else:
            self._identity = lambda: {"token": "ZHVtbXlfdG9rZW4="}


    def do_get(self, path: str, options: Dict={}):
        headers = self.__get_default_headers()
        headers.update(options.get('headers', {}))
        headers.update(self.__get_auth_headers())

        request_url = f"{self._url}{path}"

        response = requests.get(request_url, headers=headers)

        response.raise_for_status()

        json_body = response.json()

        return json_body

    def do_delete(self, path: str, options: Dict={}):
        headers = self.__get_default_headers()
        headers.update(options.get('headers', {}))
        headers.update(self.__get_auth_headers())

        request_url = f"{self._url}{path}"

        response = requests.delete(request_url, headers=headers)

        response.raise_for_status()

    def do_post(self, path: str, payload: IsDataclass, options: Dict={}):
        headers = self.__get_default_headers()
        headers.update(options.get('headers', {}))
        headers.update(self.__get_auth_headers())

        request_url = f"{self._url}{path}"

        json_payload = json.dumps(payload)

        response = requests.post(request_url, json_payload, headers=headers)

        response.raise_for_status()

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
        
        response.raise_for_status()

        if response.status_code == 200:
            json_body = response.json()
        else:
            json_body = {}

        return json_body

    def __get_auth_headers(self):
        identity = self.__get_identity()
        token = identity['token']
        return {'Authorization': 'Bearer {}'.format(token)}

    def __get_default_headers(self):
        return {'Content-Type': 'application/json'}

    def __get_identity(self):
        identity = self._identity

        if callable(self._identity):
            identity = self._identity()

        return identity

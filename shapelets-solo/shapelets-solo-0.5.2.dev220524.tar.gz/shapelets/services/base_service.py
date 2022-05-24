# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import json
import requests
import typing
import urllib3

from shapelets.dsl.argument_types import SupportedTypes
from shapelets.services.exceptions import ShapeletsException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_CONTENT_JSON_HEADER = {"Content-type": "application/json"}


class BaseService:
    def __init__(self, base_url: str, cookies: typing.Dict[str, str]):
        self.base_url = base_url
        self.cookies = cookies

    def request_post(self,
                     api_endpoint: str,
                     data: typing.Dict[str, SupportedTypes],
                     raise_type: ShapeletsException = ShapeletsException,
                     timeout_seconds: int = 300,
                     with_headers: bool = False) -> typing.Dict[str, SupportedTypes]:
        url = f"{self.base_url}/{api_endpoint}"
        json_data = json.dumps(data) if isinstance(data, dict) else data
        response = requests.post(url=url,
                                 timeout=timeout_seconds,
                                 headers=_CONTENT_JSON_HEADER,
                                 cookies=self.cookies,
                                 data=json_data,
                                 verify=False)
        if response.status_code != 200:
            try:
                response.raise_for_status()
            except requests.exceptions.RequestException as err:
                raise raise_type(err, response.content) from err
        return BaseService.__content_to_json(response, with_headers)

    def request_get(self,
                    api_endpoint: str,
                    raise_type: ShapeletsException = ShapeletsException,
                    timeout_seconds: int = 300,
                    raw_content: bool = False):
        url = f"{self.base_url}/{api_endpoint}"
        response = requests.get(url,
                                timeout=timeout_seconds,
                                headers=_CONTENT_JSON_HEADER,
                                cookies=self.cookies,
                                verify=False)
        if response.status_code != 200:
            try:
                response.raise_for_status()
            except requests.exceptions.RequestException as err:
                raise raise_type(err, response.content) from err
        if raw_content:
            return response.content
        return BaseService.__content_to_json(response)

    def request_put(self,
                    api_endpoint: str,
                    data: typing.Dict[str, SupportedTypes],
                    raise_type: ShapeletsException = ShapeletsException,
                    timeout_seconds: int = 300) -> typing.Dict[str, SupportedTypes]:
        url = f"{self.base_url}/{api_endpoint}"
        json_data = json.dumps(data)
        response = requests.put(url=url,
                                timeout=timeout_seconds,
                                headers=_CONTENT_JSON_HEADER,
                                cookies=self.cookies,
                                data=json_data,
                                verify=False)
        if response.status_code != 200:
            try:
                response.raise_for_status()
            except requests.exceptions.RequestException as err:
                raise raise_type(err, response.content) from err
        return BaseService.__content_to_json(response)

    def request_delete(self,
                       api_endpoint: str,
                       raise_type: ShapeletsException = ShapeletsException,
                       timeout_seconds: int = 300) -> bool:
        url = f"{self.base_url}/{api_endpoint}"
        response = requests.delete(url=url,
                                   timeout=timeout_seconds,
                                   headers=_CONTENT_JSON_HEADER,
                                   cookies=self.cookies,
                                   verify=False)
        if response.status_code == 200:
            return True
        if response.status_code == 404:
            return False
        try:
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            raise raise_type(err, response.content) from err
        return False

    @staticmethod
    def __content_to_json(response, with_headers: bool = False):
        content = response.content
        if content and isinstance(content, (str, bytes or bytearray)):
            json_content = json.loads(content)
            if with_headers:
                json_content["headers"] = response.headers
            return json_content
        else:
            from unittest.mock import MagicMock
            if content and isinstance(content, MagicMock):
                return content.return_value
        return None

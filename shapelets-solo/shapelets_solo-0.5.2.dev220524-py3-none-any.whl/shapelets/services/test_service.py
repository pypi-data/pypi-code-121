# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum
import typing

from shapelets.dsl import SupportedTypes
from shapelets.services.base_service import BaseService


class Endpoint(Enum):
    API = "api/###path###"

    def replace(self, path: str) -> str:
        template = str(self.value)
        return template.replace("###path###", path)


class TestService(BaseService):

    def ping(self):
        """
        This function performs a ping action.
        :return True if it receives the pong message.
        """
        self.request_get(Endpoint.API.replace("ping"), raw_content=True)
        return True

    def test_get(self, api_path: str) -> typing.Dict[str, SupportedTypes]:
        return self.request_get(Endpoint.API.replace(api_path))

    def test_get_raw(self, api_path: str) -> bytearray:
        return self.request_get(Endpoint.API.replace(api_path), raw_content=True)

    def test_delete(self, api_path: str) -> bool:
        return self.request_delete(f"api{api_path}")

    def test_post(self,
                  api_path: str,
                  data: typing.Dict[str, SupportedTypes]) -> typing.Dict[str, SupportedTypes]:
        return self.request_post(Endpoint.API.replace(api_path), data)

    def test_put(self,
                 api_path: str,
                 data: typing.Dict[str, SupportedTypes]) -> typing.Dict[str, SupportedTypes]:
        return self.request_put(Endpoint.API.replace(api_path), data)

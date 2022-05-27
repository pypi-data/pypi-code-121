#!/usr/bin/python3

#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

"""
Tuya connector API module OpenAPI client
"""

# Python base dependencies
import hashlib
import hmac
import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union

# Library dependencies
import requests

# Library libs
from fastybird_tuya_connector.logger import Logger
from fastybird_tuya_connector.types import OpenApiEndpoint


class TuyaTokenInfo:
    """
    Tuya token info

    @package        FastyBird:TuyaConnector!
    @module         api/openapi

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __uid: str
    __access_token: str
    __refresh_token: str
    __expire_time: int

    def __init__(self, token_response: Dict[str, Any]) -> None:
        result = token_response.get("result", {})

        self.__expire_time = token_response.get("t", 0) + result.get("expire", result.get("expire_time", 0)) * 1000

        self.__access_token = result.get("access_token", "")
        self.__refresh_token = result.get("refresh_token", "")

        self.__uid = result.get("uid", "")

    # -----------------------------------------------------------------------------

    @property
    def uid(self) -> str:
        """User identifier"""
        return self.__uid

    # -----------------------------------------------------------------------------

    @property
    def access_token(self) -> str:
        """Access token"""
        return self.__access_token

    # -----------------------------------------------------------------------------

    @access_token.setter
    def access_token(self, access_token: str) -> None:
        """Access token"""
        self.__access_token = access_token

    # -----------------------------------------------------------------------------

    @property
    def refresh_token(self) -> str:
        """Refresh token"""
        return self.__refresh_token

    # -----------------------------------------------------------------------------

    @property
    def expire_time(self) -> int:
        """Token expire time in seconds"""
        return self.__expire_time


class TuyaOpenAPI:  # pylint: disable=too-many-instance-attributes
    """Open Api.

    Typical usage example:

    openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY)
    """

    __session: requests.Session

    __endpoint: OpenApiEndpoint
    __access_id: str
    __access_secret: str
    __lang: str

    __token_info: Optional[TuyaTokenInfo] = None
    __dev_channel: str = ""

    __logger: Union[Logger, logging.Logger]

    __VERSION: str = "0.1.0"

    __TUYA_ERROR_CODE_TOKEN_INVALID = 1010

    __TOKEN_API_ENDPOINT = "/v1.0/token"
    __REFRESH_TOKEN_API_ENDPOINT = "/v1.0/token/{}"
    __USER_DEVICES_API_ENDPOINT = "/v1.0/users/{}/devices"
    __USER_DEVICE_DETAIL_API_ENDPOINT = "/v1.0/devices/{}"
    __USER_DEVICE_FACTORY_INFO_API_ENDPOINT = "/v1.0/devices/factory-infos"
    __USER_DEVICE_SPECIFICATION_API_ENDPOINT = "/v1.0/devices/{}/specifications"
    __USER_DEVICE_STATUS_API_ENDPOINT = "/v1.0/devices/{}/status"
    __USER_DEVICE_INFORMATION_API_ENDPOINT = "/v1.1/iot-03/devices/{}"
    __DEVICE_COMMAND_API_ENDPOINT = "/v1.0/iot-03/devices/{}/commands"

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        endpoint: OpenApiEndpoint,
        access_id: str,
        access_secret: str,
        lang: str = "en",
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__session = requests.session()

        self.__endpoint = endpoint
        self.__access_id = access_id
        self.__access_secret = access_secret
        self.__lang = lang

        self.__logger = logger

    # -----------------------------------------------------------------------------

    @property
    def dev_channel(self) -> str:
        """Dev channel"""
        return self.__dev_channel

    # -----------------------------------------------------------------------------

    @dev_channel.setter
    def dev_channel(self, dev_channel: str) -> None:
        """Dev channel setter"""
        self.__dev_channel = dev_channel

    # -----------------------------------------------------------------------------

    def connect(self) -> Dict[str, Any]:
        """Connect to Tuya Cloud"""
        response = self.get(self.__TOKEN_API_ENDPOINT, {"grant_type": 1})

        if not response["success"]:
            return response

        # Cache token info.
        self.__token_info = TuyaTokenInfo(response)

        return response

    # -----------------------------------------------------------------------------

    def disconnect(self) -> None:
        """Disconnect from Tuya Cloud"""

    # -----------------------------------------------------------------------------

    def is_connected(self) -> bool:
        """Check if client is connected to tuya cloud"""
        return self.__token_info is not None and self.__token_info.access_token != ""

    # -----------------------------------------------------------------------------

    def get_user_devices(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all devices for user"""
        if not self.is_connected():
            self.connect()

        response = self.get(path=self.__USER_DEVICES_API_ENDPOINT.format(user_id))

        result_data = response.get("result")

        if not response.get("success", False) or not isinstance(result_data, list):
            self.__logger.error(f"Error from Tuya server: {response.get('msg')}")

            raise ValueError("User devices couldn't be loaded")

        return result_data

    # -----------------------------------------------------------------------------

    def get_devices_factory_info(self, device_ids: List[str]) -> List[Dict[str, Any]]:
        """Get devices factory info"""
        if not self.is_connected():
            self.connect()

        response = self.get(
            path=self.__USER_DEVICE_FACTORY_INFO_API_ENDPOINT,
            params={
                "device_ids": ",".join(device_ids),
            },
        )

        result_data = response.get("result")

        if not response.get("success", False) or not isinstance(result_data, list):
            self.__logger.error(f"Error from Tuya server: {response.get('msg')}")

            raise ValueError("Devices factory info couldn't be loaded")

        return result_data

    # -----------------------------------------------------------------------------

    def get_device_detail(self, device_id: str) -> Dict[str, Any]:
        """Get device basic info from cloud server"""
        if not self.is_connected():
            self.connect()

        response = self.get(path=self.__USER_DEVICE_DETAIL_API_ENDPOINT.format(device_id))

        result_data = response.get("result")

        if not response.get("success", False) or not isinstance(result_data, dict):
            self.__logger.error(f"Error from Tuya server: {response.get('msg')}")

            raise ValueError("Device detail couldn't be loaded")

        return result_data

    # -----------------------------------------------------------------------------

    def get_device_specification(self, device_id: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Get functions and status for device"""
        if not self.is_connected():
            self.connect()

        response = self.get(path=self.__USER_DEVICE_SPECIFICATION_API_ENDPOINT.format(device_id))

        result_data = response.get("result")

        if not response.get("success", False) or not isinstance(result_data, dict):
            self.__logger.error(f"Error from Tuya server: {response.get('msg')}")

            raise ValueError("Device specification couldn't be loaded")

        return result_data.get("functions", []), result_data.get("status", [])

    # -----------------------------------------------------------------------------

    def get_device_status(self, device_id: str) -> List[Dict[str, Any]]:
        """Get status for device"""
        if not self.is_connected():
            self.connect()

        response = self.get(path=self.__USER_DEVICE_STATUS_API_ENDPOINT.format(device_id))

        result_data = response.get("result")

        if not response.get("success", False) or not isinstance(result_data, list):
            self.__logger.error(f"Error from Tuya server: {response.get('msg')}")

            raise ValueError("Device status couldn't be loaded")

        return result_data

    # -----------------------------------------------------------------------------

    def get_device_information(self, device_id: str) -> Dict[str, Any]:
        """Get device information"""
        if not self.is_connected():
            self.connect()

        response = self.get(path=self.__USER_DEVICE_INFORMATION_API_ENDPOINT.format(device_id))

        result_data = response.get("result")

        if not response.get("success", False) or not isinstance(result_data, dict):
            self.__logger.error(f"Error from Tuya server: {response.get('msg')}")

            raise ValueError("Device status couldn't be loaded")

        return result_data

    # -----------------------------------------------------------------------------

    def send_command(self, device_id: str, code: str, value: Union[str, int, bool]) -> bool:
        """Send command to device data point"""
        if not self.is_connected():
            self.connect()

        response = self.post(
            path=self.__DEVICE_COMMAND_API_ENDPOINT.format(device_id),
            body={
                "commands": [
                    {
                        "code": code,
                        "value": value,
                    }
                ]
            },
        )

        if not response.get("success", False) or not isinstance(response.get("result"), bool):
            self.__logger.error(f"Error from Tuya server: {response.get('msg')}")

            raise ValueError("Device command couldn't be sent")

        return True

    # -----------------------------------------------------------------------------

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Http GET

        Requests the server to return specified resources.

        Args:
            path (str): api path
            params (map): request parameter

        Returns:
            response: response body
        """
        return self.__request("GET", path, params, None)

    # -----------------------------------------------------------------------------

    def post(
        self,
        path: str,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Http POST

        Requests the server to update specified resources.

        Args:
            path (str): api path
            body (map): request body

        Returns:
            response: response body
        """
        return self.__request("POST", path, None, body)

    # -----------------------------------------------------------------------------

    def put(
        self,
        path: str,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Http PUT

        Requires the server to perform specified operations.

        Args:
            path (str): api path
            body (map): request body

        Returns:
            response: response body
        """
        return self.__request("PUT", path, None, body)

    # -----------------------------------------------------------------------------

    def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Http DELETE

        Requires the server to delete specified resources.

        Args:
            path (str): api path
            params (map): request param

        Returns:
            response: response body
        """
        return self.__request("DELETE", path, params, None)

    # -----------------------------------------------------------------------------

    def __request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self.__refresh_access_token_if_need(path)

        access_token = ""

        if self.__token_info:
            access_token = self.__token_info.access_token

        sign, timestamp = self.__calculate_sign(method, path, params, body)

        headers = {
            "client_id": self.__access_id,
            "sign": sign,
            "sign_method": "HMAC-SHA256",
            "access_token": access_token,
            "t": str(timestamp),
            "lang": self.__lang,
            "dev_lang": "python",
            "dev_version": self.__VERSION,
            "dev_channel": f"cloud_{self.__dev_channel}",
        }

        self.__logger.debug(
            f"Request: method = {method}, \
                url = {self.__endpoint.value + path},\
                params = {params},\
                body = {body},\
                t = {int(time.time()*1000)}"
        )

        response = self.__session.request(
            method, self.__endpoint.value + path, params=params, json=body, headers=headers
        )

        if response.ok is False:
            self.__logger.error("Response error: code=%s, body=%s", response.status_code, response.text)

            error_result = response.json()

            if isinstance(error_result, dict):
                return error_result

            return {}

        result = response.json()

        self.__logger.debug(
            "Response: %s",
            json.dumps(result, ensure_ascii=False, indent=2),
        )

        if result.get("code", -1) == self.__TUYA_ERROR_CODE_TOKEN_INVALID:
            self.__token_info = None
            self.connect()

        if isinstance(result, dict):
            return result

        return {}

    # -----------------------------------------------------------------------------

    # https://developer.tuya.com/docs/iot/open-api/api-reference/singnature?id=Ka43a5mtx1gsc
    def __calculate_sign(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, int]:
        # HTTP method
        str_to_sign = method
        str_to_sign += "\n"

        # Content-SHA256
        content_to_sha256 = "" if body is None or len(body.keys()) == 0 else json.dumps(body)

        str_to_sign += hashlib.sha256(content_to_sha256.encode("utf8")).hexdigest().lower()
        str_to_sign += "\n"

        # Header
        str_to_sign += "\n"

        # URL
        str_to_sign += path

        if params is not None and len(params.keys()) > 0:
            str_to_sign += "?"

            query_builder = ""
            params_keys = sorted(params.keys())

            for key in params_keys:
                query_builder += f"{key}={params[key]}&"
            str_to_sign += query_builder[:-1]

        # Sign
        timestamp = int(time.time() * 1000)

        message = self.__access_id

        if self.__token_info is not None:
            message += self.__token_info.access_token

        message += str(timestamp) + str_to_sign

        sign = (
            hmac.new(
                self.__access_secret.encode("utf8"),
                msg=message.encode("utf8"),
                digestmod=hashlib.sha256,
            )
            .hexdigest()
            .upper()
        )

        return sign, timestamp

    # -----------------------------------------------------------------------------

    def __refresh_access_token_if_need(self, path: str) -> None:
        if self.is_connected() is False:
            return

        if path.startswith(self.__TOKEN_API_ENDPOINT):
            return

        if self.__token_info is None:
            return

        # should use refresh token?
        now = int(time.time() * 1000)
        expired_time = self.__token_info.expire_time

        if expired_time - 60 * 1000 > now:  # 1min
            return

        self.__token_info.access_token = ""

        response = self.get(self.__REFRESH_TOKEN_API_ENDPOINT.format(self.__token_info.refresh_token))

        self.__token_info = TuyaTokenInfo(response)

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
Tuya connector clients module open pulsar client
"""

# Python base dependencies
import asyncio
import base64
import hashlib
import json
import logging
import ssl
import time
from typing import Dict, Union

import websockets

# Library dependencies
from Crypto.Cipher import AES

# Library libs
from fastybird_metadata.devices_module import ConnectionState
from websockets.legacy.client import WebSocketClientProtocol

from fastybird_tuya_connector.api.openapi import TuyaOpenAPI
from fastybird_tuya_connector.consumers.consumer import Consumer
from fastybird_tuya_connector.consumers.entities import (
    DeviceStatusEntity,
    DpStatusEntity,
)
from fastybird_tuya_connector.logger import Logger
from fastybird_tuya_connector.registry.model import (
    DataPointsRegistry,
    DevicesRegistry,
    PropertiesRegistry,
)
from fastybird_tuya_connector.types import (
    DataPointType,
    DeviceProperty,
    OpenPulsarEndpoint,
    OpenPulsarTopic,
)


class TuyaCloudClient:  # pylint: disable=too-many-instance-attributes,too-few-public-methods
    """
    Tuya cloud client - combined OpenPulsar WS client and OpenApi client

    @package        FastyBird:TuyaConnector!
    @module         clients/cloud

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __access_id: str
    __access_secret: str

    __endpoint: OpenPulsarEndpoint
    __topic: OpenPulsarTopic

    __consumer: Consumer

    __devices_registry: DevicesRegistry
    __properties_registry: PropertiesRegistry
    __data_points_registry: DataPointsRegistry

    __openapi: TuyaOpenAPI

    __websockets: WebSocketClientProtocol

    __logger: Union[Logger, logging.Logger]

    __last_reading_timestamp: Dict[str, float] = {}

    __WEB_SOCKET_QUERY_PARAMS: str = "?ackTimeoutMillis=3000&subscriptionType=Failover"

    __PING_INTERVAL = 30
    __PING_TIMEOUT = 3

    __DP_VALUE_RESEND_DELAY: float = 5.0

    __READ_STATE_DELAY: float = 15.0  # Delay between read state packets

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        endpoint: OpenPulsarEndpoint,
        access_id: str,
        access_secret: str,
        consumer: Consumer,
        devices_registry: DevicesRegistry,
        properties_registry: PropertiesRegistry,
        data_points_registry: DataPointsRegistry,
        openapi: TuyaOpenAPI,
        topic: OpenPulsarTopic = OpenPulsarTopic.PROD,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__access_id = access_id
        self.__access_secret = access_secret
        self.__endpoint = endpoint
        self.__topic = topic

        self.__consumer = consumer
        self.__devices_registry = devices_registry
        self.__properties_registry = properties_registry
        self.__data_points_registry = data_points_registry
        self.__openapi = openapi

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def start(self) -> None:
        """Start cloud devices communication"""
        asyncio.ensure_future(self.__websockets_worker())
        asyncio.ensure_future(self.__openapi_worker())

        for device_record in self.__devices_registry:
            try:
                device_status = self.__openapi.get_device_information(device_id=device_record.identifier)

                device_state_property_record = self.__properties_registry.get_by_property(
                    device_id=device_record.id,
                    property_type=DeviceProperty.STATE,
                )

                if device_state_property_record is not None:
                    if device_status.get("online", False) is True:
                        self.__properties_registry.set_value(
                            device_property=device_state_property_record,
                            value=ConnectionState.CONNECTED.value,
                        )

                    else:
                        self.__properties_registry.set_value(
                            device_property=device_state_property_record,
                            value=ConnectionState.DISCONNECTED.value,
                        )

            except ValueError:
                pass

    # -----------------------------------------------------------------------------

    async def __websockets_worker(self) -> None:
        ssl_context = ssl.SSLContext()
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_context.check_hostname = False

        async with websockets.connect(  # type: ignore[attr-defined]  # pylint: disable=no-member
            uri=self.__build_topic_url(),
            extra_headers={
                "Connection": "Upgrade",
                "username": self.__access_id,
                "password": self.__gen_pwd(),
            },
            ssl=ssl_context,
            ping_interval=self.__PING_INTERVAL,
            ping_timeout=self.__PING_TIMEOUT,
        ) as socket:
            self.__websockets = socket

            while True:
                message = await self.__websockets.recv()

                if isinstance(message, str):
                    await self.__on_message(message=message)

    # -----------------------------------------------------------------------------

    async def __openapi_worker(self) -> None:
        while True:  # pylint: disable=too-many-nested-blocks
            for data_point_record in self.__data_points_registry.get_all_by_type(dp_type=DataPointType.CLOUD):
                if data_point_record.expected_value is not None:
                    if data_point_record.expected_value == data_point_record.actual_value:
                        self.__data_points_registry.set_expected_value(data_point=data_point_record, value=None)

                    elif (
                        data_point_record.expected_pending is None
                        or time.time() - data_point_record.expected_pending >= self.__DP_VALUE_RESEND_DELAY
                    ):
                        device_record = self.__devices_registry.get_by_id(device_id=data_point_record.device_id)

                        if (
                            device_record is not None
                            and data_point_record.identifier is not None
                            and data_point_record.expected_value is not None
                        ):
                            self.__openapi.send_command(
                                device_id=device_record.identifier,
                                code=data_point_record.identifier,
                                value=data_point_record.expected_value,
                            )

                            self.__data_points_registry.set_expected_pending(
                                data_point=data_point_record,
                                timestamp=time.time(),
                            )

            for device_record in self.__devices_registry:
                if (
                    device_record.id.__str__() not in self.__last_reading_timestamp
                    or (time.time() - self.__last_reading_timestamp[device_record.id.__str__()])
                    >= self.__READ_STATE_DELAY
                ):
                    try:
                        reading_result = self.__openapi.get_device_status(device_id=device_record.identifier)

                        entity = DeviceStatusEntity(
                            device_identifier=device_record.identifier,
                        )

                        for data_point in reading_result:
                            data_point_value = data_point.get("value")

                            if isinstance(data_point_value, (str, int, bool)):
                                entity.add_dps_state(
                                    DpStatusEntity(
                                        device_identifier=device_record.identifier,
                                        dp_identifier=str(data_point.get("code")),
                                        dp_value=data_point_value,
                                    )
                                )

                        self.__consumer.append(entity=entity)

                        self.__last_reading_timestamp[device_record.id.__str__()] = time.time()

                        break

                    except ValueError:
                        pass

            # Be gentle to server
            await asyncio.sleep(0.01)

    # -----------------------------------------------------------------------------

    async def __on_message(self, message: str) -> None:
        message_json = json.loads(message)

        payload = base64.b64decode(message_json["payload"]).decode("ascii")

        self.__logger.debug("received message origin payload: %s", payload)

        try:  # pylint: disable=too-many-nested-blocks
            data_map = json.loads(payload)

            decrypted_data = self.__decrypt_by_aes(
                data_map["data"],
                self.__access_secret,
            )

            self.__logger.debug("received message decrypted: %s", decrypted_data)

            try:
                received_data = json.loads(decrypted_data)

                device_dps = received_data.get("status")

                if isinstance(device_dps, list):
                    entity = DeviceStatusEntity(
                        device_identifier=str(received_data.get("devId")),
                    )

                    for device_dp in device_dps:
                        if isinstance(device_dp, dict):
                            dp_value = device_dp.get("value")

                            if isinstance(dp_value, (str, int, bool)):
                                entity.add_dps_state(
                                    DpStatusEntity(
                                        device_identifier=str(received_data.get("devId")),
                                        dp_identifier=str(device_dp.get("code")),
                                        dp_value=dp_value,
                                    )
                                )

                    self.__consumer.append(entity=entity)

            except json.JSONDecodeError:
                pass

        except Exception as ex:  # pylint: disable=broad-except
            self.__logger.debug("handler message, a business exception has occurred,e:%s", ex)

        await self.__websockets.send(json.dumps({"messageId": message_json["messageId"]}))

    # -----------------------------------------------------------------------------

    def __build_topic_url(self) -> str:
        return (
            self.__endpoint.value
            + "ws/v2/consumer/persistent/"
            + self.__access_id
            + "/out/"
            + self.__topic.value
            + "/"
            + self.__access_id
            + "-sub"
            + self.__WEB_SOCKET_QUERY_PARAMS
        )

    # -----------------------------------------------------------------------------

    def __gen_pwd(self) -> str:
        mix_str = self.__access_id + self.__md5_hex(self.__access_secret)

        return self.__md5_hex(mix_str)[8:24]

    # -----------------------------------------------------------------------------

    @staticmethod
    def __decrypt_by_aes(raw: bytes, key: str) -> str:
        raw = base64.b64decode(raw)
        key = key[8:24]
        cipher = AES.new(key.encode("utf-8"), AES.MODE_ECB)
        raw = cipher.decrypt(raw)
        res_str = str(raw, "utf-8")
        res_str = res_str[: -ord(res_str[-1])]

        return res_str

    # -----------------------------------------------------------------------------

    @staticmethod
    def __md5_hex(md5_str: str) -> str:
        md_tool = hashlib.md5()
        md_tool.update(md5_str.encode("utf-8"))

        return md_tool.hexdigest()

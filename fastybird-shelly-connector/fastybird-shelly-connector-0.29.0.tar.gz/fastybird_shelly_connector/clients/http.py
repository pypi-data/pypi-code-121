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
Shelly connector clients module CoAP client
"""

# Python base dependencies
import base64
import json
import logging
import re
import time
from http import client
from socket import gethostbyaddr, timeout  # pylint: disable=no-name-in-module
from typing import List, Optional, Tuple, Union

# Library dependencies
from fastybird_metadata.devices_module import ConnectionState

# Library libs
from fastybird_shelly_connector.api.gen1parser import Gen1Parser
from fastybird_shelly_connector.api.gen1validator import Gen1Validator
from fastybird_shelly_connector.api.transformers import DataTransformHelpers
from fastybird_shelly_connector.clients.client import IClient
from fastybird_shelly_connector.consumers.consumer import Consumer
from fastybird_shelly_connector.exceptions import (
    FileNotFoundException,
    LogicException,
    ParsePayloadException,
)
from fastybird_shelly_connector.logger import Logger
from fastybird_shelly_connector.registry.model import (
    BlocksRegistry,
    CommandsRegistry,
    DevicesRegistry,
    PropertiesRegistry,
    SensorsRegistry,
)
from fastybird_shelly_connector.registry.records import (
    BlockRecord,
    DeviceRecord,
    SensorRecord,
)
from fastybird_shelly_connector.types import (
    ClientMessageType,
    ClientType,
    DeviceCommandType,
    DeviceProperty,
    WritableSensor,
)


class HttpClient(IClient):  # pylint: disable=too-many-instance-attributes
    """
    Basic HTTP API client

    @package        FastyBird:ShellyConnector!
    @module         clients/http

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __processed_devices: List[str] = []

    __validator: Gen1Validator
    __parser: Gen1Parser

    __consumer: Consumer

    __devices_registry: DevicesRegistry
    __properties_registry: PropertiesRegistry
    __commands_registry: CommandsRegistry
    __blocks_registry: BlocksRegistry
    __sensors_registry: SensorsRegistry

    __logger: Union[Logger, logging.Logger]

    __SHELLY_INFO_ENDPOINT: str = "/shelly"
    __STATUS_ENDPOINT: str = "/status"
    __SETTINGS_ENDPOINT: str = "/settings"
    __DESCRIPTION_ENDPOINT: str = "/cit/d"
    __SET_CHANNEL_SENSOR_ENDPOINT: str = "/{channel}/{index}?{action}={value}"

    __SENDING_CMD_DELAY: float = 60

    __DEVICE_COMMUNICATION_TIMEOUT: float = 120.0
    __SENSOR_VALUE_RESEND_DELAY: float = 5.0

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        validator: Gen1Validator,
        parser: Gen1Parser,
        consumer: Consumer,
        devices_registry: DevicesRegistry,
        properties_registry: PropertiesRegistry,
        commands_registry: CommandsRegistry,
        blocks_registry: BlocksRegistry,
        sensors_registry: SensorsRegistry,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__consumer = consumer

        self.__validator = validator
        self.__parser = parser

        self.__devices_registry = devices_registry
        self.__properties_registry = properties_registry
        self.__commands_registry = commands_registry
        self.__blocks_registry = blocks_registry
        self.__sensors_registry = sensors_registry

        self.__logger = logger

        self.__processed_devices = []

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> ClientType:
        """Client type"""
        return ClientType.HTTP

    # -----------------------------------------------------------------------------

    def start(self) -> None:
        """Start communication"""

    # -----------------------------------------------------------------------------

    def stop(self) -> None:
        """Stop communication"""

    # -----------------------------------------------------------------------------

    def is_connected(self) -> bool:
        """Check if client is connected"""
        return True

    # -----------------------------------------------------------------------------

    def discover(self) -> None:
        """Send discover command"""

    # -----------------------------------------------------------------------------

    def handle(self) -> None:  # pylint: disable=too-many-branches,too-many-return-statements
        """Process HTTP requests"""
        for device_record in self.__devices_registry:
            if device_record.id.__str__() in self.__processed_devices:
                continue

            self.__processed_devices.append(device_record.id.__str__())

            ip_address_property = self.__properties_registry.get_by_property(
                device_id=device_record.id,
                property_type=DeviceProperty.IP_ADDRESS,
            )

            if ip_address_property is None or not isinstance(ip_address_property.actual_value, str):
                return

            if self.__check_and_send_command(device=device_record, command=DeviceCommandType.GET_SHELLY) is False:
                return

            if self.__check_and_send_command(device=device_record, command=DeviceCommandType.GET_DESCRIPTION) is False:
                return

            if self.__check_and_send_command(device=device_record, command=DeviceCommandType.GET_SETTINGS) is False:
                return

            if self.__check_and_send_command(device=device_record, command=DeviceCommandType.GET_STATUS) is False:
                return

            state_property_record = self.__properties_registry.get_by_property(
                device_id=device_record.id,
                property_type=DeviceProperty.STATE,
            )

            if state_property_record is not None and state_property_record.actual_value == ConnectionState.INIT.value:
                self.__properties_registry.set_value(
                    item=state_property_record,
                    value=ConnectionState.CONNECTED.value,
                )

            if (
                device_record.last_communication_timestamp is None
                or time.time() - device_record.last_communication_timestamp > self.__DEVICE_COMMUNICATION_TIMEOUT
            ):
                if (
                    state_property_record is not None
                    and state_property_record.actual_value != ConnectionState.LOST.value
                ):
                    self.__properties_registry.set_value(
                        item=state_property_record,
                        value=ConnectionState.LOST.value,
                    )

                return

            if (
                device_record.last_communication_timestamp is not None
                and time.time() - device_record.last_communication_timestamp > self.__DEVICE_COMMUNICATION_TIMEOUT
            ):
                if (
                    state_property_record is not None
                    and state_property_record.actual_value != ConnectionState.CONNECTED.value
                ):
                    self.__properties_registry.set_value(
                        item=state_property_record,
                        value=ConnectionState.CONNECTED.value,
                    )

                return

            for block in self.__blocks_registry.get_all_by_device(device_id=device_record.id):
                for sensor in self.__sensors_registry.get_all_for_block(block_id=block.id):
                    if sensor.expected_value is not None:
                        if sensor.expected_value == sensor.actual_value:
                            self.__sensors_registry.set_expected_value(sensor=sensor, value=None)

                        elif (
                            sensor.expected_pending is None
                            or time.time() - sensor.expected_pending >= self.__SENSOR_VALUE_RESEND_DELAY
                        ):
                            self.write_sensor(
                                device_record=device_record,
                                block_record=block,
                                sensor_record=sensor,
                                write_value=DataTransformHelpers.transform_to_device(
                                    data_type=sensor.data_type,
                                    value_format=sensor.format,
                                    value=sensor.expected_value,
                                ),
                            )

                            self.__sensors_registry.set_expected_pending(sensor=sensor, timestamp=time.time())

        self.__processed_devices = []

    # -----------------------------------------------------------------------------

    def write_sensor(
        self,
        device_record: DeviceRecord,
        block_record: BlockRecord,
        sensor_record: SensorRecord,
        write_value: Union[str, int, float, bool, None],
    ) -> None:
        """Write value to device sensor"""
        ip_address_property = self.__properties_registry.get_by_property(
            device_id=device_record.id,
            property_type=DeviceProperty.IP_ADDRESS,
        )

        if ip_address_property is None or not isinstance(ip_address_property.actual_value, str):
            return

        match = re.compile("(?P<channelName>[a-zA-Z]+)_(?P<channelIndex>[0-9_]+)")

        test = match.fullmatch(block_record.description)

        if test is None:
            return

        if write_value is None:
            return

        success, _ = self.__send_http_get(
            host=ip_address_property.actual_value,
            url=self.__SET_CHANNEL_SENSOR_ENDPOINT.replace("{channel}", test.group("channelName"))
            .replace("{index}", test.group("channelIndex"))
            .replace("{action}", self.__build_action(sensor_record=sensor_record))
            .replace("{value}", str(write_value)),
            username=device_record.username,
            password=device_record.password,
        )

        self.__commands_registry.create_or_update(
            device_id=device_record.id,
            client_type=self.type,
            command_type=DeviceCommandType.SET_SENSOR,
            command_status=success,
        )

    # -----------------------------------------------------------------------------

    def __check_and_send_command(self, device: DeviceRecord, command: DeviceCommandType) -> bool:
        http_command = self.__commands_registry.get_by_command(
            device_id=device.id,
            client_type=self.type,
            command_type=command,
        )

        state_property_record = self.__properties_registry.get_by_property(
            device_id=device.id,
            property_type=DeviceProperty.STATE,
        )

        if http_command is None:
            self.__send_command(
                device_record=device,
                endpoint=self.__get_command_endpoint(command=command),
                command=command,
            )

            if state_property_record is not None:
                self.__properties_registry.set_value(
                    item=state_property_record,
                    value=ConnectionState.INIT.value,
                )

            return False

        if http_command.command_status is True:
            return True

        if time.time() - http_command.command_timestamp > self.__SENDING_CMD_DELAY:
            return False

        self.__send_command(
            device_record=device,
            endpoint=self.__get_command_endpoint(command=command),
            command=command,
        )

        if state_property_record is not None:
            self.__properties_registry.set_value(
                item=state_property_record,
                value=ConnectionState.INIT.value,
            )

        return False

    # -----------------------------------------------------------------------------

    def __send_command(
        self,
        device_record: DeviceRecord,
        endpoint: str,
        command: DeviceCommandType,
    ) -> None:
        ip_address_property = self.__properties_registry.get_by_property(
            device_id=device_record.id,
            property_type=DeviceProperty.IP_ADDRESS,
        )

        if ip_address_property is None or not isinstance(ip_address_property.actual_value, str):
            return

        success, response = self.__send_http_get(
            host=ip_address_property.actual_value,
            url=endpoint,
            username=device_record.username,
            password=device_record.password,
        )

        self.__commands_registry.create_or_update(
            device_id=device_record.id,
            client_type=self.type,
            command_type=command,
            command_status=success,
        )

        if success:
            self.__handle_message(
                device_identifier=device_record.identifier.lower(),
                device_ip_address=ip_address_property.actual_value,
                message_payload=response,
                message_type=self.__get_message_type_for_command(command=command),
            )

    # -----------------------------------------------------------------------------

    def __send_http_get(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        host: str,
        url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        log_error: bool = True,
    ) -> Tuple[bool, str]:
        """Send HTTP GET request"""
        res = ""
        success = False
        conn = None

        try:
            self.__logger.debug(
                "http://%s%s",
                host,
                url,
                extra={
                    "client": {
                        "type": ClientType.HTTP.value,
                    },
                },
            )

            conn = client.HTTPConnection(host, timeout=5)

            headers = {"Connection": "close"}

            conn.request("GET", url, None, headers)

            resp = conn.getresponse()

            if resp.status == 401 and username is not None and password is not None:
                combo = f"{username}:{password}"
                auth = str(base64.b64encode(combo.encode()), "cp1252")

                headers["Authorization"] = f"Basic {auth}"

                conn.request("GET", url, None, headers)

                resp = conn.getresponse()

            if resp.status == 200:
                body = resp.read()

                res = json.dumps(json.loads(str(body, "utf-8")))

                success = True

                self.__logger.debug(
                    "http://%s%s - OK",
                    host,
                    url,
                    extra={
                        "client": {
                            "type": ClientType.HTTP.value,
                        },
                    },
                )

            else:
                res = f"Error, {resp.status} {resp.reason} http://{host}{url}"

                self.__logger.warning(
                    res,
                    extra={
                        "client": {
                            "type": ClientType.HTTP.value,
                        },
                    },
                )

        except Exception as ex:  # pylint: disable=broad-except
            success = False

            if isinstance(ex, timeout):
                msg = f"Timeout connecting to http://{host}{url}"

                try:
                    res = gethostbyaddr(host)[0]
                    msg += " [" + res + "]"

                except Exception:  # pylint: disable=broad-except
                    pass

                self.__logger.error(
                    msg,
                    extra={
                        "client": {
                            "type": ClientType.HTTP.value,
                        },
                    },
                )

            else:
                res = str(ex)

                if log_error:
                    self.__logger.error(
                        "Error http GET: http://%s%s",
                        host,
                        url,
                        extra={
                            "client": {
                                "type": ClientType.HTTP.value,
                            },
                            "exception": {
                                "message": str(ex),
                                "code": type(ex).__name__,
                            },
                        },
                    )

                else:
                    self.__logger.debug(
                        "Fail http GET: %s %s %s",
                        host,
                        url,
                        ex,
                        extra={
                            "client": {
                                "type": ClientType.HTTP.value,
                            },
                        },
                    )
        finally:
            if conn:
                conn.close()

        return success, res

    # -----------------------------------------------------------------------------

    @staticmethod
    def __get_message_type_for_command(command: DeviceCommandType) -> ClientMessageType:
        if command == DeviceCommandType.GET_SHELLY:
            return ClientMessageType.HTTP_SHELLY

        if command == DeviceCommandType.GET_STATUS:
            return ClientMessageType.HTTP_STATUS

        if command == DeviceCommandType.GET_DESCRIPTION:
            return ClientMessageType.HTTP_DESCRIPTION

        if command == DeviceCommandType.GET_SETTINGS:
            return ClientMessageType.HTTP_SETTINGS

        raise AttributeError("Provided command is not supported by connector")

    # -----------------------------------------------------------------------------

    def __get_command_endpoint(self, command: DeviceCommandType) -> str:
        if command.__eq__(DeviceCommandType.GET_SHELLY):
            return self.__SHELLY_INFO_ENDPOINT

        if command.__eq__(DeviceCommandType.GET_STATUS):
            return self.__STATUS_ENDPOINT

        if command.__eq__(DeviceCommandType.GET_DESCRIPTION):
            return self.__DESCRIPTION_ENDPOINT

        if command.__eq__(DeviceCommandType.GET_SETTINGS):
            return self.__SETTINGS_ENDPOINT

        raise AttributeError("Provided command is not supported by connector")

    # -----------------------------------------------------------------------------

    @staticmethod
    def __build_action(sensor_record: SensorRecord) -> str:
        if sensor_record.description == WritableSensor.OUTPUT.value:
            return "turn"

        if sensor_record.description == WritableSensor.COLOR_TEMP.value:
            return "temp"

        return sensor_record.description

    # -----------------------------------------------------------------------------

    def __handle_message(
        self,
        device_identifier: str,
        device_ip_address: str,
        message_payload: str,
        message_type: ClientMessageType,
    ) -> None:
        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=device_identifier,
        )

        if device_record is not None:
            self.__devices_registry.set_last_communication_timestamp(
                device=device_record,
                last_communication_timestamp=time.time(),
            )

        try:
            if (
                self.__validator.validate_http_message(
                    message_payload=message_payload,
                    message_type=message_type,
                )
                is False
            ):
                return

        except (LogicException, FileNotFoundException) as ex:
            self.__logger.error(
                "Received message validation against schema failed",
                extra={
                    "device": {
                        "identifier": device_identifier,
                        "ip_address": device_ip_address,
                    },
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )
            return

        try:
            entity = self.__parser.parse_http_message(
                device_identifier=device_identifier,
                device_ip_address=device_ip_address,
                message_payload=message_payload,
                message_type=message_type,
            )

        except (FileNotFoundException, LogicException, ParsePayloadException) as ex:
            self.__logger.error(
                "Received message could not be successfully parsed to entity",
                extra={
                    "device": {
                        "identifier": device_identifier,
                        "ip_address": device_ip_address,
                    },
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )
            return

        self.__consumer.append(entity=entity)

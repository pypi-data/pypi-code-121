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
Tuya connector clients module discovery client
"""

# Python base dependencies
import json
import logging
import socket
from hashlib import md5
from typing import Any, Dict, List, Optional, Set, Union

# Library dependencies
from Crypto.Cipher import AES
from fastybird_metadata.types import DataType

# Library libs
from fastybird_tuya_connector.api.localapi import DeviceLocalApi
from fastybird_tuya_connector.api.openapi import TuyaOpenAPI
from fastybird_tuya_connector.consumers.consumer import Consumer
from fastybird_tuya_connector.consumers.entities import (
    CloudDeviceFoundEntity,
    LocalDeviceFoundEntity,
)
from fastybird_tuya_connector.logger import Logger
from fastybird_tuya_connector.registry.model import (
    DiscoveredDataPointsRegistry,
    DiscoveredDevicesRegistry,
    TuyaCloudDataPointsRegistry,
    TuyaCloudDevicesRegistry,
)
from fastybird_tuya_connector.types import DataPointType, DeviceProtocolVersion


class DevicesDiscovery:  # pylint: disable=too-many-instance-attributes
    """
    Tuya devices discovery service

    @package        FastyBird:TuyaConnector!
    @module         discovery

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __enabled: bool = False

    __connection: Optional[socket.socket] = None

    __openapi: TuyaOpenAPI

    __consumer: Consumer

    __discovered_devices_registry: DiscoveredDevicesRegistry
    __discovered_data_points_registry: DiscoveredDataPointsRegistry
    __tuya_cloud_devices_registry: TuyaCloudDevicesRegistry
    __tuya_cloud_data_points_registry: TuyaCloudDataPointsRegistry

    __logger: Union[Logger, logging.Logger]

    __udp_scan_processed: Set[DeviceProtocolVersion] = set()
    __udp_scan_retries: int = 0

    __devices_uid: Optional[str] = None

    __UDP_BIND_IP: str = "0.0.0.0"
    __UDP_PORT: Dict[str, int] = {
        DeviceProtocolVersion.V31.value: 6666,
        DeviceProtocolVersion.V33.value: 6667,
    }
    __UDP_TIMEOUT: int = 3

    __MAX_SCAN_RETRY: int = 3

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        discovered_devices_registry: DiscoveredDevicesRegistry,
        discovered_data_points_registry: DiscoveredDataPointsRegistry,
        tuya_cloud_devices_registry: TuyaCloudDevicesRegistry,
        tuya_cloud_data_points_registry: TuyaCloudDataPointsRegistry,
        consumer: Consumer,
        openapi: TuyaOpenAPI,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__discovered_devices_registry = discovered_devices_registry
        self.__discovered_data_points_registry = discovered_data_points_registry
        self.__tuya_cloud_devices_registry = tuya_cloud_devices_registry
        self.__tuya_cloud_data_points_registry = tuya_cloud_data_points_registry

        self.__consumer = consumer

        self.__openapi = openapi

        self.__logger = logger

    # -----------------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        """Discovery client status"""
        return self.__enabled

    # -----------------------------------------------------------------------------

    def enable(self) -> None:
        """Enable client"""
        self.__enabled = True

        self.__udp_scan_processed = set()
        self.__udp_scan_retries = 0

        self.__discovered_devices_registry.reset()
        self.__tuya_cloud_devices_registry.reset()

        self.__devices_uid = None

        # Clear udp client
        self.__disconnect_client()

    # -----------------------------------------------------------------------------

    def disable(self) -> None:
        """Disable client"""
        self.__enabled = False

        # Clear udp client
        self.__disconnect_client()

    # -----------------------------------------------------------------------------

    def handle(self) -> None:
        """Tuya devices discovery handle"""
        if not self.__enabled:
            return

        if self.__udp_scan_retries > self.__MAX_SCAN_RETRY:
            self.__disconnect_client()
            self.__udp_scan_retries = 0

        if self.__connection is not None:
            try:
                data, _ = self.__connection.recvfrom(4048)

                self.__handle_found_local_device(data=data)

                self.__udp_scan_retries = self.__udp_scan_retries + 1

                return

            except socket.timeout:
                # Timeout
                self.__udp_scan_retries = self.__udp_scan_retries + 1

                return

        for protocol_version in DeviceProtocolVersion:
            if protocol_version not in self.__udp_scan_processed:
                self.__disconnect_client()
                self.__connect_client(ip_address=self.__UDP_BIND_IP, port=self.__UDP_PORT[protocol_version.value])

                self.__udp_scan_processed.add(protocol_version)

                return

        if len(self.__discovered_devices_registry) > 0:
            if self.__devices_uid is None:
                test_device_record = self.__discovered_devices_registry[0]

                try:
                    device_detail = self.__openapi.get_device_detail(device_id=test_device_record.id)

                except ValueError:
                    self.__discovered_devices_registry.remove(device_id=test_device_record.id)

                    return

                self.__devices_uid = device_detail.get("uid")

            # Device uid couldn't be obtained
            if self.__devices_uid is None:
                self.__logger.warning("Devices uid couldn't be obtained from device detail")

                self.disable()

                return

            user_devices = self.__openapi.get_user_devices(user_id=self.__devices_uid)

            devices_factory_info = self.__openapi.get_devices_factory_info(
                device_ids=list(i["id"] for i in user_devices),
            )

            self.__handle_found_cloud_devices(user_devices=user_devices, devices_factory_info=devices_factory_info)

            self.__handle_check_local_devices()

        # Devices discovery is finished
        self.disable()

    # -----------------------------------------------------------------------------

    def __connect_client(self, ip_address: str, port: int) -> None:
        if self.__connection is None:
            try:
                self.__connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

                self.__connection.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                self.__connection.bind((ip_address, port))
                self.__connection.settimeout(self.__UDP_TIMEOUT)

            except Exception as ex:  # pylint: disable=broad-except
                self.__logger.error(
                    "UDP client can't be created",
                    extra={
                        "exception": {
                            "message": str(ex),
                            "code": type(ex).__name__,
                        },
                    },
                )
                self.__logger.exception(ex)

    # -----------------------------------------------------------------------------

    def __disconnect_client(self) -> None:
        if self.__connection is not None:
            try:
                self.__connection.shutdown(socket.SHUT_RDWR)

            except socket.error:
                pass

        self.__connection = None

    # -----------------------------------------------------------------------------

    def __handle_found_local_device(self, data: bytes) -> None:
        try:
            result = self.__unpad(
                string=AES.new(md5(b"yGAdlopoPVldABfn").digest(), AES.MODE_ECB).decrypt(data[20:-8])
            ).decode()

        except Exception:  # pylint: disable=broad-except
            result = (data[20:-8]).decode()

        try:
            content: Dict = json.loads(result)

            self.__logger.debug("Received valid UDP packet: %r", content)

            self.__discovered_devices_registry.append(
                device_id=str(content.get("gwId")),
                device_ip_address=str(content.get("ip")),
                device_product_key=str(content.get("productKey")),
                device_encrypted=bool(content.get("encrypt", False)),
                device_version=str(content.get("version")),
            )

        except json.JSONDecodeError:
            self.__logger.debug("Invalid UDP Packet: %r", data)

    # -----------------------------------------------------------------------------

    def __handle_found_cloud_devices(  # pylint: disable=too-many-branches
        self,
        user_devices: List[Dict[str, Any]],
        devices_factory_info: List[Dict[str, Any]],
    ) -> None:
        for user_device in user_devices:
            self.__tuya_cloud_devices_registry.create_or_update(
                device_id=str(user_device.get("id")),
                device_local_key=str(user_device.get("local_key")),
                device_name=str(user_device.get("name")),
                device_uid=str(user_device.get("uid")),
                device_model=str(user_device.get("model")),
            )

        for device_factory_info in devices_factory_info:
            cloud_device_record = self.__tuya_cloud_devices_registry.get_by_id(
                device_id=str(device_factory_info.get("id")),
            )

            if cloud_device_record is not None:
                self.__tuya_cloud_devices_registry.create_or_update(
                    device_id=cloud_device_record.id,
                    device_local_key=cloud_device_record.local_key,
                    device_name=cloud_device_record.name,
                    device_uid=cloud_device_record.uid,
                    device_model=cloud_device_record.model,
                    device_serial_number=str(device_factory_info.get("sn")),
                    device_mac_address=str(device_factory_info.get("mac")),
                )

        for cloud_device_record in self.__tuya_cloud_devices_registry:
            device_functions, device_statuses = self.__openapi.get_device_specification(
                device_id=cloud_device_record.id,
            )

            for device_function in device_functions:
                existing_dp = self.__tuya_cloud_data_points_registry.get_by_code(
                    device_id=cloud_device_record.id,
                    dp_code=str(device_function.get("code")),
                )

                data_type = existing_dp.data_type if existing_dp is not None else DataType.UNKNOWN

                value_format = None

                function_type = str(device_function.get("type")).lower()

                if function_type == "boolean":
                    data_type = DataType.BOOLEAN

                if function_type == "integer":
                    data_type = DataType.INT

                if function_type == "enum":
                    data_type = DataType.ENUM

                    value_format = device_function.get("range")

                if function_type == "json":
                    pass

                try:
                    function_spec = json.loads(str(device_function.get("values")))

                except json.JSONDecodeError:
                    function_spec = {}

                self.__tuya_cloud_data_points_registry.create_or_update(
                    device_id=cloud_device_record.id,
                    dp_code=str(device_function.get("code")),
                    dp_type=DataPointType.CLOUD,
                    dp_name=str(device_function.get("code")),
                    dp_data_type=data_type,
                    dp_unit=str(function_spec.get("unit")),
                    dp_value_format=value_format,
                    dp_min_value=int(str(function_spec.get("min"))) if "min" in function_spec else None,
                    dp_max_value=int(str(function_spec.get("max"))) if "max" in function_spec else None,
                    dp_step_value=int(str(function_spec.get("step"))) if "step" in function_spec else None,
                    dp_queryable=existing_dp.queryable if existing_dp is not None else False,
                    dp_settable=True,
                )

            for device_status in device_statuses:
                existing_dp = self.__tuya_cloud_data_points_registry.get_by_code(
                    device_id=cloud_device_record.id,
                    dp_code=str(device_status.get("code")),
                )

                data_type = existing_dp.data_type if existing_dp is not None else DataType.UNKNOWN

                value_format = None

                function_type = str(device_status.get("type")).lower()

                if function_type == "boolean":
                    data_type = DataType.BOOLEAN

                if function_type == "integer":
                    data_type = DataType.INT

                if function_type == "enum":
                    data_type = DataType.ENUM

                    value_format = device_status.get("range")

                try:
                    function_spec = json.loads(str(device_status.get("values")))

                except json.JSONDecodeError:
                    function_spec = {}

                self.__tuya_cloud_data_points_registry.create_or_update(
                    device_id=cloud_device_record.id,
                    dp_code=str(device_status.get("code")),
                    dp_type=DataPointType.CLOUD,
                    dp_name=str(device_status.get("code")),
                    dp_data_type=data_type,
                    dp_unit=str(function_spec.get("unit")),
                    dp_value_format=value_format,
                    dp_min_value=int(str(function_spec.get("min"))) if "min" in function_spec else None,
                    dp_max_value=int(str(function_spec.get("max"))) if "max" in function_spec else None,
                    dp_step_value=int(str(function_spec.get("step"))) if "step" in function_spec else None,
                    dp_queryable=True,
                    dp_settable=existing_dp.settable if existing_dp is not None else False,
                )

            self.__consumer.append(
                entity=CloudDeviceFoundEntity(
                    device_identifier=cloud_device_record.id,
                )
            )

    # -----------------------------------------------------------------------------

    def __handle_check_local_devices(self) -> None:
        for discovered_device_record in self.__discovered_devices_registry:  # pylint: disable=too-many-nested-blocks
            cloud_device_record = self.__tuya_cloud_devices_registry.get_by_id(device_id=discovered_device_record.id)

            if cloud_device_record is None:
                continue

            local_device = DeviceLocalApi(
                device_identifier=discovered_device_record.id,
                local_key=cloud_device_record.local_key,
                ip_address=discovered_device_record.ip_address,
                protocol_version=discovered_device_record.version,
                logger=self.__logger,
            )

            local_device.connect()

            if local_device.is_connected():
                device_state = local_device.read_states()

                local_device.disconnect()

                if isinstance(device_state, dict):
                    device_dps = device_state.get("dps")

                    if isinstance(device_dps, dict):
                        for dp_index, dp_state in device_dps.items():
                            dp_data_type = DataType.UNKNOWN

                            if isinstance(dp_state, bool):
                                dp_data_type = DataType.BOOLEAN

                            if isinstance(dp_state, int):
                                dp_data_type = DataType.INT

                            if isinstance(dp_state, str):
                                dp_data_type = DataType.STRING

                            if isinstance(dp_state, dict):
                                if (  # pylint: disable=too-many-boolean-expressions
                                    "r" in dp_state and "g" in dp_state and "b" in dp_state
                                ) or ("h" in dp_state and "s" in dp_state and "v" in dp_state):
                                    dp_data_type = DataType.COLOR

                            self.__discovered_data_points_registry.create_or_update(
                                device_id=cloud_device_record.id,
                                dp_index=int(dp_index),
                                dp_type=DataPointType.LOCAL,
                                dp_data_type=dp_data_type,
                            )

            self.__consumer.append(
                entity=LocalDeviceFoundEntity(
                    device_identifier=discovered_device_record.id,
                )
            )

    # -----------------------------------------------------------------------------

    @staticmethod
    def __unpad(string: bytes) -> bytes:
        return string[: -ord(string[len(string) - 1 :])]

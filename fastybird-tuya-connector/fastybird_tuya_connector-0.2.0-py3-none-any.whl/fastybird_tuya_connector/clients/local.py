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
Tuya connector clients module device client
"""

# Python base dependencies
import asyncio
import ipaddress
import json
import logging
import time
import uuid
from asyncio import BaseTransport, Future, Task, Transport
from typing import Dict, Optional, Union

# Library dependencies
from fastybird_metadata.devices_module import ConnectionState
from tuyaface.const import CMD_TYPE

# Library libs
from fastybird_tuya_connector.consumers.consumer import Consumer
from fastybird_tuya_connector.consumers.entities import (
    DeviceStatusEntity,
    DpStatusEntity,
)
from fastybird_tuya_connector.logger import Logger
from fastybird_tuya_connector.protocol.local import TuyaLocalProtocol
from fastybird_tuya_connector.registry.model import (
    DataPointsRegistry,
    DevicesRegistry,
    PropertiesRegistry,
)
from fastybird_tuya_connector.types import (
    DataPointType,
    DeviceProperty,
    DeviceProtocolVersion,
)


class LocalDeviceClient:  # pylint: disable=too-few-public-methods
    """
    Tuya device local network client factory

    @package        FastyBird:TuyaConnector!
    @module         clients/local

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __consumer: Consumer

    __devices_registry: DevicesRegistry
    __properties_registry: PropertiesRegistry
    __data_points_registry: DataPointsRegistry

    __logger: Union[Logger, logging.Logger]

    __local_devices: Dict[str, "LocalDeviceItem"] = {}

    __DEVICE_UDP_PORT: int = 6668

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        consumer: Consumer,
        devices_registry: DevicesRegistry,
        properties_registry: PropertiesRegistry,
        data_points_registry: DataPointsRegistry,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__consumer = consumer
        self.__devices_registry = devices_registry
        self.__properties_registry = properties_registry
        self.__data_points_registry = data_points_registry

        self.__logger = logger

    # -----------------------------------------------------------------------------

    async def start(self) -> None:
        """Start local devices communication"""
        for device_record in self.__devices_registry:
            ip_address_property = self.__properties_registry.get_by_property(
                device_id=device_record.id,
                property_type=DeviceProperty.IP_ADDRESS,
            )

            if ip_address_property is None or ip_address_property.value is None:
                continue

            ip_address = ipaddress.IPv4Address(ip_address_property.value)

            if not ip_address.is_private:
                continue

            local_key_property = self.__properties_registry.get_by_property(
                device_id=device_record.id,
                property_type=DeviceProperty.LOCAL_KEY,
            )

            if local_key_property is None or local_key_property.value is None:
                continue

            result = await self.__create(
                device_id=device_record.id,
                device_identifier=device_record.identifier,
                ip_address=str(ip_address_property.value),
                device_key=str(local_key_property.value),
            )

            if result is not None:
                self.__local_devices[device_record.id.__str__()] = result

    # -----------------------------------------------------------------------------

    async def stop(self) -> None:
        """Stop local devices communication"""
        for local_device in self.__local_devices.values():
            await local_device.close()

    # -----------------------------------------------------------------------------

    async def __create(
        self,
        device_id: uuid.UUID,
        device_identifier: str,
        ip_address: str,
        device_key: str,
    ) -> Optional["LocalDeviceItem"]:
        loop = asyncio.get_running_loop()

        on_connected = loop.create_future()

        try:
            _, protocol = await loop.create_connection(
                protocol_factory=lambda: LocalDeviceItem(
                    device_id=device_id,
                    device_identifier=device_identifier,
                    device_key=device_key,
                    on_connected=on_connected,
                    consumer=self.__consumer,
                    properties_registry=self.__properties_registry,
                    data_points_registry=self.__data_points_registry,
                    logger=self.__logger,
                ),
                host=ip_address,
                port=self.__DEVICE_UDP_PORT,
            )

        except ConnectionRefusedError:
            self.__logger.error("Connection to device: %s:%s could not be established", device_identifier, ip_address)

            return None

        await asyncio.wait_for(on_connected, timeout=5)

        if not isinstance(protocol, LocalDeviceItem):
            raise Exception("Device instance could not be created")

        self.__logger.debug("Connected to local device: %s:%s", device_identifier, ip_address)

        return protocol


class LocalDeviceItem(asyncio.Protocol):  # pylint: disable=too-many-instance-attributes
    """
    Tuya device local network client

    @package        FastyBird:TuyaConnector!
    @module         clients/local

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __id: uuid.UUID

    __is_connected: bool = False

    __transport: Optional[Transport] = None

    __heartbeater: Optional[Task]
    __exchange: Optional[Task]

    __tuya_protocol: TuyaLocalProtocol

    __on_connected: Future

    __consumer: Consumer
    __properties_registry: PropertiesRegistry
    __data_points_registry: DataPointsRegistry

    __sequence_nr: int = 0

    __listeners: Dict[int, asyncio.Semaphore] = {}

    __logger: Union[Logger, logging.Logger]

    __last_reading_timestamp: float = 0.0

    __COMMUNICATION_INTERVAL: float = 0.5

    __HEARTBEAT_INTERVAL: float = 7.0
    __HEARTBEAT_SEQ_NO: int = -100

    __WAIT_FOR_REPLY_TIMEOUT: float = 5.0

    __DP_VALUE_RESEND_DELAY: float = 5.0

    __READ_STATE_DELAY: float = 5.0  # Delay between read state packets

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        consumer: Consumer,
        properties_registry: PropertiesRegistry,
        data_points_registry: DataPointsRegistry,
        device_identifier: str,
        device_key: str,
        on_connected: Future,
        gateway_identifier: Optional[str] = None,
        protocol_version: DeviceProtocolVersion = DeviceProtocolVersion.V33,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        super().__init__()

        self.__on_connected = on_connected

        self.__consumer = consumer

        self.__properties_registry = properties_registry
        self.__data_points_registry = data_points_registry

        self.__id = device_id

        self.__tuya_protocol = TuyaLocalProtocol(
            device_identifier=device_identifier,
            device_key=device_key,
            gateway_identifier=gateway_identifier if gateway_identifier is not None else device_identifier,
            protocol_version=protocol_version,
            logger=logger,
        )

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self.__is_connected

    # -----------------------------------------------------------------------------

    async def close(self) -> None:
        """Close connection to device"""
        if self.__heartbeater is not None:
            self.__heartbeater.cancel()

            try:
                await self.__heartbeater

            except asyncio.CancelledError:
                pass

            self.__heartbeater = None

        if self.__exchange is not None:
            self.__exchange.cancel()

            try:
                await self.__exchange

            except asyncio.CancelledError:
                pass

            self.__exchange = None

        if self.__transport is not None:
            transport = self.__transport
            self.__transport = None
            transport.close()

    # -----------------------------------------------------------------------------

    def connection_made(self, transport: BaseTransport) -> None:  # pylint: disable=too-many-statements
        """Connection to device was established"""
        if not isinstance(transport, Transport):
            raise Exception("Invalid connection transport created")

        async def heartbeat_loop() -> None:
            """Continuously send heart beat updates"""
            self.__logger.debug("Started device heartbeat loop")

            while True:
                try:
                    self.__logger.debug("(%s) PING", self.__id.__str__())

                    self.__send_request(command=CMD_TYPE.HEART_BEAT, sequence_nr=self.__HEARTBEAT_SEQ_NO)

                    await asyncio.sleep(self.__HEARTBEAT_INTERVAL)

                except asyncio.CancelledError:
                    self.__logger.debug("Stopped heartbeat loop")
                    raise

                except asyncio.TimeoutError:
                    self.__logger.debug("Heartbeat failed due to timeout, disconnecting")
                    break

                except Exception as ex:  # pylint: disable=broad-except
                    self.__logger.error("Heartbeat failed, disconnecting")
                    self.__logger.exception(ex)
                    break

            if self.__transport is not None:
                inner_transport = self.__transport
                self.__transport = None
                inner_transport.close()

        async def exchange_loop() -> None:  # pylint: disable=too-many-branches
            """Continuously send heart beat updates"""
            self.__logger.debug("Started device exchange loop")

            while True:  # pylint: disable=too-many-nested-blocks
                try:
                    for data_point_record in self.__data_points_registry.get_all_by_device(device_id=self.__id):
                        if data_point_record.type != DataPointType.LOCAL or data_point_record.index is None:
                            continue

                        if data_point_record.expected_value is not None:
                            if data_point_record.expected_value == data_point_record.actual_value:
                                self.__data_points_registry.set_expected_value(data_point=data_point_record, value=None)

                            elif (
                                data_point_record.expected_pending is None
                                or time.time() - data_point_record.expected_pending >= self.__DP_VALUE_RESEND_DELAY
                            ):
                                writing_result = await self.__write_state(
                                    value=data_point_record.expected_value,
                                    idx=data_point_record.index,
                                )

                                if writing_result is True:
                                    self.__data_points_registry.set_expected_pending(
                                        data_point=data_point_record,
                                        timestamp=time.time(),
                                    )

                    if (time.time() - self.__last_reading_timestamp) >= self.__READ_STATE_DELAY:
                        reading_result = await self.__read_states()

                        if reading_result is not None:
                            self.__last_reading_timestamp = time.time()

                    await asyncio.sleep(self.__COMMUNICATION_INTERVAL)

                except asyncio.CancelledError:
                    self.__logger.debug("Stopped exchange loop")
                    raise

                except asyncio.TimeoutError:
                    self.__logger.debug("Exchange failed due to timeout, disconnecting")
                    break

                except Exception as ex:  # pylint: disable=broad-except
                    self.__logger.error("Exchange failed, disconnecting")
                    self.__logger.exception(ex)
                    break

            if self.__transport is not None:
                inner_transport = self.__transport
                self.__transport = None
                inner_transport.close()

        self.__on_connected.set_result(True)

        self.__is_connected = True

        self.__transport = transport

        loop = asyncio.get_running_loop()

        self.__heartbeater = loop.create_task(heartbeat_loop())
        self.__exchange = loop.create_task(exchange_loop())

        device_state_property_record = self.__properties_registry.get_by_property(
            device_id=self.__id,
            property_type=DeviceProperty.STATE,
        )

        if device_state_property_record is not None:
            self.__properties_registry.set_value(
                device_property=device_state_property_record,
                value=ConnectionState.CONNECTED.value,
            )

    # -----------------------------------------------------------------------------

    def data_received(self, data: bytes) -> None:
        """Data were received from device"""
        for reply in self.__tuya_protocol.decode_payload(raw_reply=data):  # pylint: disable=too-many-nested-blocks
            if "seq" in reply and reply.get("seq") in self.__listeners:
                sem = self.__listeners[reply.get("seq")]
                self.__listeners[reply.get("seq")] = reply
                sem.release()

            elif reply.get("cmd") == CMD_TYPE.HEART_BEAT:
                self.__logger.debug("(%s) PONG", self.__id.__str__())

            elif reply.get("cmd") == CMD_TYPE.STATUS:
                devices_data = reply.get("data")

                self.__handle_received_dps(message=devices_data)

            else:
                pass

    # -----------------------------------------------------------------------------

    def connection_lost(self, exc: Optional[Exception]) -> None:
        """Connection with device was lost"""
        self.__logger.debug("Connection lost: %s", exc)

        self.__is_connected = False

        device_state_property_record = self.__properties_registry.get_by_property(
            device_id=self.__id,
            property_type=DeviceProperty.STATE,
        )

        if device_state_property_record is not None:
            self.__properties_registry.set_value(
                device_property=device_state_property_record,
                value=ConnectionState.CONNECTED.value,
            )

    # -----------------------------------------------------------------------------

    async def __read_states(self) -> bool:
        """Get device status"""
        sequence_nr = self.__send_request(command=CMD_TYPE.DP_QUERY)

        try:
            msg = await self.__wait_for_reply(sequence_nr=sequence_nr)

            if isinstance(msg, dict):
                data = msg.get("data")

                if isinstance(data, str):
                    self.__handle_received_dps(message=data)

                return True

        except asyncio.TimeoutError:
            pass

        return False

    # -----------------------------------------------------------------------------

    async def __write_states(self, value: Dict[Union[str, int], Union[int, float, bool, str]]) -> bool:
        """Set device status"""
        sequence_nr = self.__send_request(command=CMD_TYPE.CONTROL, payload={str(k): v for k, v in value.items()})

        try:
            msg = await self.__wait_for_reply(sequence_nr=sequence_nr)

        except asyncio.TimeoutError:
            return False

        return msg is not None

    # -----------------------------------------------------------------------------

    async def __write_state(self, value: Union[int, float, bool, str], idx: int = 1) -> bool:
        """Set state"""
        return await self.__write_states({idx: value})

    # -----------------------------------------------------------------------------

    def __send_request(
        self,
        command: CMD_TYPE = CMD_TYPE.DP_QUERY,
        payload: Optional[Dict[Union[str, int], Union[int, float, bool, str]]] = None,
        sequence_nr: Optional[int] = None,
    ) -> int:
        if not sequence_nr:
            self.__sequence_nr = self.__sequence_nr + 1

            payload_sequence_nr = self.__sequence_nr

        else:
            payload_sequence_nr = sequence_nr

        request = self.__tuya_protocol.build_payload(
            sequence_nr=self.__sequence_nr,
            command=command,
            data=payload,
        )

        self.__logger.debug(
            "(%s) sending msg (seq %s): [%x:%s] payload: [%s]",
            self.__id.__str__(),
            payload_sequence_nr,
            command,
            CMD_TYPE(command).name,
            payload,
        )

        if self.__transport is not None:
            self.__transport.write(request)

        return self.__sequence_nr

    # -----------------------------------------------------------------------------

    async def __wait_for_reply(self, sequence_nr: int) -> asyncio.Semaphore:
        if sequence_nr in self.__listeners:
            raise Exception(f"listener exists for {sequence_nr}")

        self.__listeners[sequence_nr] = asyncio.Semaphore(0)

        try:
            await asyncio.wait_for(self.__listeners[sequence_nr].acquire(), self.__WAIT_FOR_REPLY_TIMEOUT)

        except asyncio.TimeoutError:
            del self.__listeners[sequence_nr]

            raise

        return self.__listeners.pop(sequence_nr)

    # -----------------------------------------------------------------------------

    def __handle_received_dps(self, message: str) -> None:
        try:
            decoded = json.loads(message)

            if isinstance(decoded, dict):
                dps = decoded.get("dps")

                if isinstance(dps, dict):
                    entity = DeviceStatusEntity(
                        device_identifier=str(decoded.get("devId")),
                    )

                    for dp_index, dp_value in dps.items():
                        entity.add_dps_state(
                            DpStatusEntity(
                                device_identifier=str(decoded.get("devId")),
                                dp_index=int(dp_index),
                                dp_value=dp_value,
                            )
                        )

                    self.__consumer.append(entity=entity)

        except json.JSONDecodeError:
            pass

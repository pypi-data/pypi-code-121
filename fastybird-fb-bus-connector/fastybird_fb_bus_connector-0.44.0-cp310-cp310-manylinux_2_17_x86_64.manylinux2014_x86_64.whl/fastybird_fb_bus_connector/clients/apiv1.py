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
FastyBird BUS connector clients module client for API v1
"""

# pylint: disable=too-many-lines

# Python base dependencies
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Set, Union

# Library dependencies
from fastybird_metadata.devices_module import ConnectionState, DeviceAttributeName
from fastybird_metadata.types import ButtonPayload, DataType, SwitchPayload
from kink import inject

# Library libs
from fastybird_fb_bus_connector.api.v1builder import V1Builder
from fastybird_fb_bus_connector.clients.client import IClient
from fastybird_fb_bus_connector.exceptions import (
    BuildPayloadException,
    InvalidStateException,
)
from fastybird_fb_bus_connector.logger import Logger
from fastybird_fb_bus_connector.registry.model import (
    DevicesRegistry,
    DiscoveredDevicesRegistry,
    DiscoveredRegistersRegistry,
    RegistersRegistry, DevicesAttributesRegistry,
)
from fastybird_fb_bus_connector.registry.records import (
    DeviceRecord,
    DiscoveredAttributeRegisterRecord,
    DiscoveredDeviceRecord,
    DiscoveredInputRegisterRecord,
    DiscoveredOutputRegisterRecord,
    DiscoveredRegisterRecord,
    RegisterRecord,
)
from fastybird_fb_bus_connector.transporters.transporter import ITransporter
from fastybird_fb_bus_connector.types import (
    UNASSIGNED_ADDRESS,
    DeviceProperty,
    Packet,
    RegisterType,
)


@inject(alias=IClient)
class ApiV1Client(IClient):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Communication client for API v1

    @package        FastyBird:FbBusConnector!
    @module         clients/apiv1

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __discovery_enabled: bool = False

    __devices_registry: DevicesRegistry
    __devices_attributes_registry: DevicesAttributesRegistry
    __registers_registry: RegistersRegistry

    __discovered_devices_registry: DiscoveredDevicesRegistry
    __discovered_registers_registry: DiscoveredRegistersRegistry

    __transporter: ITransporter

    __discovery_attempts: int = 0
    __discovery_total_attempts: int = 0
    __discovery_broadcasting_finished: bool = False
    __discovery_last_broadcast_request_send_timestamp: float = 0.0

    __processed_devices: List[str] = []
    __processed_devices_registers: Dict[str, Dict[int, Set[str]]] = {}

    __logger: Union[Logger, logging.Logger]

    __MAX_TRANSMIT_ATTEMPTS: int = 5  # Maximum count of sending packets before gateway mark device as lost

    __PING_DELAY: float = 15.0  # Delay between pings packets
    __READ_STATE_DELAY: float = 5.0  # Delay between read state packets
    __READ_WAITING: float = 0.5  # Waiting delay after packet is sent
    __WRITE_WAITING: float = 0.5  # Waiting delay after packet is sent

    __DISCOVERY_MAX_ATTEMPTS: int = 5  # Maxim count of sending search device packets
    __DISCOVERY_MAX_TOTAL_ATTEMPTS: int = (
        100  # Maximum total count of packets before gateway mark paring as unsuccessful
    )
    __DISCOVERY_BROADCAST_DELAY: float = 2.0  # Waiting delay before another broadcast is sent
    __DISCOVERY_DEVICE_DELAY: float = 5.0  # Waiting delay paring is marked as unsuccessful
    __DISCOVERY_BROADCAST_WAITING_DELAY: float = 2.0  # Maximum time gateway will wait for reply during broadcasting

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        devices_registry: DevicesRegistry,
        devices_attributes_registry: DevicesAttributesRegistry,
        registers_registry: RegistersRegistry,
        discovered_devices_registry: DiscoveredDevicesRegistry,
        discovered_registers_registry: DiscoveredRegistersRegistry,
        transporter: ITransporter,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__devices_registry = devices_registry
        self.__devices_attributes_registry = devices_attributes_registry
        self.__registers_registry = registers_registry

        self.__discovered_devices_registry = discovered_devices_registry
        self.__discovered_registers_registry = discovered_registers_registry

        self.__transporter = transporter

        self.__logger = logger

        self.__processed_devices = []
        self.__processed_devices_registers = {}

    # -----------------------------------------------------------------------------

    def enable_discovery(self) -> None:
        """Enable client devices discovery"""
        self.__discovery_enabled = True

        self.__logger.info("Discovery mode is activated")

    # -----------------------------------------------------------------------------

    def disable_discovery(self) -> None:
        """Disable client devices discovery"""
        self.__discovery_enabled = False

        self.__discovery_total_attempts = 0
        self.__discovery_last_broadcast_request_send_timestamp = 0.0
        self.__discovery_total_attempts = 0
        self.__discovery_attempts = 0

        self.__discovery_broadcasting_finished = False

        self.__discovered_devices_registry.reset()

        self.__logger.info("Discovery mode is deactivated")

    # -----------------------------------------------------------------------------

    def handle(self) -> None:
        """Handle connected devices"""
        if self.__transporter.packet_to_be_sent > 0:
            return

        if self.__discovery_enabled:
            self.__process_discovery()

        else:
            for device in self.__devices_registry:
                if not device.enabled:
                    continue

                if device.id.__str__() not in self.__processed_devices:
                    self.__process_device(device=device)

                    self.__processed_devices.append(device.id.__str__())

                    return

            self.__processed_devices = []

    # -----------------------------------------------------------------------------

    def __process_device(  # pylint: disable=too-many-return-statements,too-many-branches
        self,
        device: DeviceRecord,
    ) -> None:
        """Handle client read or write message to device"""
        device_address = self.__devices_registry.get_address(device=device)

        if device_address is None:
            self.__logger.error(
                "Device address could not be fetched from registry. Device is disabled and have to be re-discovered",
                extra={
                    "device": {
                        "id": device.id.__str__(),
                        "serial_number": device.serial_number,
                    },
                },
            )

            self.__devices_registry.disable(device=device)

            return

        # Maximum send packet attempts was reached device is now marked as lost
        if device.transmit_attempts >= self.__MAX_TRANSMIT_ATTEMPTS:
            if device.is_lost:
                self.__logger.info(
                    "Device with address: %s is still lost",
                    device_address,
                    extra={
                        "device": {
                            "id": device.id.__str__(),
                            "serial_number": device.serial_number,
                            "address": device_address,
                        },
                    },
                )

                try:
                    self.__devices_registry.set_state(device=device, state=ConnectionState.LOST)

                except InvalidStateException:
                    self.__logger.error(
                        "Device state could not be updated. Device is disabled and have to be re-discovered",
                        extra={
                            "device": {
                                "id": device.id.__str__(),
                                "serial_number": device.serial_number,
                            },
                        },
                    )

                    self.__devices_registry.disable(device=device)

                    return

            else:
                self.__logger.info(
                    "Device with address: %s is lost",
                    device_address,
                    extra={
                        "device": {
                            "id": device.id.__str__(),
                            "serial_number": device.serial_number,
                            "address": device_address,
                        },
                    },
                )

                try:
                    self.__devices_registry.set_state(device=device, state=ConnectionState.LOST)

                except InvalidStateException:
                    self.__logger.error(
                        "Device state could not be updated. Device is disabled and have to be re-discovered",
                        extra={
                            "device": {
                                "id": device.id.__str__(),
                                "serial_number": device.serial_number,
                            },
                        },
                    )

                    self.__devices_registry.disable(device=device)

            return

        # Device state is lost...
        if device.is_lost:
            # ...wait for ping delay...
            if (time.time() - device.last_misc_packet_timestamp) >= self.__PING_DELAY:
                # ...then try to PING device
                self.__send_ping_handler(device=device, device_address=device_address)

            return

        # Device state is unknown...
        if self.__devices_registry.is_device_unknown(device=device):
            # ...wait for read state delay...
            if (time.time() - device.last_misc_packet_timestamp) >= self.__READ_STATE_DELAY:
                # ...ask device for its state
                self.__send_read_device_state_handler(device=device, device_address=device_address)

            return

        # Check if device is in RUNNING mode
        if not self.__devices_registry.is_device_running(device=device):
            return

        if self.__write_register_handler(device=device, device_address=device_address):
            return

        self.__read_registers_handler(device=device, device_address=device_address)

    # -----------------------------------------------------------------------------

    def __process_discovery(self) -> None:
        """Handle discovery process"""
        # Connector protection
        if self.__discovery_total_attempts >= self.__DISCOVERY_MAX_TOTAL_ATTEMPTS:
            self.__logger.info("Maximum attempts reached. Disabling discovery procedure to prevent infinite loop")

            self.disable_discovery()

            return

        if not self.__discovery_broadcasting_finished:
            # Check if search counter is reached
            if self.__discovery_attempts < self.__DISCOVERY_MAX_ATTEMPTS:
                # Search timeout is not reached, new devices could be searched
                if (
                    self.__discovery_last_broadcast_request_send_timestamp == 0
                    or time.time() - self.__discovery_last_broadcast_request_send_timestamp
                    >= self.__DISCOVERY_BROADCAST_DELAY
                ):
                    # Broadcast discovery request for new device
                    self.__broadcast_discover_devices_handler()

            # Searching for devices finished
            else:
                self.__discovery_broadcasting_finished = True

                self.__discovered_devices_registry.prepare_devices()

            return

        # Check if some devices are in queue
        if len(self.__discovered_devices_registry) == 0:
            self.disable_discovery()

            return

        # Device for discovery is assigned
        for discovered_device in self.__discovered_devices_registry:
            # Max device discovery attempts were reached
            if discovered_device.transmit_attempts >= self.__MAX_TRANSMIT_ATTEMPTS or (
                discovered_device.last_packet_timestamp != 0.0
                and time.time() - discovered_device.last_packet_timestamp >= self.__DISCOVERY_DEVICE_DELAY
            ):
                self.__logger.warning(
                    "Discovery could not be finished, device: %s is lost. Moving to next device in queue",
                    discovered_device.serial_number,
                    extra={
                        "device": {
                            "serial_number": discovered_device.serial_number,
                            "address": discovered_device.address,
                        },
                    },
                )

                # Move to next device in queue
                self.__discovered_devices_registry.remove(serial_number=discovered_device.serial_number)

                return

            # Packet was sent to device, waiting for device reply
            if discovered_device.waiting_for_packet:
                return

            # Check if are some registers left for initialization
            register_record = next(
                iter(
                    [
                        register
                        for register in self.__discovered_registers_registry.get_all_by_device(
                            device_serial_number=discovered_device.serial_number
                        )
                        if register.data_type == DataType.UNKNOWN
                    ]
                ),
                None,
            )

            if register_record is not None:
                self.__send_provide_register_structure_handler(
                    discovered_device=discovered_device,
                    discovered_register=register_record,
                )

            # Set device to operating mode
            else:
                self.__send_finalize_device_discovery_handler(discovered_device=discovered_device)

    # -----------------------------------------------------------------------------

    def __send_ping_handler(self, device: DeviceRecord, device_address: int) -> None:
        result = self.__transporter.send_packet(
            address=device_address,
            payload=V1Builder.build_ping(),
            waiting_time=self.__READ_WAITING,
        )

        self.__devices_registry.set_misc_packet_timestamp(device=device, success=result)

    # -----------------------------------------------------------------------------

    def __send_read_device_state_handler(self, device: DeviceRecord, device_address: int) -> None:
        state_attribute = self.__registers_registry.get_by_name(device_id=device.id, name=DeviceProperty.STATE.value)

        if state_attribute is None:
            self.__logger.error(
                "Device state attribute register could not be fetched from registry",
                extra={
                    "device": {
                        "id": device.id.__str__(),
                        "serial_number": device.serial_number,
                    },
                },
            )

            return

        output_content = V1Builder.build_read_single_register_value(
            register_type=state_attribute.type,
            register_address=state_attribute.address,
        )

        result = self.__transporter.send_packet(
            address=device_address,
            payload=output_content,
            waiting_time=self.__READ_WAITING,
        )

        self.__devices_registry.set_misc_packet_timestamp(device=device, success=result)

    # -----------------------------------------------------------------------------

    def __write_register_handler(self, device: DeviceRecord, device_address: int) -> bool:
        for register_type in (RegisterType.OUTPUT, RegisterType.ATTRIBUTE):
            registers = self.__registers_registry.get_all_for_device(
                device_id=device.id,
                register_type=register_type,
            )

            for register in registers:
                if register.expected_value is not None and register.expected_pending is None:
                    if self.__write_value_to_single_register(
                        device=device,
                        device_address=device_address,
                        register=register,
                        write_value=register.expected_value,
                    ):
                        return True

        return False

    # -----------------------------------------------------------------------------

    def __read_registers_handler(  # pylint: disable=too-many-return-statements,too-many-branches
        self,
        device: DeviceRecord,
        device_address: int,
    ) -> None:
        """Process devices registers reading"""
        for registers_type in [  # pylint: disable=too-many-nested-blocks
            RegisterType.INPUT,
            RegisterType.OUTPUT,
            RegisterType.ATTRIBUTE,
        ]:
            if device.id.__str__() not in self.__processed_devices_registers:
                self.__processed_devices_registers[device.id.__str__()] = {}

            if registers_type.value not in self.__processed_devices_registers[device.id.__str__()]:
                self.__processed_devices_registers[device.id.__str__()][registers_type.value] = set()

            processed_length = len(self.__processed_devices_registers[device.id.__str__()][registers_type.value])

            registers = self.__registers_registry.get_all_for_device(
                device_id=device.id,
                register_type=registers_type,
            )

            if registers_type == RegisterType.ATTRIBUTE:
                registers = [register for register in registers if register.queryable]

            if 0 < len(registers) != processed_length:
                # Try to read all registers of one type at once
                if registers_type != RegisterType.ATTRIBUTE and self.__is_all_registers_readable(
                    device=device, registers_count=len(registers)
                ):
                    self.__read_multiple_registers(
                        device=device,
                        device_address=device_address,
                        registers_type=registers_type,
                        registers_count=len(registers),
                    )

                    for register in registers:
                        self.__processed_devices_registers[device.id.__str__()][registers_type.value].add(
                            register.id.__str__(),
                        )

                    return

                # Registers have to be read one by one
                for register in registers:
                    if (
                        register.id.__str__()
                        in self.__processed_devices_registers[device.id.__str__()][registers_type.value]
                    ):
                        continue

                    self.__read_single_register(
                        device=device,
                        device_address=device_address,
                        register_type=registers_type,
                        register_address=register.address,
                    )

                    self.__processed_devices_registers[device.id.__str__()][registers_type.value].add(
                        register.id.__str__(),
                    )

                    return

        if time.time() - device.last_reading_packet_timestamp < device.sampling_time:
            return

        for registers_type in [  # pylint: disable=too-many-nested-blocks
            RegisterType.INPUT,
            RegisterType.OUTPUT,
            RegisterType.ATTRIBUTE,
        ]:
            self.__processed_devices_registers[device.id.__str__()][registers_type.value] = set()

    # -----------------------------------------------------------------------------

    def __broadcast_discover_devices_handler(self) -> None:
        """Broadcast devices discovery packet to bus"""
        # Set counters & flags...
        self.__discovery_attempts += 1
        self.__discovery_total_attempts += 1
        self.__discovery_last_broadcast_request_send_timestamp = time.time()

        self.__logger.debug("Preparing to broadcast search devices")

        self.__transporter.broadcast_packet(
            payload=V1Builder.build_discovery(),
            waiting_time=self.__DISCOVERY_BROADCAST_WAITING_DELAY,
        )

    # -----------------------------------------------------------------------------

    def __send_provide_register_structure_handler(
        self,
        discovered_device: DiscoveredDeviceRecord,
        discovered_register: DiscoveredRegisterRecord,
    ) -> None:
        """We know basic device structure, let's get structure for each register"""
        output_content = V1Builder.build_read_single_register_structure(
            register_type=discovered_register.type,
            register_address=discovered_register.address,
            serial_number=(
                discovered_device.serial_number if discovered_device.address == UNASSIGNED_ADDRESS else None
            ),
        )

        # Mark that gateway is waiting for reply from device...
        self.__discovered_devices_registry.set_waiting_for_packet(
            device=discovered_device,
            packet_type=Packet.READ_SINGLE_REGISTER_STRUCTURE,
        )

        self.__discovery_total_attempts += 1

        if discovered_device.address == UNASSIGNED_ADDRESS:
            self.__transporter.broadcast_packet(
                payload=output_content,
                waiting_time=self.__DISCOVERY_BROADCAST_WAITING_DELAY,
            )

        else:
            result = self.__transporter.send_packet(
                address=discovered_device.address,
                payload=output_content,
            )

            if result is False:
                # Mark that gateway is not waiting any reply from device
                self.__discovered_devices_registry.set_waiting_for_packet(device=discovered_device, packet_type=None)

    # -----------------------------------------------------------------------------

    def __send_finalize_device_discovery_handler(self, discovered_device: DiscoveredDeviceRecord) -> None:
        existing_device = self.__devices_registry.get_by_serial_number(serial_number=discovered_device.serial_number)

        if (
            # New device is without bus address
            discovered_device.address == UNASSIGNED_ADDRESS
            or (
                # Or device bus address is different from stored in connector registry
                existing_device is not None
                and discovered_device.address != self.__devices_registry.get_address(device=existing_device)
                and self.__devices_registry.get_address(device=existing_device) is not None
            )
        ):
            # Bus address have to be updated to correct one
            self.__write_discovered_device_new_address(
                discovered_device=discovered_device,
            )

        # No other actions are required...
        else:
            # Device could be restarted to running mode
            self.__write_discovered_device_state(
                discovered_device=discovered_device,
            )

        # Move to next device in queue
        self.__discovered_devices_registry.remove(serial_number=discovered_device.serial_number)

    # -----------------------------------------------------------------------------

    def __read_single_register(  # pylint: disable=too-many-branches
        self,
        device: DeviceRecord,
        device_address: int,
        register_type: RegisterType,
        register_address: int,
    ) -> None:
        output_content = V1Builder.build_read_single_register_value(
            register_type=register_type,
            register_address=register_address,
        )

        result = self.__transporter.send_packet(
            address=device_address,
            payload=output_content,
            waiting_time=self.__READ_WAITING,
        )

        self.__devices_registry.set_read_packet_timestamp(device=device, success=result)

    # -----------------------------------------------------------------------------

    def __read_multiple_registers(  # pylint: disable=too-many-branches
        self,
        device: DeviceRecord,
        device_address: int,
        registers_type: RegisterType,
        registers_count: int,
    ) -> None:
        start_address = 0

        output_content = V1Builder.build_read_multiple_registers_values(
            register_type=registers_type,
            start_address=start_address,
            registers_count=registers_count,
        )

        result = self.__transporter.send_packet(
            address=device_address,
            payload=output_content,
            waiting_time=self.__READ_WAITING,
        )

        self.__devices_registry.set_read_packet_timestamp(device=device, success=result)

    # -----------------------------------------------------------------------------

    def __write_value_to_single_register(
        self,
        device: DeviceRecord,
        device_address: int,
        register: RegisterRecord,
        write_value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload],
    ) -> bool:
        try:
            output_content = V1Builder.build_write_single_register_value(
                register_type=register.type,
                register_address=register.address,
                register_data_type=register.data_type,
                register_name=None,
                write_value=write_value,
            )

        except BuildPayloadException as ex:
            self.__logger.error(
                "Value couldn't be written into register",
                extra={
                    "device": {
                        "id": device.id.__str__(),
                    },
                    "register": {
                        "address": register.address,
                        "type": register.type.value,
                        "data_type": register.data_type.value,
                    },
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )
            self.__logger.exception(ex)

            # There is some problem with transforming expected value, write is skipped & cleared
            self.__registers_registry.set_expected_value(register=register, value=None)

            return False

        result = self.__transporter.send_packet(
            address=device_address,
            payload=output_content,
            waiting_time=self.__WRITE_WAITING,
        )

        if result:
            self.__registers_registry.set_expected_pending(register=register, timestamp=time.time())

        # Update communication timestamp
        self.__devices_registry.set_write_packet_timestamp(device=device, success=result)

        return result

    # -----------------------------------------------------------------------------

    def __write_discovered_device_new_address(
        self,
        discovered_device: DiscoveredDeviceRecord,
    ) -> None:
        """Discovered device is without address or with different address. Let's try to write new address to device"""
        address_register = next(
            iter(
                [
                    register
                    for register in self.__discovered_registers_registry.get_all_by_device(
                        device_serial_number=discovered_device.serial_number
                    )
                    if isinstance(register, DiscoveredAttributeRegisterRecord)
                       and register.name == DeviceProperty.ADDRESS.value
                ]
            ),
            None,
        )

        if address_register is None:
            self.__logger.warning(
                "Register with stored address of discovered device could not be loaded. Discovery couldn't be finished",
                extra={
                    "device": {
                        "serial_number": discovered_device.serial_number,
                        "address": discovered_device.address,
                    },
                },
            )

            return

        # Discovered device actual address
        actual_address = discovered_device.address

        # Assign new address to device
        free_address = self.__devices_registry.find_free_address()

        if free_address is None:
            self.__logger.warning(
                "No free address for new device is available. Discovery couldn't be finished",
                extra={
                    "device": {
                        "serial_number": discovered_device.serial_number,
                        "address": discovered_device.address,
                    },
                },
            )

            return

        discovered_device.address = free_address

        updated_device = self.__devices_registry.get_by_serial_number(serial_number=discovered_device.serial_number)

        if updated_device is not None:
            updated_device_address = self.__devices_registry.get_address(device=updated_device)

            if updated_device_address is not None and updated_device_address != UNASSIGNED_ADDRESS:
                # Use address stored before
                discovered_device.address = updated_device_address

        try:
            output_content = V1Builder.build_write_single_register_value(
                register_type=address_register.type,
                register_address=address_register.address,
                register_data_type=address_register.data_type,
                register_name=address_register.name,
                write_value=discovered_device.address,
                serial_number=(discovered_device.serial_number if actual_address == UNASSIGNED_ADDRESS else None),
            )

        except BuildPayloadException as ex:
            self.__logger.warning(
                "New device address couldn't be written into register. Discovery couldn't be finished",
                extra={
                    "device": {
                        "serial_number": discovered_device.serial_number,
                        "address": discovered_device.address,
                    },
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )
            self.__logger.exception(ex)

            return

        # Data to write are ready to be broadcast, lets persist device into registry
        self.__finalize_discovered_device(discovered_device=discovered_device)

        # After device update their address, it should be restarted in running mode
        if actual_address == UNASSIGNED_ADDRESS:
            self.__transporter.broadcast_packet(
                payload=output_content,
                waiting_time=self.__DISCOVERY_BROADCAST_WAITING_DELAY,
            )

        else:
            result = self.__transporter.send_packet(
                address=actual_address,
                payload=output_content,
                waiting_time=self.__DISCOVERY_BROADCAST_WAITING_DELAY,
            )

            if result is False:
                self.__logger.warning(
                    "Device address couldn't written into device. Device have to be discovered again",
                    extra={
                        "device": {
                            "serial_number": discovered_device.serial_number,
                            "address": discovered_device.address,
                        },
                    },
                )

    # -----------------------------------------------------------------------------

    def __write_discovered_device_state(
        self,
        discovered_device: DiscoveredDeviceRecord,
    ) -> None:
        """Discovered device is ready to be used. Discoverable mode have to be deactivated"""
        state_register = next(
            iter(
                [
                    register
                    for register in self.__discovered_registers_registry.get_all_by_device(
                        device_serial_number=discovered_device.serial_number
                    )
                    if isinstance(register, DiscoveredAttributeRegisterRecord)
                       and register.name == DeviceProperty.STATE.value
                ]
            ),
            None,
        )

        if state_register is None:
            self.__logger.warning(
                "Register with stored state could not be loaded. Discovery couldn't be finished",
                extra={
                    "device": {
                        "serial_number": discovered_device.serial_number,
                        "address": discovered_device.address,
                    },
                },
            )

            return

        try:
            output_content = V1Builder.build_write_single_register_value(
                register_type=state_register.type,
                register_address=state_register.address,
                register_data_type=state_register.data_type,
                register_name=state_register.name,
                write_value=ConnectionState.RUNNING.value,
            )

        except BuildPayloadException as ex:
            self.__logger.warning(
                "Device state couldn't be written into register. Discovery couldn't be finished",
                extra={
                    "device": {
                        "serial_number": discovered_device.serial_number,
                        "address": discovered_device.address,
                    },
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )
            self.__logger.exception(ex)

            return

        # Data to write are ready to be broadcast, lets persist device into registry
        self.__finalize_discovered_device(discovered_device=discovered_device)

        # When device state is changed, discovery mode will be deactivated
        result = self.__transporter.send_packet(
            address=discovered_device.address,
            payload=output_content,
        )

        if result is False:
            self.__logger.warning(
                "Device state couldn't written into device. State have to be changed manually",
                extra={
                    "device": {
                        "serial_number": discovered_device.serial_number,
                        "address": discovered_device.address,
                    },
                },
            )

    # -----------------------------------------------------------------------------

    def __finalize_discovered_device(
        self,
        discovered_device: DiscoveredDeviceRecord,
    ) -> None:
        """Persist discovered device into connector registry"""
        existing_device = self.__devices_registry.get_by_serial_number(serial_number=discovered_device.serial_number)

        device_record = self.__devices_registry.create_or_update(
            device_id=uuid.uuid4() if existing_device is None else existing_device.id,
            device_serial_number=discovered_device.serial_number,
            device_enabled=False,
        )

        self.__devices_attributes_registry.create_or_update(
            device_id=device_record.id,
            attribute_id=uuid.uuid4(),
            attribute_identifier=DeviceAttributeName.HARDWARE_MANUFACTURER.value,
            attribute_value=discovered_device.hardware_manufacturer,
        )

        self.__devices_attributes_registry.create_or_update(
            device_id=device_record.id,
            attribute_id=uuid.uuid4(),
            attribute_identifier=DeviceAttributeName.HARDWARE_MODEL.value,
            attribute_value=discovered_device.hardware_model,
        )

        self.__devices_attributes_registry.create_or_update(
            device_id=device_record.id,
            attribute_id=uuid.uuid4(),
            attribute_identifier=DeviceAttributeName.HARDWARE_VERSION.value,
            attribute_value=discovered_device.hardware_version,
        )

        self.__devices_attributes_registry.create_or_update(
            device_id=device_record.id,
            attribute_id=uuid.uuid4(),
            attribute_identifier=DeviceAttributeName.FIRMWARE_MANUFACTURER.value,
            attribute_value=discovered_device.firmware_manufacturer,
        )

        self.__devices_attributes_registry.create_or_update(
            device_id=device_record.id,
            attribute_id=uuid.uuid4(),
            attribute_identifier=DeviceAttributeName.FIRMWARE_VERSION.value,
            attribute_value=discovered_device.firmware_version,
        )

        for register in self.__discovered_registers_registry.get_all_by_device(
            device_serial_number=discovered_device.serial_number
        ):
            existing_register = self.__registers_registry.get_by_address(
                device_id=device_record.id, register_type=register.type, register_address=register.address
            )

            if isinstance(register, (DiscoveredInputRegisterRecord, DiscoveredOutputRegisterRecord)):
                self.__registers_registry.create_or_update(
                    device_id=device_record.id,
                    register_id=uuid.uuid4() if existing_register is None else existing_register.id,
                    register_type=register.type,
                    register_address=register.address,
                    register_data_type=register.data_type,
                )

            elif isinstance(register, DiscoveredAttributeRegisterRecord):
                attribute_register = self.__registers_registry.create_or_update(
                    device_id=device_record.id,
                    register_id=uuid.uuid4() if existing_register is None else existing_register.id,
                    register_type=register.type,
                    register_address=register.address,
                    register_data_type=register.data_type,
                    register_name=register.name,
                    register_queryable=register.queryable,
                    register_settable=register.settable,
                )

                if register.name == DeviceProperty.ADDRESS.value:
                    self.__registers_registry.set_actual_value(
                        register=attribute_register,
                        value=discovered_device.address,
                    )

                if register.name == DeviceProperty.STATE.value:
                    self.__registers_registry.set_actual_value(
                        register=attribute_register,
                        value=discovered_device.state.value,
                    )

                if register.name == DeviceProperty.MAX_PACKET_LENGTH.value:
                    self.__registers_registry.set_actual_value(
                        register=attribute_register,
                        value=discovered_device.max_packet_length,
                    )

        # Device initialization is finished, enable it for communication
        device_record = self.__devices_registry.enable(device=device_record)

        try:
            # Update device state
            device_record = self.__devices_registry.set_state(device=device_record, state=ConnectionState.UNKNOWN)

            self.__devices_registry.enable(device=device_record)

        except InvalidStateException:
            self.__logger.error(
                "Device state could not be updated. Device is disabled and have to be re-discovered",
                extra={
                    "device": {
                        "id": device_record.id.__str__(),
                        "serial_number": device_record.serial_number,
                    },
                },
            )

            self.__devices_registry.disable(device=device_record)

        # Update last packet sent status
        self.__devices_registry.set_misc_packet_timestamp(device=device_record)

    # -----------------------------------------------------------------------------

    def __is_all_registers_readable(self, device: DeviceRecord, registers_count: int) -> bool:
        """Check if all registers could be read at once"""
        # Calculate maximum count registers per one packet
        # e.g. max_packet_length = 24 => max_readable_registers_count = 4
        #   - only 4 registers could be read in one packet
        max_readable_registers_count = (
            self.__devices_registry.get_max_packet_length_for_device(device=device) - 8
        ) // 4

        return max_readable_registers_count >= registers_count

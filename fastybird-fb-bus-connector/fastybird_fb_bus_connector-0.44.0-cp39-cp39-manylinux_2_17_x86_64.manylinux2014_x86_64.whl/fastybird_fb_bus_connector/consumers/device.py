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
FastyBird BUS connector consumers module consumer for device messages
"""

# Library dependencies
import logging
from datetime import datetime
from typing import Union

from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.types import ButtonPayload, SwitchPayload
from kink import inject

from fastybird_fb_bus_connector.consumers.consumer import IConsumer
from fastybird_fb_bus_connector.consumers.entities import (
    BaseEntity,
    DeviceDiscoveryEntity,
    MultipleRegistersEntity,
    PongEntity,
    RegisterStructureEntity,
    SingleRegisterEntity,
)

# Library libs
from fastybird_fb_bus_connector.exceptions import InvalidStateException
from fastybird_fb_bus_connector.logger import Logger
from fastybird_fb_bus_connector.registry.model import (
    DevicesRegistry,
    DiscoveredDevicesRegistry,
    DiscoveredRegistersRegistry,
    RegistersRegistry,
)
from fastybird_fb_bus_connector.registry.records import RegisterRecord
from fastybird_fb_bus_connector.types import RegisterType


@inject(alias=IConsumer)
class DeviceItemConsumer(IConsumer):  # pylint: disable=too-few-public-methods
    """
    BUS messages consumer for devices messages

    @package        FastyBird:FbBusConnector!
    @module         consumers/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry

    __logger: Union[Logger, logging.Logger]

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        devices_registry: DevicesRegistry,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__devices_registry = devices_registry

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def consume(self, entity: BaseEntity) -> None:
        """Consume received message"""
        if not isinstance(entity, PongEntity):
            return

        device_record = self.__devices_registry.get_by_address(address=entity.device_address)

        if device_record is None:
            self.__logger.error(
                "Message is for unknown device: %d",
                entity.device_address,
                extra={
                    "device": {
                        "address": entity.device_address,
                    },
                },
            )

            return

        try:
            self.__devices_registry.set_state(device=device_record, state=ConnectionState.UNKNOWN)

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


@inject(alias=IConsumer)
class RegisterItemConsumer(IConsumer):  # pylint: disable=too-few-public-methods
    """
    BUS messages consumer for registers messages

    @package        FastyBird:FbBusConnector!
    @module         consumers/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry
    __registers_registry: RegistersRegistry

    __logger: Union[Logger, logging.Logger]

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        devices_registry: DevicesRegistry,
        registers_registry: RegistersRegistry,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__devices_registry = devices_registry
        self.__registers_registry = registers_registry

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def consume(self, entity: BaseEntity) -> None:  # pylint: disable=too-many-branches
        """Consume received message"""
        if not isinstance(entity, (SingleRegisterEntity, MultipleRegistersEntity)):
            return

        device_record = self.__devices_registry.get_by_address(address=entity.device_address)

        if device_record is None:
            self.__logger.error(
                "Message is for unknown device %d",
                entity.device_address,
                extra={
                    "device": {
                        "address": entity.device_address,
                    },
                },
            )

            return

        if isinstance(entity, SingleRegisterEntity):
            register_address, register_value = entity.register_value

            register_record = self.__registers_registry.get_by_address(
                device_id=device_record.id,
                register_type=entity.register_type,
                register_address=register_address,
            )

            if register_record is None:
                self.__logger.error(
                    "Message is for unknown register %s:%d",
                    entity.register_type,
                    register_address,
                    extra={
                        "device": {
                            "id": device_record.id.__str__(),
                        },
                    },
                )

                return

            self.__write_value_to_register(register_record=register_record, value=register_value)

        elif isinstance(entity, MultipleRegistersEntity):
            for register_address, register_value in entity.registers_values:
                register_record = self.__registers_registry.get_by_address(
                    device_id=device_record.id,
                    register_type=entity.registers_type,
                    register_address=register_address,
                )

                if register_record is None:
                    self.__logger.error(
                        "Message is for unknown register %s:%d",
                        entity.registers_type,
                        register_address,
                        extra={
                            "device": {
                                "id": device_record.id.__str__(),
                            },
                        },
                    )

                    continue

                self.__write_value_to_register(register_record=register_record, value=register_value)

    # -----------------------------------------------------------------------------

    def __write_value_to_register(
        self,
        register_record: RegisterRecord,
        value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None],
    ) -> None:
        self.__registers_registry.set_actual_value(
            register=register_record,
            value=value,
        )


@inject(alias=IConsumer)
class DiscoveryConsumer(IConsumer):  # pylint: disable=too-few-public-methods
    """
    BUS messages consumer for devices discovery messages

    @package        FastyBird:FbBusConnector!
    @module         consumers/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __discovered_devices_registry: DiscoveredDevicesRegistry
    __discovered_registers_registry: DiscoveredRegistersRegistry

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        discovered_devices_registry: DiscoveredDevicesRegistry,
        discovered_registers_registry: DiscoveredRegistersRegistry,
    ) -> None:
        self.__discovered_devices_registry = discovered_devices_registry
        self.__discovered_registers_registry = discovered_registers_registry

    # -----------------------------------------------------------------------------

    def consume(self, entity: BaseEntity) -> None:
        """Consume received message"""
        if isinstance(entity, DeviceDiscoveryEntity):
            self.__consume_set_device_discovery(entity=entity)

            return

        if isinstance(entity, RegisterStructureEntity):
            self.__consume_register_structure(entity=entity)

            return

    # -----------------------------------------------------------------------------

    def __consume_set_device_discovery(self, entity: DeviceDiscoveryEntity) -> None:
        self.__discovered_devices_registry.append(
            # Device description
            device_address=entity.device_address,
            device_max_packet_length=entity.device_max_packet_length,
            device_serial_number=entity.device_serial_number,
            device_state=entity.device_state,
            device_hardware_version=entity.device_hardware_version,
            device_hardware_model=entity.device_hardware_model,
            device_hardware_manufacturer=entity.device_hardware_manufacturer,
            device_firmware_version=entity.device_firmware_version,
            device_firmware_manufacturer=entity.device_firmware_manufacturer,
            # Registers sizes info
            input_registers_size=entity.input_registers_size,
            output_registers_size=entity.output_registers_size,
            attributes_registers_size=entity.attributes_registers_size,
        )

    # -----------------------------------------------------------------------------

    def __consume_register_structure(self, entity: RegisterStructureEntity) -> None:
        discovered_device = self.__discovered_devices_registry.get_by_address(address=entity.device_address)

        if discovered_device is None:
            return

        self.__discovered_devices_registry.set_waiting_for_packet(device=discovered_device, packet_type=None)

        if entity.register_type in (RegisterType.INPUT, RegisterType.OUTPUT, RegisterType.ATTRIBUTE):
            if entity.register_type == RegisterType.INPUT:
                # Update register record
                self.__discovered_registers_registry.append_input_register(
                    device_serial_number=discovered_device.serial_number,
                    device_address=entity.device_address,
                    register_address=entity.register_address,
                    # Configure register data type
                    register_data_type=entity.register_data_type,
                )

            elif entity.register_type == RegisterType.OUTPUT:
                # Update register record
                self.__discovered_registers_registry.append_output_register(
                    device_serial_number=discovered_device.serial_number,
                    device_address=entity.device_address,
                    register_address=entity.register_address,
                    # Configure register data type
                    register_data_type=entity.register_data_type,
                )

            elif entity.register_type == RegisterType.ATTRIBUTE:
                # Update register record
                self.__discovered_registers_registry.append_attribute_register(
                    device_serial_number=discovered_device.serial_number,
                    device_address=entity.device_address,
                    register_address=entity.register_address,
                    # Configure register details
                    register_data_type=entity.register_data_type,
                    register_name=entity.register_name,
                    register_settable=entity.register_settable,
                    register_queryable=entity.register_queryable,
                )

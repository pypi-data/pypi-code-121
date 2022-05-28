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
FastyBird BUS connector module
"""

# Python base dependencies
import asyncio
import logging
import re
import uuid
from datetime import datetime
from typing import Dict, Optional, Union

# Library dependencies
from fastybird_devices_module.connectors.connector import IConnector
from fastybird_devices_module.entities.channel import (
    ChannelControlEntity,
    ChannelDynamicPropertyEntity,
    ChannelEntity,
    ChannelPropertyEntity,
)
from fastybird_devices_module.entities.connector import ConnectorControlEntity
from fastybird_devices_module.entities.device import (
    DeviceAttributeEntity,
    DeviceControlEntity,
    DeviceDynamicPropertyEntity,
    DevicePropertyEntity,
    DeviceStaticPropertyEntity,
)
from fastybird_devices_module.exceptions import RestartConnectorException
from fastybird_devices_module.utils import normalize_value
from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.types import (
    ButtonPayload,
    ControlAction,
    DataType,
    SwitchPayload,
)
from kink import inject

from fastybird_fb_bus_connector.clients.client import Client
from fastybird_fb_bus_connector.consumers.consumer import Consumer
from fastybird_fb_bus_connector.entities import FbBusConnectorEntity, FbBusDeviceEntity
from fastybird_fb_bus_connector.events.listeners import EventsListener
from fastybird_fb_bus_connector.exceptions import InvalidStateException
from fastybird_fb_bus_connector.logger import Logger
from fastybird_fb_bus_connector.registry.model import (
    DevicesAttributesRegistry,
    DevicesRegistry,
    RegistersRegistry,
)

# Library libs
from fastybird_fb_bus_connector.registry.records import (
    InputRegisterRecord,
    OutputRegisterRecord,
)
from fastybird_fb_bus_connector.transporters.transporter import ITransporter
from fastybird_fb_bus_connector.types import ConnectorAction, RegisterName, RegisterType


@inject(alias=IConnector)
class FbBusConnector(IConnector):  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """
    FastyBird BUS connector

    @package        FastyBird:FbBusConnector!
    @module         connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __stopped: bool = False

    __connector_id: uuid.UUID

    __packets_to_be_sent: int = 0

    __consumer: Consumer
    __client: Client

    __devices_registry: DevicesRegistry
    __registers_registry: RegistersRegistry
    __devices_attributes_registry: DevicesAttributesRegistry

    __transporter: ITransporter

    __events_listener: EventsListener

    __logger: Union[Logger, logging.Logger]

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        connector_id: uuid.UUID,
        consumer: Consumer,
        client: Client,
        devices_registry: DevicesRegistry,
        registers_registry: RegistersRegistry,
        devices_attributes_registry: DevicesAttributesRegistry,
        transporter: ITransporter,
        events_listener: EventsListener,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__connector_id = connector_id

        self.__client = client
        self.__consumer = consumer

        self.__devices_registry = devices_registry
        self.__registers_registry = registers_registry
        self.__devices_attributes_registry = devices_attributes_registry

        self.__transporter = transporter

        self.__events_listener = events_listener

        self.__logger = logger

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Connector identifier"""
        return self.__connector_id

    # -----------------------------------------------------------------------------

    def initialize(self, connector: FbBusConnectorEntity) -> None:
        """Set connector to initial state"""
        self.__devices_registry.reset()

        for device in connector.devices:
            self.initialize_device(device=device)

    # -----------------------------------------------------------------------------

    def initialize_device(self, device: FbBusDeviceEntity) -> None:
        """Initialize device in connector registry"""
        device_record = self.__devices_registry.append(
            device_id=device.id,
            device_enabled=False,
            device_serial_number=device.identifier,
        )

        for device_property in device.properties:
            self.initialize_device_property(device=device, device_property=device_property)

        for device_attribute in device.attributes:
            self.initialize_device_attribute(device=device, device_attribute=device_attribute)

        for channel in device.channels:
            self.initialize_device_channel(device=device, channel=channel)

        self.__devices_registry.enable(device=device_record)

    # -----------------------------------------------------------------------------

    def remove_device(self, device_id: uuid.UUID) -> None:
        """Remove device from connector registry"""
        self.__devices_registry.remove(device_id=device_id)

    # -----------------------------------------------------------------------------

    def reset_devices(self) -> None:
        """Reset devices registry to initial state"""
        self.__devices_registry.reset()

    # -----------------------------------------------------------------------------

    def initialize_device_property(self, device: FbBusDeviceEntity, device_property: DevicePropertyEntity) -> None:
        """Initialize device property aka attribute register in connector registry"""
        match = re.compile("(?P<name>[a-zA-Z-]+)_(?P<address>[0-9]+)")

        parsed_property_identifier = match.fullmatch(device_property.identifier)

        if parsed_property_identifier is not None:
            if isinstance(device_property, DeviceDynamicPropertyEntity):
                self.__registers_registry.append_attribute_register(
                    device_id=device.id,
                    register_id=device_property.id,
                    register_address=int(parsed_property_identifier.group("address")),
                    register_data_type=device_property.data_type,
                    register_invalid=device_property.invalid,
                    register_name=str(parsed_property_identifier.group("name")),
                    register_settable=device_property.settable,
                    register_queryable=device_property.queryable,
                )

            elif isinstance(device_property, DeviceStaticPropertyEntity):
                self.__registers_registry.append_attribute_register(
                    device_id=device.id,
                    register_id=device_property.id,
                    register_address=int(parsed_property_identifier.group("address")),
                    register_data_type=device_property.data_type,
                    register_invalid=device_property.invalid,
                    register_name=str(parsed_property_identifier.group("name")),
                    register_settable=device_property.settable,
                    register_queryable=device_property.queryable,
                    register_value=device_property.value,
                )

    # -----------------------------------------------------------------------------

    def notify_device_property(self, device: FbBusDeviceEntity, device_property: DevicePropertyEntity) -> None:
        """Notify device property was reported to connector"""

    # -----------------------------------------------------------------------------

    def remove_device_property(self, device: FbBusDeviceEntity, property_id: uuid.UUID) -> None:
        """Remove device property from connector registry"""
        self.__registers_registry.remove(register_id=property_id)

    # -----------------------------------------------------------------------------

    def reset_devices_properties(self, device: FbBusDeviceEntity) -> None:
        """Reset devices properties registry to initial state"""
        self.__registers_registry.reset(device_id=device.id, registers_type=RegisterType.ATTRIBUTE)

    # -----------------------------------------------------------------------------

    def initialize_device_attribute(self, device: FbBusDeviceEntity, device_attribute: DeviceAttributeEntity) -> None:
        """Initialize device attribute"""
        if isinstance(device_attribute, DeviceAttributeEntity):
            self.__devices_attributes_registry.append(
                device_id=device_attribute.device.id,
                attribute_id=device_attribute.id,
                attribute_identifier=device_attribute.identifier,
                attribute_name=device_attribute.name,
                attribute_value=device_attribute.content
                if isinstance(device_attribute.content, str) or device_attribute.content is None
                else str(device_attribute.content),
            )

    # -----------------------------------------------------------------------------

    def notify_device_attribute(self, device: FbBusDeviceEntity, device_attribute: DeviceAttributeEntity) -> None:
        """Notify device attribute was reported to connector"""

    # -----------------------------------------------------------------------------

    def remove_device_attribute(self, device: FbBusDeviceEntity, attribute_id: uuid.UUID) -> None:
        """Remove device attribute from connector registry"""
        self.__devices_attributes_registry.remove(attribute_id=attribute_id, propagate=False)

    # -----------------------------------------------------------------------------

    def reset_devices_attributes(self, device: FbBusDeviceEntity) -> None:
        """Reset devices attributes registry to initial state"""
        self.__devices_attributes_registry.reset(device_id=device.id)

    # -----------------------------------------------------------------------------

    def initialize_device_channel(self, device: FbBusDeviceEntity, channel: ChannelEntity) -> None:
        """Initialize device channel aka registers group in connector registry"""
        for channel_property in channel.properties:
            self.initialize_device_channel_property(channel=channel, channel_property=channel_property)

    # -----------------------------------------------------------------------------

    def remove_device_channel(self, device: FbBusDeviceEntity, channel_id: uuid.UUID) -> None:
        """Remove device channel from connector registry"""
        io_registers = self.__registers_registry.get_all_for_device(
            device_id=device.id,
            register_type=[RegisterType.OUTPUT, RegisterType.INPUT],
        )

        for register in io_registers:
            if (
                isinstance(register, (OutputRegisterRecord, InputRegisterRecord))
                and register.channel_id is not None
                and register.channel_id.__eq__(channel_id)
            ):
                self.__registers_registry.remove(register_id=register.id)

    # -----------------------------------------------------------------------------

    def reset_devices_channels(self, device: FbBusDeviceEntity) -> None:
        """Reset devices channels registry to initial state"""
        self.__registers_registry.reset(device_id=device.id, registers_type=RegisterType.OUTPUT)
        self.__registers_registry.reset(device_id=device.id, registers_type=RegisterType.INPUT)

    # -----------------------------------------------------------------------------

    def initialize_device_channel_property(
        self,
        channel: ChannelEntity,
        channel_property: ChannelPropertyEntity,
    ) -> None:
        """Initialize device channel property aka input or output register in connector registry"""
        match_channel = re.compile("(?P<type>[a-zA-Z-]+)_(?P<counter>[0-9]+)")

        parsed_channel_identifier = match_channel.fullmatch(channel.identifier)

        channel_type: Optional[RegisterName] = None

        if parsed_channel_identifier is not None and RegisterName.has_value(
            str(parsed_channel_identifier.group("type"))
        ):
            channel_type = RegisterName(str(parsed_channel_identifier.group("type")))

        elif RegisterName.has_value(channel.identifier):
            channel_type = RegisterName(channel.identifier)

        if channel_type is None:
            self.__logger.warning(
                "Channel identifier is not as expected. Register couldn't be mapped",
                extra={
                    "device": {
                        "id": channel.device.id.__str__(),
                    },
                    "channel": {
                        "id": channel.device.id.__str__(),
                    },
                },
            )

            return

        match_property = re.compile("(?P<name>[a-zA-Z-]+)_(?P<address>[0-9]+)")

        parsed_property_identifier = match_property.fullmatch(channel_property.identifier)

        if parsed_property_identifier is not None:
            if channel_type == RegisterName.OUTPUT:
                self.__registers_registry.append_output_register(
                    device_id=channel.device.id,
                    register_id=channel_property.id,
                    register_address=int(parsed_property_identifier.group("address")),
                    register_data_type=channel_property.data_type,
                    register_invalid=channel_property.invalid,
                    channel_id=channel.id,
                )

            elif channel_type == RegisterName.INPUT:
                self.__registers_registry.append_input_register(
                    device_id=channel.device.id,
                    register_id=channel_property.id,
                    register_address=int(parsed_property_identifier.group("address")),
                    register_data_type=channel_property.data_type,
                    register_invalid=channel_property.invalid,
                    channel_id=channel.id,
                )

            else:
                self.__logger.warning(
                    "Channel identifier is not as expected. Register couldn't be mapped",
                    extra={
                        "device": {
                            "id": channel.device.id.__str__(),
                        },
                        "channel": {
                            "id": channel.device.id.__str__(),
                        },
                    },
                )

    # -----------------------------------------------------------------------------

    def notify_device_channel_property(
        self,
        channel: ChannelEntity,
        channel_property: ChannelPropertyEntity,
    ) -> None:
        """Notify device channel property was reported to connector"""

    # -----------------------------------------------------------------------------

    def remove_device_channel_property(self, channel: ChannelEntity, property_id: uuid.UUID) -> None:
        """Remove device channel property from connector registry"""
        self.__registers_registry.remove(register_id=property_id)

    # -----------------------------------------------------------------------------

    def reset_devices_channels_properties(self, channel: ChannelEntity) -> None:
        """Reset devices channels properties registry to initial state"""
        if channel.identifier == RegisterName.OUTPUT.value:
            self.__registers_registry.reset(device_id=channel.device.id, registers_type=RegisterType.OUTPUT)

        elif channel.identifier == RegisterName.INPUT.value:
            self.__registers_registry.reset(device_id=channel.device.id, registers_type=RegisterType.INPUT)

    # -----------------------------------------------------------------------------

    async def start(self) -> None:
        """Start connector services"""
        # When connector is starting...
        self.__events_listener.open()

        for device in self.__devices_registry:
            try:
                # ...set device state to unknown
                self.__devices_registry.set_state(device=device, state=ConnectionState.UNKNOWN)

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

            registers = self.__registers_registry.get_all_for_device(
                device_id=device.id,
                register_type=[RegisterType.OUTPUT, RegisterType.INPUT, RegisterType.ATTRIBUTE],
            )

            for register in registers:
                self.__registers_registry.set_valid_state(register=register, state=False)

        self.__logger.info("Connector has been started")

        self.__stopped = False

        # Register connector coroutine
        asyncio.ensure_future(self.__worker())

    # -----------------------------------------------------------------------------

    def stop(self) -> None:
        """Close all opened connections & stop connector"""
        # When connector is closing...
        for device in self.__devices_registry:
            try:
                # ...set device state to disconnected
                self.__devices_registry.set_state(device=device, state=ConnectionState.DISCONNECTED)

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

            registers = self.__registers_registry.get_all_for_device(
                device_id=device.id,
                register_type=[RegisterType.OUTPUT, RegisterType.INPUT, RegisterType.ATTRIBUTE],
            )

            for register in registers:
                self.__registers_registry.set_valid_state(register=register, state=False)

        self.__events_listener.close()

        self.__logger.info("Connector has been stopped")

        self.__stopped = True

    # -----------------------------------------------------------------------------

    def has_unfinished_tasks(self) -> bool:
        """Check if connector has some unfinished task"""
        return not self.__consumer.is_empty()

    # -----------------------------------------------------------------------------

    async def write_property(
        self,
        property_item: Union[DevicePropertyEntity, ChannelPropertyEntity],
        data: Dict,
    ) -> None:
        """Write device or channel property value to device"""
        if self.__stopped:
            self.__logger.warning("Connector is stopped, value can't be written")

            return

        if isinstance(property_item, (DeviceDynamicPropertyEntity, ChannelDynamicPropertyEntity)):
            register_record = self.__registers_registry.get_by_id(register_id=property_item.id)

            if register_record is None:
                return

            if property_item.data_type is not None:
                value_to_write = normalize_value(
                    data_type=property_item.data_type,
                    value=data.get("expected_value", None),
                    value_format=property_item.format,
                    value_invalid=property_item.invalid,
                )

            else:
                value_to_write = data.get("expected_value", None)

            if (
                isinstance(value_to_write, (str, int, float, bool, datetime, ButtonPayload, SwitchPayload))
                or value_to_write is None
            ):
                if (
                    isinstance(value_to_write, SwitchPayload)
                    and register_record.data_type == DataType.SWITCH
                    and value_to_write == SwitchPayload.TOGGLE
                ):
                    if register_record.actual_value == SwitchPayload.ON:
                        value_to_write = SwitchPayload.OFF

                    else:
                        value_to_write = SwitchPayload.ON

                self.__registers_registry.set_expected_value(register=register_record, value=value_to_write)

                return

    # -----------------------------------------------------------------------------

    async def write_control(
        self,
        control_item: Union[ConnectorControlEntity, DeviceControlEntity, ChannelControlEntity],
        data: Optional[Dict],
        action: ControlAction,
    ) -> None:
        """Write connector control action"""
        if isinstance(control_item, ConnectorControlEntity):
            if not ConnectorAction.has_value(control_item.name):
                return

            control_action = ConnectorAction(control_item.name)

            if control_action == ConnectorAction.DISCOVER:
                self.__client.discover()

            if control_action == ConnectorAction.RESTART:
                raise RestartConnectorException("Restarting connector")

    # -----------------------------------------------------------------------------

    async def __worker(self) -> None:
        """Run connector service"""
        while True:
            if self.__stopped and self.has_unfinished_tasks():
                return

            self.__consumer.handle()

            # Continue processing devices
            self.__client.handle()

            self.__transporter.handle()

            # Be gentle to server
            await asyncio.sleep(0.01)

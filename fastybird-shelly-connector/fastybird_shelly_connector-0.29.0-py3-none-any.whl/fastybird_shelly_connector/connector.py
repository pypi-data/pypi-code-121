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
Shelly connector module
"""

# Python base dependencies
import asyncio
import logging
import re
import uuid
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
)
from fastybird_devices_module.utils import normalize_value
from fastybird_metadata.devices_module import ConnectionState, DeviceAttributeName
from fastybird_metadata.types import ButtonPayload, ControlAction, SwitchPayload
from kink import inject

# Library libs
from fastybird_shelly_connector.clients.client import Client
from fastybird_shelly_connector.consumers.consumer import Consumer
from fastybird_shelly_connector.entities import (
    ShellyConnectorEntity,
    ShellyDeviceEntity,
)
from fastybird_shelly_connector.events.listeners import EventsListener
from fastybird_shelly_connector.logger import Logger
from fastybird_shelly_connector.registry.model import (
    BlocksRegistry,
    DevicesRegistry,
    PropertiesRegistry,
    SensorsRegistry,
)
from fastybird_shelly_connector.types import (
    ConnectorAction,
    DeviceDescriptionSource,
    DeviceProperty,
    SensorType,
    SensorUnit,
)


@inject(alias=IConnector)
class ShellyConnector(IConnector):  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """
    Shelly connector service

    @package        FastyBird:ShellyConnector!
    @module         connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __stopped: bool = False

    __connector_id: uuid.UUID

    __consumer: Consumer

    __devices_registry: DevicesRegistry
    __properties_registry: PropertiesRegistry
    __blocks_registry: BlocksRegistry
    __sensors_registry: SensorsRegistry

    __client: Client

    __events_listener: EventsListener

    __logger: Union[Logger, logging.Logger]

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        connector_id: uuid.UUID,
        consumer: Consumer,
        devices_registry: DevicesRegistry,
        properties_registry: PropertiesRegistry,
        blocks_registry: BlocksRegistry,
        sensors_registry: SensorsRegistry,
        client: Client,
        events_listener: EventsListener,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__connector_id = connector_id

        self.__consumer = consumer

        self.__devices_registry = devices_registry
        self.__properties_registry = properties_registry
        self.__blocks_registry = blocks_registry
        self.__sensors_registry = sensors_registry

        self.__client = client

        self.__events_listener = events_listener

        self.__logger = logger

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Connector identifier"""
        return self.__connector_id

    # -----------------------------------------------------------------------------

    def initialize(self, connector: ShellyConnectorEntity) -> None:
        """Set connector to initial state"""
        self.__devices_registry.reset()

        for device in connector.devices:
            self.initialize_device(device=device)

    # -----------------------------------------------------------------------------

    def initialize_device(self, device: ShellyDeviceEntity) -> None:
        """Initialize device in connector registry"""
        self.__devices_registry.append(
            description_source=DeviceDescriptionSource.MANUAL,
            device_id=device.id,
            device_identifier=device.identifier,
            device_name=device.name,
        )

        for device_property in device.properties:
            self.initialize_device_property(device=device, device_property=device_property)

        for device_attribute in device.attributes:
            self.initialize_device_attribute(device=device, device_attribute=device_attribute)

        for channel in device.channels:
            self.initialize_device_channel(device=device, channel=channel)

    # -----------------------------------------------------------------------------

    def remove_device(self, device_id: uuid.UUID) -> None:
        """Remove device from connector registry"""
        self.__devices_registry.remove(device_id=device_id)

    # -----------------------------------------------------------------------------

    def reset_devices(self) -> None:
        """Reset devices registry to initial state"""
        self.__devices_registry.reset()

    # -----------------------------------------------------------------------------

    def initialize_device_property(self, device: ShellyDeviceEntity, device_property: DevicePropertyEntity) -> None:
        """Initialize device property in connector registry"""
        if not DeviceProperty.has_value(device_property.identifier):
            return

        if isinstance(device_property, DeviceDynamicPropertyEntity):
            property_record = self.__properties_registry.append(
                device_id=device_property.device.id,
                property_id=device_property.id,
                property_type=DeviceProperty(device_property.identifier),
                property_value=None,
            )

        else:
            property_record = self.__properties_registry.append(
                device_id=device_property.device.id,
                property_id=device_property.id,
                property_type=DeviceProperty(device_property.identifier),
                property_value=device_property.value,
            )

        if device_property.identifier == DeviceProperty.STATE.value:
            self.__properties_registry.set_value(item=property_record, value=ConnectionState.UNKNOWN.value)

    # -----------------------------------------------------------------------------

    def notify_device_property(self, device: ShellyDeviceEntity, device_property: DevicePropertyEntity) -> None:
        """Notify device property was reported to connector"""

    # -----------------------------------------------------------------------------

    def remove_device_property(self, device: ShellyDeviceEntity, property_id: uuid.UUID) -> None:
        """Remove device from connector registry"""
        self.__properties_registry.remove(property_id=property_id)

    # -----------------------------------------------------------------------------

    def reset_devices_properties(self, device: ShellyDeviceEntity) -> None:
        """Reset devices properties registry to initial state"""
        self.__properties_registry.reset(device_id=device.id)

    # -----------------------------------------------------------------------------

    def initialize_device_attribute(self, device: ShellyDeviceEntity, device_attribute: DeviceAttributeEntity) -> None:
        """Initialize device attribute in connector"""
        if (
            device_attribute.identifier == DeviceAttributeName.HARDWARE_MODEL.value
            and device_attribute.content is not None
        ):
            self.__devices_registry.append(
                description_source=DeviceDescriptionSource.MANUAL,
                device_id=device.id,
                device_identifier=device.identifier,
                device_name=device.name,
                device_type=str(device_attribute.content),
            )

    # -----------------------------------------------------------------------------

    def notify_device_attribute(self, device: ShellyDeviceEntity, device_attribute: DeviceAttributeEntity) -> None:
        """Notify device attribute was reported to connector"""

    # -----------------------------------------------------------------------------

    def remove_device_attribute(self, device: ShellyDeviceEntity, attribute_id: uuid.UUID) -> None:
        """Remove device attribute from connector"""

    # -----------------------------------------------------------------------------

    def reset_devices_attributes(self, device: ShellyDeviceEntity) -> None:
        """Reset devices attributes to initial state"""

    # -----------------------------------------------------------------------------

    def initialize_device_channel(self, device: ShellyDeviceEntity, channel: ChannelEntity) -> None:
        """Initialize device channel aka shelly device block in connector registry"""
        match = re.compile("(?P<identifier>[0-9]+)_(?P<description>[a-zA-Z0-9_]+)")

        parsed_channel_identifier = match.fullmatch(channel.identifier)

        if parsed_channel_identifier is None:
            self.__logger.warning(
                "Device's channel couldn't be initialized",
                extra={
                    "device": {
                        "id": channel.device.id.__str__(),
                    },
                    "channel": {
                        "id": channel.id.__str__(),
                    },
                },
            )

            return

        self.__blocks_registry.append(
            device_id=channel.device.id,
            block_id=channel.id,
            block_identifier=int(parsed_channel_identifier.group("identifier")),
            block_description=parsed_channel_identifier.group("description"),
        )

        for channel_property in channel.properties:
            self.initialize_device_channel_property(channel=channel, channel_property=channel_property)

    # -----------------------------------------------------------------------------

    def remove_device_channel(self, device: ShellyDeviceEntity, channel_id: uuid.UUID) -> None:
        """Remove device channel from connector registry"""
        self.__blocks_registry.remove(block_id=channel_id)

    # -----------------------------------------------------------------------------

    def reset_devices_channels(self, device: ShellyDeviceEntity) -> None:
        """Reset devices channels registry to initial state"""
        self.__blocks_registry.reset(device_id=device.id)

    # -----------------------------------------------------------------------------

    def initialize_device_channel_property(
        self,
        channel: ChannelEntity,
        channel_property: ChannelPropertyEntity,
    ) -> None:
        """Initialize device channel property aka shelly device sensor|state in connector registry"""
        match = re.compile("(?P<identifier>[0-9]+)_(?P<type>[a-zA-Z]{1,3})_(?P<description>[a-zA-Z0-9]+)")

        parser_property_identifier = match.fullmatch(channel_property.identifier)

        if (
            parser_property_identifier is None
            or not SensorType.has_value(parser_property_identifier.group("type"))
            or (channel_property.unit is not None and not SensorUnit.has_value(channel_property.unit))
        ):
            self.__logger.warning(
                "Device's channel's property couldn't be initialized",
                extra={
                    "device": {
                        "id": channel_property.channel.device.id.__str__(),
                    },
                    "channel": {
                        "id": channel_property.channel.id.__str__(),
                    },
                    "property": {
                        "id": channel_property.id.__str__(),
                    },
                },
            )

            return

        self.__sensors_registry.append(
            block_id=channel_property.channel.id,
            sensor_id=channel_property.id,
            sensor_identifier=int(parser_property_identifier.group("identifier")),
            sensor_type=SensorType(parser_property_identifier.group("type")),
            sensor_description=parser_property_identifier.group("description"),
            sensor_unit=SensorUnit(channel_property.unit) if channel_property.unit is not None else None,
            sensor_data_type=channel_property.data_type,
            sensor_value_format=channel_property.format,
            sensor_value_invalid=channel_property.invalid,
            sensor_queryable=channel_property.queryable,
            sensor_settable=channel_property.settable,
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
        self.__sensors_registry.remove(sensor_id=property_id)

    # -----------------------------------------------------------------------------

    def reset_devices_channels_properties(self, channel: ChannelEntity) -> None:
        """Reset devices channels properties registry to initial state"""
        self.__sensors_registry.reset(block_id=channel.id)

    # -----------------------------------------------------------------------------

    async def start(self) -> None:
        """Start connector services"""
        self.__events_listener.open()

        for state_property_record in self.__properties_registry.get_all_by_type(property_type=DeviceProperty.STATE):
            self.__properties_registry.set_value(
                item=state_property_record,
                value=ConnectionState.UNKNOWN.value,
            )

        for sensor in self.__sensors_registry:
            self.__sensors_registry.set_valid_state(sensor=sensor, state=False)

        self.__client.start()

        self.__logger.info("Connector has been started")

        self.__stopped = False

        # Register connector coroutine
        asyncio.ensure_future(self.__worker())

    # -----------------------------------------------------------------------------

    def stop(self) -> None:
        """Close all opened connections & stop connector"""
        self.__client.stop()

        for state_property_record in self.__properties_registry.get_all_by_type(property_type=DeviceProperty.STATE):
            self.__properties_registry.set_value(
                item=state_property_record,
                value=ConnectionState.DISCONNECTED.value,
            )

        for sensor in self.__sensors_registry:
            self.__sensors_registry.set_valid_state(sensor=sensor, state=False)

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
        if isinstance(property_item, ChannelDynamicPropertyEntity):
            sensor_record = self.__sensors_registry.get_by_id(sensor_id=property_item.id)

            if sensor_record is None:
                return

            value_to_write = normalize_value(
                data_type=property_item.data_type,
                value=data.get("expected_value", None),
                value_format=property_item.format,
                value_invalid=property_item.invalid,
            )

            if (
                isinstance(value_to_write, (str, int, float, bool, ButtonPayload, SwitchPayload))
                or value_to_write is None
            ):
                self.__sensors_registry.set_expected_value(sensor=sensor_record, value=value_to_write)

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
                pass

    # -----------------------------------------------------------------------------

    async def __worker(self) -> None:
        """Run connector service"""
        while True:
            if self.__stopped and self.has_unfinished_tasks():
                return

            self.__consumer.handle()

            # Continue processing communication
            self.__client.handle()

            # Be gentle to server
            await asyncio.sleep(0.01)

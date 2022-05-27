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
Tuya connector module
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
from fastybird_devices_module.exceptions import RestartConnectorException
from fastybird_devices_module.utils import normalize_value
from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.types import ControlAction
from kink import inject

from fastybird_tuya_connector.clients.cloud import TuyaCloudClient

# Library libs
from fastybird_tuya_connector.clients.local import LocalDeviceClient
from fastybird_tuya_connector.consumers.consumer import Consumer
from fastybird_tuya_connector.discovery import DevicesDiscovery
from fastybird_tuya_connector.entities import TuyaConnectorEntity, TuyaDeviceEntity
from fastybird_tuya_connector.events.listeners import EventsListener
from fastybird_tuya_connector.logger import Logger
from fastybird_tuya_connector.registry.model import (
    AttributesRegistry,
    DataPointsRegistry,
    DevicesRegistry,
    PropertiesRegistry,
)
from fastybird_tuya_connector.types import (
    ConnectorAction,
    ConnectorMode,
    DataPointType,
    DeviceAttribute,
    DeviceProperty,
)


@inject(alias=IConnector)
class TuyaConnector(IConnector):  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """
    Tuya connector

    @package        FastyBird:TuyaConnector!
    @module         connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __stopped: bool = False
    __discovery: bool = False

    __mode: ConnectorMode

    __connector_id: uuid.UUID

    __devices_registry: DevicesRegistry
    __properties_registry: PropertiesRegistry
    __attributes_registry: AttributesRegistry
    __data_points_registry: DataPointsRegistry

    __devices_discovery: DevicesDiscovery

    __local_device_client: LocalDeviceClient
    __cloud_device_client: TuyaCloudClient

    __consumer: Consumer

    __events_listener: EventsListener

    __logger: Union[Logger, logging.Logger]

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Connector identifier"""
        return self.__connector_id

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        mode: ConnectorMode,
        connector_id: uuid.UUID,
        devices_registry: DevicesRegistry,
        properties_registry: PropertiesRegistry,
        attributes_registry: AttributesRegistry,
        data_points_registry: DataPointsRegistry,
        devices_discovery: DevicesDiscovery,
        local_device_client: LocalDeviceClient,
        cloud_device_client: TuyaCloudClient,
        consumer: Consumer,
        events_listener: EventsListener,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__mode = mode
        self.__connector_id = connector_id
        self.__devices_registry = devices_registry
        self.__properties_registry = properties_registry
        self.__attributes_registry = attributes_registry
        self.__data_points_registry = data_points_registry

        self.__devices_discovery = devices_discovery

        self.__local_device_client = local_device_client
        self.__cloud_device_client = cloud_device_client

        self.__consumer = consumer

        self.__events_listener = events_listener

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def initialize(self, connector: TuyaConnectorEntity) -> None:
        """Set connector to initial state"""
        self.__devices_registry.reset()

        for device in connector.devices:
            self.initialize_device(device=device)

    # -----------------------------------------------------------------------------

    def initialize_device(self, device: TuyaDeviceEntity) -> None:
        """Initialize device in connector registry"""
        self.__devices_registry.append(
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

    def initialize_device_property(self, device: TuyaDeviceEntity, device_property: DevicePropertyEntity) -> None:
        """Initialize device property"""
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
            self.__properties_registry.set_value(device_property=property_record, value=ConnectionState.UNKNOWN.value)

    # -----------------------------------------------------------------------------

    def notify_device_property(self, device: TuyaDeviceEntity, device_property: DevicePropertyEntity) -> None:
        """Notify device property was reported to connector"""

    # -----------------------------------------------------------------------------

    def remove_device_property(self, device: TuyaDeviceEntity, property_id: uuid.UUID) -> None:
        """Remove device property from connector registry"""
        self.__properties_registry.remove(property_id=property_id)

    # -----------------------------------------------------------------------------

    def reset_devices_properties(self, device: TuyaDeviceEntity) -> None:
        """Reset devices properties registry to initial state"""
        self.__properties_registry.reset(device_id=device.id)

    # -----------------------------------------------------------------------------

    def initialize_device_attribute(self, device: TuyaDeviceEntity, device_attribute: DeviceAttributeEntity) -> None:
        """Initialize device attribute"""
        if not DeviceAttribute.has_value(device_attribute.identifier):
            return

        self.__attributes_registry.append(
            device_id=device_attribute.device.id,
            attribute_id=device_attribute.id,
            attribute_type=DeviceAttribute(device_attribute.identifier),
            attribute_value=device_attribute.content if isinstance(device_attribute.content, (int, str)) else None,
        )

    # -----------------------------------------------------------------------------

    def notify_device_attribute(self, device: TuyaDeviceEntity, device_attribute: DeviceAttributeEntity) -> None:
        """Notify device attribute was reported to connector"""

    # -----------------------------------------------------------------------------

    def remove_device_attribute(self, device: TuyaDeviceEntity, attribute_id: uuid.UUID) -> None:
        """Remove device attribute from connector registry"""
        self.__attributes_registry.remove(attribute_id=attribute_id)

    # -----------------------------------------------------------------------------

    def reset_devices_attributes(self, device: TuyaDeviceEntity) -> None:
        """Reset devices attributes registry to initial state"""
        self.__attributes_registry.reset(device_id=device.id)

    # -----------------------------------------------------------------------------

    def initialize_device_channel(self, device: TuyaDeviceEntity, channel: ChannelEntity) -> None:
        """Initialize device channel"""
        for channel_property in channel.properties:
            self.initialize_device_channel_property(channel=channel, channel_property=channel_property)

    # -----------------------------------------------------------------------------

    def remove_device_channel(self, device: TuyaDeviceEntity, channel_id: uuid.UUID) -> None:
        """Remove device channel from connector registry"""
        self.__data_points_registry.reset(device_id=device.id)

    # -----------------------------------------------------------------------------

    def reset_devices_channels(self, device: TuyaDeviceEntity) -> None:
        """Reset devices channels registry to initial state"""
        self.__data_points_registry.reset(device_id=device.id)

    # -----------------------------------------------------------------------------

    def initialize_device_channel_property(
        self,
        channel: ChannelEntity,
        channel_property: ChannelPropertyEntity,
    ) -> None:
        """Initialize device channel property"""
        match = re.compile("dp_(?P<index>[0-9])")

        parsed_property_identifier = match.fullmatch(channel_property.identifier)

        if parsed_property_identifier is not None:
            self.__data_points_registry.append(
                device_id=channel.device.id,
                dp_id=channel_property.id,
                dp_index=int(parsed_property_identifier.group("index")),
                dp_name=channel_property.name,
                dp_type=DataPointType.LOCAL,
                dp_unit=channel_property.unit,
                dp_data_type=channel_property.data_type,
                dp_value_format=channel_property.format,
                dp_queryable=channel_property.queryable,
                dp_settable=channel_property.settable,
            )

        else:
            self.__data_points_registry.append(
                device_id=channel.device.id,
                dp_id=channel_property.id,
                dp_identifier=channel_property.identifier,
                dp_name=channel_property.name,
                dp_type=DataPointType.CLOUD,
                dp_unit=channel_property.unit,
                dp_data_type=channel_property.data_type,
                dp_value_format=channel_property.format,
                dp_queryable=channel_property.queryable,
                dp_settable=channel_property.settable,
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
        self.__data_points_registry.remove(dp_id=property_id)

    # -----------------------------------------------------------------------------

    def reset_devices_channels_properties(self, channel: ChannelEntity) -> None:
        """Reset devices channels properties registry to initial state"""
        self.__data_points_registry.reset(device_id=channel.device.id)

    # -----------------------------------------------------------------------------

    async def start(self) -> None:
        """Start connector services"""
        self.__events_listener.open()

        for state_property_record in self.__properties_registry.get_all_by_type(property_type=DeviceProperty.STATE):
            self.__properties_registry.set_value(
                device_property=state_property_record,
                value=ConnectionState.UNKNOWN.value,
            )

        self.__logger.info("Connector has been started")

        self.__stopped = False

        # Register connector coroutine
        asyncio.ensure_future(self.__worker())

        if self.__mode == ConnectorMode.CLOUD:
            self.__cloud_device_client.start()

        if self.__mode == ConnectorMode.LOCAL:
            await self.__local_device_client.start()

    # -----------------------------------------------------------------------------

    def stop(self) -> None:
        """Close all opened connections & stop connector"""
        for state_property_record in self.__properties_registry.get_all_by_type(property_type=DeviceProperty.STATE):
            self.__properties_registry.set_value(
                device_property=state_property_record,
                value=ConnectionState.DISCONNECTED.value,
            )

        for data_point_record in self.__data_points_registry:
            self.__data_points_registry.set_valid_state(data_point=data_point_record, state=False)

        self.__events_listener.close()

        self.__logger.info("Connector has been stopped")

        self.__stopped = True

    # -----------------------------------------------------------------------------

    def has_unfinished_tasks(self) -> bool:
        """Check if connector has some unfinished task"""
        return not self.__consumer.is_empty()

    # -----------------------------------------------------------------------------

    async def write_property(  # pylint: disable=too-many-branches
        self,
        property_item: Union[DevicePropertyEntity, ChannelPropertyEntity],
        data: Dict,
    ) -> None:
        """Write device or channel property value to device"""
        if isinstance(property_item, ChannelDynamicPropertyEntity):
            data_point_record = self.__data_points_registry.get_by_id(dp_id=property_item.id)

            if data_point_record is None:
                return

            value_to_write = normalize_value(
                data_type=property_item.data_type,
                value=data.get("expected_value", None),
                value_format=property_item.format,
                value_invalid=property_item.invalid,
            )

            if isinstance(value_to_write, (str, int, bool)) or value_to_write is None:
                self.__data_points_registry.set_expected_value(data_point=data_point_record, value=value_to_write)

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
                self.__discovery = True
                self.__devices_discovery.enable()

                if self.__mode == ConnectorMode.LOCAL:
                    await self.__local_device_client.stop()

    # -----------------------------------------------------------------------------

    async def __worker(self) -> None:
        """Run connector service"""
        while True:
            if self.__stopped and self.has_unfinished_tasks():
                return

            self.__consumer.handle()

            # Devices discovery is turned on...
            if self.__discovery:
                # ...and proces devices discovery
                self.__devices_discovery.handle()

                if self.__devices_discovery.enabled and self.__consumer.is_empty():
                    raise RestartConnectorException("Discovery finished, restarting connector")

            # Be gentle to server
            await asyncio.sleep(0.01)

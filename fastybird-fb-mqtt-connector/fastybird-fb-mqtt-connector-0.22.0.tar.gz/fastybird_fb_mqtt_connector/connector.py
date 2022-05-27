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
FastyBird MQTT connector module
"""

# Python base dependencies
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union

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
from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.types import (
    ButtonPayload,
    ControlAction,
    DataType,
    SwitchPayload,
)
from kink import inject

# Library libs
from fastybird_fb_mqtt_connector.clients.client import IClient
from fastybird_fb_mqtt_connector.consumers.consumer import Consumer
from fastybird_fb_mqtt_connector.entities import (
    FbMqttConnectorEntity,
    FbMqttDeviceEntity,
)
from fastybird_fb_mqtt_connector.events.listeners import EventsListener
from fastybird_fb_mqtt_connector.logger import Logger
from fastybird_fb_mqtt_connector.registry.model import (
    ChannelsPropertiesRegistry,
    ChannelsRegistry,
    DevicesAttributesRegistry,
    DevicesPropertiesRegistry,
    DevicesRegistry,
)
from fastybird_fb_mqtt_connector.registry.records import (
    ChannelPropertyRecord,
    DevicePropertyRecord,
)


@inject(alias=IConnector)
class FbMqttConnector(IConnector):  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """
    FastyBird MQTT connector

    @package        FastyBird:FbMqttConnector!
    @module         connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __stopped: bool = False

    __connector_id: uuid.UUID

    __consumer: Consumer
    __client: Optional[IClient] = None

    __devices_registry: DevicesRegistry
    __devices_properties_registry: DevicesPropertiesRegistry
    __devices_attributes_registry: DevicesAttributesRegistry
    __channels_registry: ChannelsRegistry
    __channels_properties_registry: ChannelsPropertiesRegistry

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
        connector_id: uuid.UUID,
        consumer: Consumer,
        client: Optional[IClient],
        devices_registry: DevicesRegistry,
        devices_properties_registry: DevicesPropertiesRegistry,
        devices_attributes_registry: DevicesAttributesRegistry,
        channels_registry: ChannelsRegistry,
        channels_properties_registry: ChannelsPropertiesRegistry,
        events_listener: EventsListener,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__connector_id = connector_id

        self.__client = client
        self.__consumer = consumer

        self.__devices_registry = devices_registry
        self.__devices_properties_registry = devices_properties_registry
        self.__devices_attributes_registry = devices_attributes_registry
        self.__channels_registry = channels_registry
        self.__channels_properties_registry = channels_properties_registry

        self.__events_listener = events_listener

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def initialize(self, connector: FbMqttConnectorEntity) -> None:
        """Set connector to initial state"""
        self.__devices_registry.reset()

        for device in connector.devices:
            self.initialize_device(device=device)

    # -----------------------------------------------------------------------------

    def initialize_device(self, device: FbMqttDeviceEntity) -> None:
        """Initialize device in connector registry"""
        device_controls: List[str] = []

        for control in device.controls:
            device_controls.append(control.name)

        self.__devices_registry.append(
            device_id=device.id,
            device_identifier=device.identifier,
            device_name=device.name,
            controls=device_controls,
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

    def initialize_device_property(self, device: FbMqttDeviceEntity, device_property: DevicePropertyEntity) -> None:
        """Initialize device property"""
        if isinstance(device_property, DeviceDynamicPropertyEntity):
            self.__devices_properties_registry.append(
                device_id=device_property.device.id,
                property_id=device_property.id,
                property_identifier=device_property.identifier,
                property_name=device_property.name,
                property_data_type=device_property.data_type,
                property_value_format=device_property.format,
                property_unit=device_property.unit,
                property_queryable=device_property.queryable,
                property_settable=device_property.settable,
            )

    # -----------------------------------------------------------------------------

    def notify_device_property(self, device: FbMqttDeviceEntity, device_property: DevicePropertyEntity) -> None:
        """Notify device property was reported to connector"""

    # -----------------------------------------------------------------------------

    def remove_device_property(self, device: FbMqttDeviceEntity, property_id: uuid.UUID) -> None:
        """Remove device property from connector registry"""
        self.__devices_properties_registry.remove(property_id=property_id, propagate=False)

    # -----------------------------------------------------------------------------

    def reset_devices_properties(self, device: FbMqttDeviceEntity) -> None:
        """Reset devices properties registry to initial state"""
        self.__devices_properties_registry.reset(device_id=device.id)

    # -----------------------------------------------------------------------------

    def initialize_device_attribute(self, device: FbMqttDeviceEntity, device_attribute: DeviceAttributeEntity) -> None:
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

    def notify_device_attribute(self, device: FbMqttDeviceEntity, device_attribute: DeviceAttributeEntity) -> None:
        """Notify device attribute was reported to connector"""

    # -----------------------------------------------------------------------------

    def remove_device_attribute(self, device: FbMqttDeviceEntity, attribute_id: uuid.UUID) -> None:
        """Remove device attribute from connector registry"""
        self.__devices_attributes_registry.remove(attribute_id=attribute_id, propagate=False)

    # -----------------------------------------------------------------------------

    def reset_devices_attributes(self, device: FbMqttDeviceEntity) -> None:
        """Reset devices attributes registry to initial state"""
        self.__devices_attributes_registry.reset(device_id=device.id)

    # -----------------------------------------------------------------------------

    def initialize_device_channel(self, device: FbMqttDeviceEntity, channel: ChannelEntity) -> None:
        """Initialize device channel"""
        self.__channels_registry.append(
            device_id=channel.device.id,
            channel_id=channel.id,
            channel_identifier=channel.identifier,
            channel_name=channel.name,
        )

        for channel_property in channel.properties:
            self.initialize_device_channel_property(channel=channel, channel_property=channel_property)

    # -----------------------------------------------------------------------------

    def remove_device_channel(self, device: FbMqttDeviceEntity, channel_id: uuid.UUID) -> None:
        """Remove device channel from connector registry"""
        self.__channels_registry.remove(channel_id=channel_id, propagate=False)

    # -----------------------------------------------------------------------------

    def reset_devices_channels(self, device: FbMqttDeviceEntity) -> None:
        """Reset devices channels registry to initial state"""
        self.__channels_registry.reset(device_id=device.id)

    # -----------------------------------------------------------------------------

    def initialize_device_channel_property(
        self,
        channel: ChannelEntity,
        channel_property: ChannelPropertyEntity,
    ) -> None:
        """Initialize device channel property"""
        if isinstance(channel_property, ChannelDynamicPropertyEntity):
            self.__channels_properties_registry.append(
                channel_id=channel_property.channel.id,
                property_id=channel_property.id,
                property_identifier=channel_property.identifier,
                property_name=channel_property.name,
                property_data_type=channel_property.data_type,
                property_value_format=channel_property.format,
                property_unit=channel_property.unit,
                property_queryable=channel_property.queryable,
                property_settable=channel_property.settable,
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
        self.__channels_properties_registry.remove(property_id=property_id, propagate=False)

    # -----------------------------------------------------------------------------

    def reset_devices_channels_properties(self, channel: ChannelEntity) -> None:
        """Reset devices channels properties registry to initial state"""
        self.__channels_properties_registry.reset(channel_id=channel.id)

    # -----------------------------------------------------------------------------

    async def start(self) -> None:
        """Start connector services"""
        # When connector is starting...
        self.__events_listener.open()

        for device in self.__devices_registry:
            # ...set device state to unknown
            self.__devices_registry.set_state(device=device, state=ConnectionState.UNKNOWN)

        if self.__client is not None:
            self.__client.start()

        self.__logger.info("Connector has been started")

        self.__stopped = False

        # Register connector coroutine
        asyncio.ensure_future(self.__worker())

    # -----------------------------------------------------------------------------

    def stop(self) -> None:
        """Close all opened connections & stop connector"""
        if self.__client is not None:
            self.__client.stop()

        # When connector is closing...
        for device in self.__devices_registry:
            # ...set device state to disconnected
            self.__devices_registry.set_state(device=device, state=ConnectionState.DISCONNECTED)

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
        if self.__stopped:
            self.__logger.warning("Connector is stopped, value can't be written")

            return

        if isinstance(property_item, (DeviceDynamicPropertyEntity, ChannelDynamicPropertyEntity)):
            property_record: Union[DevicePropertyRecord, ChannelPropertyRecord, None] = None

            if isinstance(property_item, DeviceDynamicPropertyEntity):
                property_record = self.__devices_properties_registry.get_by_id(property_id=property_item.id)

            elif isinstance(property_item, ChannelDynamicPropertyEntity):
                property_record = self.__channels_properties_registry.get_by_id(property_id=property_item.id)

            if property_record is None:
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
                    and property_record.data_type == DataType.SWITCH
                    and value_to_write == SwitchPayload.TOGGLE
                ):
                    if property_record.actual_value == SwitchPayload.ON:
                        value_to_write = SwitchPayload.OFF

                    else:
                        value_to_write = SwitchPayload.ON

                if isinstance(property_item, DeviceDynamicPropertyEntity) and isinstance(
                    property_record, DevicePropertyRecord
                ):
                    self.__devices_properties_registry.set_expected_value(
                        device_property=property_record,
                        value=value_to_write,
                    )

                if isinstance(property_item, ChannelDynamicPropertyEntity) and isinstance(
                    property_record, ChannelPropertyRecord
                ):
                    self.__channels_properties_registry.set_expected_value(
                        channel_property=property_record,
                        value=value_to_write,
                    )

                return

    # -----------------------------------------------------------------------------

    async def write_control(
        self,
        control_item: Union[ConnectorControlEntity, DeviceControlEntity, ChannelControlEntity],
        data: Optional[Dict],
        action: ControlAction,
    ) -> None:
        """Write connector control action"""

    # -----------------------------------------------------------------------------

    async def __worker(self) -> None:
        """Run connector service"""
        while True:
            if self.__stopped and self.has_unfinished_tasks():
                return

            self.__consumer.handle()

            # Continue processing devices
            if self.__client is not None:
                self.__client.handle()

            # Be gentle to server
            await asyncio.sleep(0.01)

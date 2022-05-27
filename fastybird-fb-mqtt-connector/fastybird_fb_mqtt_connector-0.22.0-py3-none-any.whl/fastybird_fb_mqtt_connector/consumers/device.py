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
FastyBird MQTT connector consumers module devices messages consumers
"""

# Python base dependencies
import logging
import uuid
from typing import List, Union

# Library dependencies
from fastybird_metadata.devices_module import ConnectionState, DeviceAttributeName
from kink import inject

# Library libs
from fastybird_fb_mqtt_connector.consumers.consumer import IConsumer
from fastybird_fb_mqtt_connector.consumers.entities import (
    BaseEntity,
    DeviceAttributeEntity,
)
from fastybird_fb_mqtt_connector.logger import Logger
from fastybird_fb_mqtt_connector.registry.model import (
    ChannelsRegistry,
    DevicesAttributesRegistry,
    DevicesPropertiesRegistry,
    DevicesRegistry,
)
from fastybird_fb_mqtt_connector.registry.records import DeviceRecord
from fastybird_fb_mqtt_connector.types import ExtensionType


@inject(alias=IConsumer)
class DeviceAttributeItemConsumer(IConsumer):  # pylint: disable=too-few-public-methods
    """
    Device attribute message consumer

    @package        FastyBird:FbMqttConnector!
    @module         consumers/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry
    __properties_registry: DevicesPropertiesRegistry
    __attributes_registry: DevicesAttributesRegistry
    __channels_registry: ChannelsRegistry

    __logger: Union[Logger, logging.Logger]

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        devices_registry: DevicesRegistry,
        properties_registry: DevicesPropertiesRegistry,
        attributes_registry: DevicesAttributesRegistry,
        channels_registry: ChannelsRegistry,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__devices_registry = devices_registry
        self.__properties_registry = properties_registry
        self.__attributes_registry = attributes_registry
        self.__channels_registry = channels_registry

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def consume(self, entity: BaseEntity) -> None:
        """Consume received message"""
        if not isinstance(entity, DeviceAttributeEntity):
            return

        device = self.__devices_registry.get_by_identifier(device_identifier=entity.device)

        if device is None:
            self.__logger.error("Message is for unknown device %s", entity.device)

            return

        if entity.attribute == DeviceAttributeEntity.STATE and ConnectionState.has_value(str(entity.value)):
            self.__devices_registry.set_state(device=device, state=ConnectionState(str(entity.value)))

        else:
            to_update = {
                "device_id": device.id,
                "device_identifier": device.identifier,
                "device_name": device.name,
                "controls": device.controls,
            }

            if entity.attribute == DeviceAttributeEntity.NAME:
                to_update["device_name"] = str(entity.value)

            if entity.attribute == DeviceAttributeEntity.CONTROLS and isinstance(entity.value, list):
                to_update["controls"] = entity.value

            if entity.attribute == DeviceAttributeEntity.PROPERTIES and isinstance(entity.value, list):
                self.__process_properties(device=device, values=entity.value)

            if entity.attribute == DeviceAttributeEntity.CHANNELS and isinstance(entity.value, list):
                self.__process_channels(device=device, values=entity.value)

            if entity.attribute == DeviceAttributeEntity.EXTENSIONS and isinstance(entity.value, list):
                self.__process_extensions(device=device, values=entity.value)

            self.__devices_registry.update(**to_update)  # type: ignore[arg-type]

        self.__logger.debug("Consumed device attribute message for: %s", device.identifier)

    # -----------------------------------------------------------------------------

    def __process_properties(self, device: DeviceRecord, values: List) -> None:
        for identifier in values:
            device_property = self.__properties_registry.get_by_identifier(
                device_id=device.id,
                property_identifier=identifier,
            )

            if device_property is None:
                self.__properties_registry.create_or_update(
                    device_id=device.id,
                    property_id=uuid.uuid4(),
                    property_identifier=identifier,
                )

        for device_property in self.__properties_registry.get_all_for_device(device_id=device.id):
            if device_property.identifier not in values:
                self.__properties_registry.remove(property_id=device_property.id)

    # -----------------------------------------------------------------------------

    def __process_channels(self, device: DeviceRecord, values: List) -> None:
        for identifier in values:
            channel = self.__channels_registry.get_by_identifier(
                device_id=device.id,
                channel_identifier=identifier,
            )

            if channel is None:
                self.__channels_registry.create_or_update(
                    device_id=device.id,
                    channel_id=uuid.uuid4(),
                    channel_identifier=identifier,
                )

        for channel in self.__channels_registry.get_all_by_device(device_id=device.id):
            if channel.identifier not in values:
                self.__channels_registry.remove(channel_id=channel.id)

    # -----------------------------------------------------------------------------

    def __process_extensions(self, device: DeviceRecord, values: List) -> None:
        for extension in values:
            if extension == ExtensionType.FASTYBIRD_HARDWARE:
                for attribute_identifier in [
                    DeviceAttributeName.HARDWARE_MANUFACTURER.value,
                    DeviceAttributeName.HARDWARE_MODEL.value,
                    DeviceAttributeName.HARDWARE_VERSION.value,
                    DeviceAttributeName.HARDWARE_MAC_ADDRESS.value,
                ]:
                    device_attribute = self.__attributes_registry.get_by_identifier(
                        device_id=device.id,
                        attribute_identifier=attribute_identifier,
                    )

                    if device_attribute is None:
                        self.__attributes_registry.create_or_update(
                            device_id=device.id,
                            attribute_id=uuid.uuid4(),
                            attribute_identifier=attribute_identifier,
                        )

            if extension == ExtensionType.FASTYBIRD_FIRMWARE:
                for attribute_identifier in [
                    DeviceAttributeName.FIRMWARE_MANUFACTURER.value,
                    DeviceAttributeName.FIRMWARE_NAME.value,
                    DeviceAttributeName.FIRMWARE_VERSION.value,
                ]:
                    device_attribute = self.__attributes_registry.get_by_identifier(
                        device_id=device.id,
                        attribute_identifier=attribute_identifier,
                    )

                    if device_attribute is None:
                        self.__attributes_registry.create_or_update(
                            device_id=device.id,
                            attribute_id=uuid.uuid4(),
                            attribute_identifier=attribute_identifier,
                        )

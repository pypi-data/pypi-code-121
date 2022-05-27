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
FastyBird MQTT connector consumers module devices extensions messages consumers
"""

# Python base dependencies
import logging
from typing import Optional, Union

# Library dependencies
from fastybird_metadata.devices_module import DeviceAttributeName
from kink import inject

# Library libs
from fastybird_fb_mqtt_connector.consumers.consumer import IConsumer
from fastybird_fb_mqtt_connector.consumers.entities import (
    BaseEntity,
    ExtensionAttributeEntity,
)
from fastybird_fb_mqtt_connector.logger import Logger
from fastybird_fb_mqtt_connector.registry.model import (
    DevicesAttributesRegistry,
    DevicesRegistry,
)
from fastybird_fb_mqtt_connector.types import ExtensionType


@inject(alias=IConsumer)
class DeviceExtensionItemConsumer(IConsumer):  # pylint: disable=too-few-public-methods
    """
    Device extension message consumer

    @package        FastyBird:FbMqttConnector!
    @module         consumers/extension

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry
    __attributes_registry: DevicesAttributesRegistry

    __logger: Union[Logger, logging.Logger]

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        devices_registry: DevicesRegistry,
        attributes_registry: DevicesAttributesRegistry,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__devices_registry = devices_registry
        self.__attributes_registry = attributes_registry

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def consume(self, entity: BaseEntity) -> None:
        """Consume received message"""
        if not isinstance(entity, ExtensionAttributeEntity):
            return

        device = self.__devices_registry.get_by_identifier(device_identifier=entity.device)

        if device is None:
            self.__logger.error("Message is for unknown device %s", entity.device)

            return

        attribute_identifier: Optional[str] = None

        if attribute_identifier is None:
            return

        # HARDWARE INFO
        if (
            entity.extension.__eq__(ExtensionType.FASTYBIRD_HARDWARE)
            and entity.parameter == ExtensionAttributeEntity.MANUFACTURER
        ):
            attribute_identifier = DeviceAttributeName.HARDWARE_MANUFACTURER.value

        elif (
            entity.extension.__eq__(ExtensionType.FASTYBIRD_HARDWARE)
            and entity.parameter == ExtensionAttributeEntity.MODEL
        ):
            attribute_identifier = DeviceAttributeName.HARDWARE_MODEL.value

        elif (
            entity.extension.__eq__(ExtensionType.FASTYBIRD_HARDWARE)
            and entity.parameter == ExtensionAttributeEntity.VERSION
        ):
            attribute_identifier = DeviceAttributeName.HARDWARE_VERSION.value

        elif (
            entity.extension.__eq__(ExtensionType.FASTYBIRD_HARDWARE)
            and entity.parameter == ExtensionAttributeEntity.MAC_ADDRESS
        ):
            attribute_identifier = DeviceAttributeName.HARDWARE_MAC_ADDRESS.value

        # FIRMWARE INFO
        elif (
            entity.extension.__eq__(ExtensionType.FASTYBIRD_FIRMWARE)
            and entity.parameter == ExtensionAttributeEntity.MANUFACTURER
        ):
            attribute_identifier = DeviceAttributeName.FIRMWARE_MANUFACTURER.value

        elif (
            entity.extension.__eq__(ExtensionType.FASTYBIRD_FIRMWARE)
            and entity.parameter == ExtensionAttributeEntity.NAME
        ):
            attribute_identifier = DeviceAttributeName.FIRMWARE_NAME.value

        elif (
            entity.extension.__eq__(ExtensionType.FASTYBIRD_FIRMWARE)
            and entity.parameter == ExtensionAttributeEntity.VERSION
        ):
            attribute_identifier = DeviceAttributeName.FIRMWARE_VERSION.value

        device_attribute = self.__attributes_registry.get_by_identifier(
            device_id=device.id,
            attribute_identifier=attribute_identifier,
        )

        if device_attribute is not None:
            self.__attributes_registry.create_or_update(
                device_id=device_attribute.device_id,
                attribute_id=device_attribute.id,
                attribute_identifier=device_attribute.identifier,
                attribute_name=device_attribute.name,
                attribute_value=entity.value,
            )

        self.__logger.debug("Consumed device extension message for: %s", device.identifier)

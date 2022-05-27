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
FastyBird MQTT connector consumers module channels messages consumers
"""

# Python base dependencies
import logging
import uuid
from typing import List, Union

# Library dependencies
from kink import inject

# Library libs
from fastybird_fb_mqtt_connector.consumers.consumer import IConsumer
from fastybird_fb_mqtt_connector.consumers.entities import (
    BaseEntity,
    ChannelAttributeEntity,
)
from fastybird_fb_mqtt_connector.logger import Logger
from fastybird_fb_mqtt_connector.registry.model import (
    ChannelsPropertiesRegistry,
    ChannelsRegistry,
    DevicesRegistry,
)
from fastybird_fb_mqtt_connector.registry.records import ChannelRecord


@inject(alias=IConsumer)
class ChannelAttributeItemConsumer(IConsumer):  # pylint: disable=too-few-public-methods
    """
    Channel attribute message consumer

    @package        FastyBird:FbMqttConnector!
    @module         consumers/channel

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry
    __channels_registry: ChannelsRegistry
    __properties_registry: ChannelsPropertiesRegistry

    __logger: Union[Logger, logging.Logger]

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        devices_registry: DevicesRegistry,
        channels_registry: ChannelsRegistry,
        properties_registry: ChannelsPropertiesRegistry,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__devices_registry = devices_registry
        self.__channels_registry = channels_registry
        self.__properties_registry = properties_registry

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def consume(self, entity: BaseEntity) -> None:
        """Consume received message"""
        if not isinstance(entity, ChannelAttributeEntity):
            return

        device = self.__devices_registry.get_by_identifier(device_identifier=entity.device)

        if device is None:
            self.__logger.error("Message is for unknown device %s", entity.device)

            return

        channel = self.__channels_registry.get_by_identifier(device_id=device.id, channel_identifier=entity.channel)

        if channel is None:
            self.__logger.error("Message is for unknown channel %s", entity.device)

            return

        to_update = {
            "device_id": device.id,
            "channel_id": channel.id,
            "channel_identifier": channel.identifier,
            "channel_name": channel.name,
            "controls": channel.controls,
        }

        if entity.attribute == ChannelAttributeEntity.NAME:
            to_update["channel_name"] = str(entity.value)

        if entity.attribute == ChannelAttributeEntity.CONTROLS and isinstance(entity.value, list):
            to_update["controls"] = entity.value

        if entity.attribute == ChannelAttributeEntity.PROPERTIES and isinstance(entity.value, list):
            self.__process_properties(channel=channel, values=entity.value)

        self.__channels_registry.create_or_update(**to_update)  # type: ignore[arg-type]

        self.__logger.debug("Consumed channel attribute message for: %s", channel.identifier)

    # -----------------------------------------------------------------------------

    def __process_properties(self, channel: ChannelRecord, values: List) -> None:
        for identifier in values:
            channel_property = self.__properties_registry.get_by_identifier(
                channel_id=channel.id,
                property_identifier=identifier,
            )

            if channel_property is None:
                self.__properties_registry.create_or_update(
                    channel_id=channel.id,
                    property_id=uuid.uuid4(),
                    property_identifier=identifier,
                )

        for channel_property in self.__properties_registry.get_all_for_channel(channel_id=channel.id):
            if channel_property.identifier not in values:
                self.__properties_registry.remove(property_id=channel_property.id)

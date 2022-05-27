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
FastyBird MQTT connector consumers module properties messages consumers
"""

# Python base dependencies
import logging
import uuid
from abc import ABC
from typing import Dict, List, Optional, Tuple, Union

# Library dependencies
from fastybird_metadata.types import DataType
from kink import inject

# Library libs
from fastybird_fb_mqtt_connector.consumers.consumer import IConsumer
from fastybird_fb_mqtt_connector.consumers.entities import (
    BaseEntity,
    ChannelPropertyEntity,
    DevicePropertyEntity,
    PropertyAttributeEntity,
)
from fastybird_fb_mqtt_connector.logger import Logger
from fastybird_fb_mqtt_connector.registry.model import (
    ChannelsPropertiesRegistry,
    ChannelsRegistry,
    DevicesPropertiesRegistry,
    DevicesRegistry,
)
from fastybird_fb_mqtt_connector.registry.records import (
    ChannelPropertyRecord,
    DevicePropertyRecord,
)


class PropertyItemConsumer(IConsumer, ABC):  # pylint: disable=too-few-public-methods
    """
    Base property message consumer

    @package        FastyBird:FbMqttConnector!
    @module         consumers/property

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @staticmethod
    def _prepare_update_data(
        record: Union[DevicePropertyRecord, ChannelPropertyRecord],
        entity: Union[DevicePropertyEntity, ChannelPropertyEntity],
    ) -> Dict[
        str,
        Union[
            str,
            bool,
            DataType,
            Union[
                Tuple[Optional[int], Optional[int]],
                Tuple[Optional[float], Optional[float]],
                List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
                None,
            ],
            uuid.UUID,
            None,
        ],
    ]:
        to_update: Dict[
            str,
            Union[
                str,
                bool,
                DataType,
                Union[
                    Tuple[Optional[int], Optional[int]],
                    Tuple[Optional[float], Optional[float]],
                    List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
                    None,
                ],
                uuid.UUID,
                None,
            ],
        ] = {
            "property_id": record.id,
            "property_identifier": record.identifier,
            "property_name": record.name,
            "property_data_type": record.data_type,
            "property_value_format": record.format,
            "property_unit": record.unit,
            "property_queryable": record.queryable,
            "property_settable": record.settable,
        }

        for attribute in entity.attributes:
            if attribute.attribute in PropertyAttributeEntity.NAME:
                to_update["property_name"] = attribute.value

            if attribute.attribute == PropertyAttributeEntity.QUERYABLE:
                to_update["property_queryable"] = attribute.value

            if attribute.attribute == PropertyAttributeEntity.SETTABLE:
                to_update["property_settable"] = attribute.value

            if attribute.attribute == PropertyAttributeEntity.DATA_TYPE:
                to_update["property_data_type"] = attribute.value

            if attribute.attribute == PropertyAttributeEntity.UNIT:
                to_update["property_unit"] = attribute.value

            if attribute.attribute == PropertyAttributeEntity.FORMAT:
                to_update["property_value_format"] = attribute.value

        return to_update


@inject(alias=IConsumer)
class DevicePropertyItemConsumer(PropertyItemConsumer):  # pylint: disable=too-few-public-methods
    """
    Device property message consumer

    @package        FastyBird:FbMqttConnector!
    @module         consumers/property

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry
    __properties_registry: DevicesPropertiesRegistry

    __logger: Union[Logger, logging.Logger]

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        devices_registry: DevicesRegistry,
        properties_registry: DevicesPropertiesRegistry,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__devices_registry = devices_registry
        self.__properties_registry = properties_registry

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def consume(self, entity: BaseEntity) -> None:
        """Consume received message"""
        if not isinstance(entity, DevicePropertyEntity):
            return

        device = self.__devices_registry.get_by_identifier(device_identifier=entity.device)

        if device is None:
            self.__logger.error("Message is for unknown device %s", entity.device)

            return

        device_property = self.__properties_registry.get_by_identifier(
            device_id=device.id,
            property_identifier=entity.name,
        )

        if device_property is None:
            self.__logger.error("Message is for unknown device property %s", entity.name)

            return

        if len(entity.attributes) > 0:
            to_update = {
                **self._prepare_update_data(record=device_property, entity=entity),
                **{
                    "device_id": device_property.device_id,
                },
            }

            self.__properties_registry.create_or_update(**to_update)  # type: ignore[arg-type]

        elif entity.value is not None:
            self.__properties_registry.set_actual_value(device_property=device_property, value=entity.value)


@inject(alias=IConsumer)
class ChannelPropertyItemConsumer(PropertyItemConsumer):  # pylint: disable=too-few-public-methods
    """
    Channel property message consumer

    @package        FastyBird:FbMqttConnector!
    @module         consumers/property

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
        if not isinstance(entity, ChannelPropertyEntity):
            return

        device = self.__devices_registry.get_by_identifier(device_identifier=entity.device)

        if device is None:
            self.__logger.error("Message is for unknown device %s", entity.device)

            return

        channel = self.__channels_registry.get_by_identifier(device_id=device.id, channel_identifier=entity.channel)

        if channel is None:
            self.__logger.error("Message is for unknown channel %s", entity.channel)

            return

        channel_property = self.__properties_registry.get_by_identifier(
            channel_id=channel.id,
            property_identifier=entity.name,
        )

        if channel_property is None:
            self.__logger.error("Message is for unknown channel property %s", entity.name)

            return

        if len(entity.attributes) > 0:
            to_update = {
                **self._prepare_update_data(record=channel_property, entity=entity),
                **{
                    "channel_id": channel_property.channel_id,
                },
            }

            self.__properties_registry.create_or_update(**to_update)  # type: ignore[arg-type]

        elif entity.value is not None:
            self.__properties_registry.set_actual_value(channel_property=channel_property, value=entity.value)

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
FastyBird MQTT connector api module parser for API v1
"""

# Python base dependencies
import re
from typing import List, Tuple

# Library libs
from fastybird_fb_mqtt_connector.api.v1validator import V1Validator
from fastybird_fb_mqtt_connector.consumers.entities import (
    BaseEntity,
    ChannelAttributeEntity,
    ChannelPropertyEntity,
    DeviceAttributeEntity,
    DevicePropertyEntity,
    ExtensionAttributeEntity,
    PropertyAttributeEntity,
)
from fastybird_fb_mqtt_connector.exceptions import ParsePayloadException
from fastybird_fb_mqtt_connector.types import ExtensionType


class V1Parser:
    """
    MQTT topic parser

    @package        FastyBird:FbMqttConnector!
    @module         api/v1parser

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @staticmethod
    def parse_message(topic: str, payload: str, retained: bool = False) -> BaseEntity:
        """Parse received message topic & value"""
        if V1Validator.validate(topic=topic) is False:
            raise ParsePayloadException("Provided topic is not valid")

        if V1Validator.validate_device_attribute(topic=topic):
            device_attribute = V1Parser.parse_device_attribute(
                topic=topic,
                payload=payload,
            )
            device_attribute.retained = retained

            return device_attribute

        if V1Validator.validate_device_hardware_info(topic=topic):
            device_hardware = V1Parser.parse_device_hardware_info(
                topic=topic,
                payload=payload,
            )
            device_hardware.retained = retained

            return device_hardware

        if V1Validator.validate_device_firmware_info(topic=topic):
            device_firmware = V1Parser.parse_device_firmware_info(
                topic=topic,
                payload=payload,
            )
            device_firmware.retained = retained

            return device_firmware

        if V1Validator.validate_device_property(topic=topic):
            device_property = V1Parser.parse_device_property(
                topic=topic,
                payload=payload,
            )
            device_property.retained = retained

            return device_property

        if V1Validator.validate_channel_part(topic=topic):
            result = re.findall(V1Validator.CHANNEL_PARTIAL_REGEXP, topic)
            device, channel = result.pop()

            return V1Parser.parse_channel_message(
                device=device,
                channel=channel,
                topic=topic,
                payload=payload,
                retained=retained,
            )

        raise ParsePayloadException("Provided topic is not valid")

    # -----------------------------------------------------------------------------

    @staticmethod
    def parse_channel_message(  # pylint: disable=too-many-arguments
        device: str,
        channel: str,
        topic: str,
        payload: str,
        retained: bool = False,
    ) -> BaseEntity:
        """Parse received message topic & value for device channel"""
        if V1Validator.validate_channel_attribute(topic=topic):
            channel_attribute = V1Parser.parse_channel_attribute(
                device=device,
                channel=channel,
                topic=topic,
                payload=payload,
            )
            channel_attribute.retained = retained

            return channel_attribute

        if V1Validator.validate_channel_property(topic=topic):
            channel_property = V1Parser.parse_channel_property(
                device=device,
                channel=channel,
                topic=topic,
                payload=payload,
            )
            channel_property.retained = retained

            return channel_property

        raise ParsePayloadException("Provided topic is not valid")

    # -----------------------------------------------------------------------------

    @staticmethod
    def parse_device_attribute(
        topic: str,
        payload: str,
    ) -> DeviceAttributeEntity:
        """Parse device attribute topic & value"""
        result = re.findall(V1Validator.DEVICE_ATTRIBUTE_REGEXP, topic)
        device, attribute = result.pop()

        return DeviceAttributeEntity(
            device=device,
            attribute=attribute,
            value=payload,
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def parse_device_hardware_info(
        topic: str,
        payload: str,
    ) -> ExtensionAttributeEntity:
        """Parse device hardware extension info topic & value"""
        result = re.findall(V1Validator.DEVICE_HW_INFO_REGEXP, topic)
        device, hardware = result.pop()

        return ExtensionAttributeEntity(
            device=device,
            extension=ExtensionType.FASTYBIRD_HARDWARE,
            parameter=hardware,
            value=payload,
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def parse_device_firmware_info(
        topic: str,
        payload: str,
    ) -> ExtensionAttributeEntity:
        """Parse device firmware info topic & value"""
        result = re.findall(V1Validator.DEVICE_FW_INFO_REGEXP, topic)
        device, firmware = result.pop()

        return ExtensionAttributeEntity(
            device=device,
            extension=ExtensionType.FASTYBIRD_FIRMWARE,
            parameter=firmware,
            value=payload,
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def parse_device_property(
        topic: str,
        payload: str,
    ) -> DevicePropertyEntity:
        """Parse device property topic & value"""
        result = re.findall(V1Validator.DEVICE_PROPERTY_REGEXP, topic)
        device, name, _, attribute = result.pop()

        entity = DevicePropertyEntity(
            device=device,
            name=name,
        )

        if attribute:
            entity.add_attribute(PropertyAttributeEntity(attribute=attribute, value=payload))

        else:
            entity.value = payload

        return entity

    # -----------------------------------------------------------------------------

    @staticmethod
    def parse_channel_attribute(  # pylint: disable=too-many-arguments
        device: str,
        channel: str,
        topic: str,
        payload: str,
    ) -> ChannelAttributeEntity:
        """Parse channel control attribute & value"""
        result: List[Tuple[str, str, str]] = re.findall(V1Validator.CHANNEL_ATTRIBUTE_REGEXP, topic)
        _, __, attribute = result.pop()

        return ChannelAttributeEntity(
            device=device,
            channel=channel,
            attribute=attribute,
            value=payload,
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def parse_channel_property(  # pylint: disable=too-many-arguments
        device: str,
        channel: str,
        topic: str,
        payload: str,
    ) -> ChannelPropertyEntity:
        """Parse channel property topic & value"""
        result: List[Tuple[str, str, str, str, str]] = re.findall(V1Validator.CHANNEL_PROPERTY_REGEXP, topic)
        _, __, name, ___, attribute = result.pop()

        entity = ChannelPropertyEntity(
            device=device,
            channel=channel,
            name=name,
        )

        if attribute:
            entity.add_attribute(PropertyAttributeEntity(attribute=attribute, value=payload))

        else:
            entity.value = payload

        return entity

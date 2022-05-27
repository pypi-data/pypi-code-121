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
FastyBird MQTT connector api module validator for API v1
"""

# Python base dependencies
import re


class V1Validator:
    """
    MQTT topic validator

    @package        FastyBird:FbMqttConnector!
    @module         api/v1validator

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    # TOPIC: /fb/*
    CONVENTION_PREFIX_REGEXP = r"^\/fb\/.*$"

    # TOPIC: /fb/v1/*
    API_VERSION_REGEXP = r"^\/fb\/v1\/.*$"

    # TOPIC: /fb/v1/<device>/$channel/<channel>/*
    CHANNEL_PARTIAL_REGEXP = r"^\/fb\/v1\/([a-z0-9-]+)\/\$channel\/([a-z0-9_]+)\/.*$"

    # TOPIC: /fb/v1/<device>/<$state|$name|$properties|$controls|$channels|$extensions>
    DEVICE_ATTRIBUTE_REGEXP = r"^\/fb\/v1\/([a-z0-9-]+)\/\$(state|name|properties|controls|channels|extensions)$"

    # TOPIC: /fb/v1/<device>/$hw/<mac-address|manufacturer|model|version>
    DEVICE_HW_INFO_REGEXP = r"^\/fb\/v1\/([a-z0-9-]+)\/\$hw\/(mac-address|manufacturer|model|version)$"
    # TOPIC: /fb/v1/<device>/$fw/<name|manufacturer|version>
    DEVICE_FW_INFO_REGEXP = r"^\/fb\/v1\/([a-z0-9-]+)\/\$fw\/(name|manufacturer|version)$"

    # TOPIC: /fb/v1/<device>/$property/<property>[/<$name|$settable|$queryable|$data-type|$format|$unit>]
    DEVICE_PROPERTY_REGEXP = (
        r"^\/fb\/v1\/([a-z0-9-]+)\/\$property\/([a-z0-9-]+)(\/\$(name|settable|queryable|data-type|format|unit))?$"
    )
    # TOPIC: /fb/v1/<device>/$property/<property>/set
    DEVICE_PROPERTY_SET_REGEXP = r"^\/fb\/v1\/([a-z0-9-]+)\/\$property\/([a-z0-9-]+)\/set?$"

    # TOPIC: /fb/v1/<device>/$control/<configure|reset|reconnect|factory-reset|ota>
    DEVICE_CONTROL_REGEXP = r"^\/fb\/v1\/([a-z0-9-]+)\/\$control\/([a-z0-9-]+)?$"

    # TOPIC: /fb/v1/*/$channel/<channel>/<$name|$properties|$controls>
    CHANNEL_ATTRIBUTE_REGEXP = r"\/(.*)\/\$channel\/([a-z0-9_]+)\/\$(name|properties|controls)$"
    # TOPIC: /fb/v1/*/$channel/<channel>/$property/<property>
    # [/<$name|$settable|$queryable|$data-type|$format|$unit>]
    CHANNEL_PROPERTY_REGEXP = (
        r"\/(.*)\/\$channel\/([a-z0-9_]+)\/\$property\/([a-z0-9-]+)(\/\$("
        r"name|settable|queryable|data-type|format|unit))?$"
    )
    # TOPIC: /fb/v1/*/$channel/<channel>/$property/<property>/set
    CHANNEL_PROPERTY_SET_REGEXP = r"\/(.*)\/\$channel\/([a-z0-9_]+)\/\$property\/([a-z0-9-]+)\/set?$"

    # -----------------------------------------------------------------------------

    @classmethod
    def validate(cls, topic: str) -> bool:
        """Validate topic against sets of regular expressions"""
        # Check if message is sent from broker
        if len(re.findall(r".*/set$", topic)) > 0:
            return False

        if cls.validate_convention(topic) is False or cls.validate_version(topic) is False:
            return False

        if (
            cls.validate_device_attribute(topic)
            or cls.validate_device_hardware_info(topic)
            or cls.validate_device_firmware_info(topic)
            or cls.validate_device_property(topic)
        ):
            return True

        # Check for channel subscriptions
        if cls.validate_channel_part(topic):
            if cls.validate_channel_attribute(topic) or cls.validate_channel_property(topic):
                return True

        return False

    # -----------------------------------------------------------------------------

    @classmethod
    def validate_convention(cls, topic: str) -> bool:
        """Validate topic against convention regular expression"""
        return len(re.findall(cls.CONVENTION_PREFIX_REGEXP, topic)) == 1

    # -----------------------------------------------------------------------------

    @classmethod
    def validate_version(cls, topic: str) -> bool:
        """Validate topic against version regular expression"""
        return len(re.findall(cls.API_VERSION_REGEXP, topic)) == 1

    # -----------------------------------------------------------------------------

    @classmethod
    def validate_is_command(cls, topic: str) -> bool:
        """Validate topic against version regular expression"""
        return len(re.findall(r".*/set$", topic)) == 1

    # -----------------------------------------------------------------------------

    @classmethod
    def validate_device_attribute(cls, topic: str) -> bool:
        """Validate topic against device attribute regular expression"""
        return len(re.findall(cls.DEVICE_ATTRIBUTE_REGEXP, topic)) == 1

    # -----------------------------------------------------------------------------

    @classmethod
    def validate_device_hardware_info(cls, topic: str) -> bool:
        """Validate topic against device hardware info regular expression"""
        return len(re.findall(cls.DEVICE_HW_INFO_REGEXP, topic)) == 1

    # -----------------------------------------------------------------------------

    @classmethod
    def validate_device_firmware_info(cls, topic: str) -> bool:
        """Validate topic against device firmware info regular expression"""
        return len(re.findall(cls.DEVICE_FW_INFO_REGEXP, topic)) == 1

    # -----------------------------------------------------------------------------

    @classmethod
    def validate_device_property(cls, topic: str) -> bool:
        """Validate topic against device property regular expression"""
        return len(re.findall(cls.DEVICE_PROPERTY_REGEXP, topic)) == 1

    # -----------------------------------------------------------------------------

    @classmethod
    def validate_device_property_set(cls, topic: str) -> bool:
        """Validate topic against device property regular expression"""
        return len(re.findall(cls.DEVICE_PROPERTY_SET_REGEXP, topic)) == 1

    # -----------------------------------------------------------------------------

    @classmethod
    def validate_channel_part(cls, topic: str) -> bool:
        """Validate topic against channel part regular expression"""
        return len(re.findall(cls.CHANNEL_PARTIAL_REGEXP, topic)) == 1

    # -----------------------------------------------------------------------------

    @classmethod
    def validate_channel_attribute(cls, topic: str) -> bool:
        """Validate topic against channel control attribute expression"""
        return cls.validate_channel_part(topic) and len(re.findall(cls.CHANNEL_ATTRIBUTE_REGEXP, topic)) == 1

    # -----------------------------------------------------------------------------

    @classmethod
    def validate_channel_property(cls, topic: str) -> bool:
        """Validate topic against channel property regular expression"""
        return cls.validate_channel_part(topic) and len(re.findall(cls.CHANNEL_PROPERTY_REGEXP, topic)) == 1

    # -----------------------------------------------------------------------------

    @classmethod
    def validate_channel_property_set(cls, topic: str) -> bool:
        """Validate topic against channel property regular expression"""
        return cls.validate_channel_part(topic) and len(re.findall(cls.CHANNEL_PROPERTY_SET_REGEXP, topic)) == 1

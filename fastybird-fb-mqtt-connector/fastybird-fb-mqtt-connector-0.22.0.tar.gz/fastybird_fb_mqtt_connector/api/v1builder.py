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
FastyBird MQTT connector api module builder for API v1
"""

# Python base dependencies
from typing import Dict, Optional


class V1Builder:
    """
    MQTT topic builder

    @package        FastyBird:FbMqttConnector!
    @module         api/v1builder

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    BROADCAST_TOPIC = "/fb/v1/$broadcast/{ACTION}"
    DEVICE_PROPERTY_TOPIC = "/fb/v1/{DEVICE_ID}/$property/{IDENTIFIER}/set"
    DEVICE_CONTROL_TOPIC = "/fb/v1/{DEVICE_ID}/$control/{CONTROL}/set"
    CHANNEL_PROPERTY_TOPIC = "/fb/v1/{DEVICE_ID}/$channel/{CHANNEL_ID}/$property/{IDENTIFIER}/set"
    CHANNEL_CONTROL_TOPIC = "/fb/v1/{DEVICE_ID}/$channel/{CHANNEL_ID}/$control/{CONTROL}/set"

    # -----------------------------------------------------------------------------

    @staticmethod
    def build_device_property(device: str, identifier: str) -> str:
        """Build set device property topic"""
        return V1Builder.build_topic(
            topic=V1Builder.DEVICE_PROPERTY_TOPIC,
            data={
                "DEVICE_ID": device,
                "IDENTIFIER": identifier,
            },
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def build_device_command(device: str, command: str) -> str:
        """Build send device command topic"""
        return V1Builder.build_topic(
            topic=V1Builder.DEVICE_CONTROL_TOPIC,
            data={
                "DEVICE_ID": device,
                "CONTROL": command,
            },
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def build_channel_property(device: str, channel: str, identifier: str) -> str:
        """Build set channel property topic"""
        return V1Builder.build_topic(
            topic=V1Builder.CHANNEL_PROPERTY_TOPIC,
            data={
                "DEVICE_ID": device,
                "CHANNEL_ID": channel,
                "IDENTIFIER": identifier,
            },
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def build_channel_command(device: str, channel: str, command: str) -> str:
        """Build send channel command topic"""
        return V1Builder.build_topic(
            topic=V1Builder.CHANNEL_CONTROL_TOPIC,
            data={
                "DEVICE_ID": device,
                "CHANNEL_ID": channel,
                "CONTROL": command,
            },
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def build_topic(topic: str, data: Dict[str, Optional[str]]) -> str:
        """Build MQTT topic string"""
        build_topic = topic

        for key, value in data.items():
            if value is not None:
                build_topic = build_topic.replace(f"{{{key}}}", value)

        return build_topic

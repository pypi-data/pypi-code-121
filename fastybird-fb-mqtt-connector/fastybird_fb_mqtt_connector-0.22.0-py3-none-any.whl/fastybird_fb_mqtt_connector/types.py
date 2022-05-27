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
FastyBird MQTT connector types module
"""

# Python base dependencies
from enum import unique

# Library dependencies
from fastybird_metadata.devices_module import ConnectorPropertyName
from fastybird_metadata.enum import ExtendedEnum

CONNECTOR_NAME: str = "fb-mqtt"
DEVICE_NAME: str = "fb-mqtt"

DEFAULT_SERVER_ADDRESS: str = "127.0.0.1"
DEFAULT_SERVER_PORT: int = 1883
DEFAULT_SERVER_SECURED_PORT: int = 8883


@unique
class ProtocolVersion(ExtendedEnum):
    """
    Communication protocol version

    @package        FastyBird:FbMqttConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    V1: str = "v1"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class ExtensionType(ExtendedEnum):
    """
    Communication protocol extension

    @package        FastyBird:FbMqttConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    FASTYBIRD_HARDWARE: str = "com.fastybird.hardware"
    FASTYBIRD_FIRMWARE: str = "com.fastybird.firmware"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class ConnectorAttribute(ExtendedEnum):
    """
    Known connector attribute name

    @package        FastyBird:FbBusConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    SERVER: str = ConnectorPropertyName.SERVER.value
    PORT: str = ConnectorPropertyName.PORT.value
    SECURED_PORT: str = ConnectorPropertyName.SECURED_PORT.value
    USERNAME: str = "username"
    PASSWORD: str = "password"
    PROTOCOL: str = "protocol"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member

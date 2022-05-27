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
Tuya connector types module
"""

# Python base dependencies
from enum import unique

# Library dependencies
from fastybird_metadata.devices_module import DeviceAttributeName, DevicePropertyName
from fastybird_metadata.enum import ExtendedEnum

CONNECTOR_NAME: str = "tuya"
DEVICE_NAME: str = "tuya"


@unique
class ConnectorMode(ExtendedEnum):
    """
    Tuya connector communication mode

    @package        FastyBird:TuyaConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    LOCAL: str = "local"
    CLOUD: str = "cloud"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class DeviceProtocolVersion(ExtendedEnum):
    """
    Device communication protocol version

    @package        FastyBird:TuyaConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    V31: str = "3.1"
    V33: str = "3.3"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class ConnectorProperty(ExtendedEnum):
    """
    Known connector property name

    @package        FastyBird:FbBusConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    ACCESS_ID: str = "access_id"
    ACCESS_SECRET: str = "access_secret"
    OPENAPI_ENDPOINT: str = "openapi_endpoint"
    OPENPULSAR_ENDPOINT: str = "openpulsar_endpoint"
    COMMUNICATION_MODE: str = "communication_mode"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class DeviceProperty(ExtendedEnum):
    """
    Devices property name

    @package        FastyBird:TuyaConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    IP_ADDRESS: str = DevicePropertyName.IP_ADDRESS.value
    STATE: str = DevicePropertyName.STATE.value
    LOCAL_KEY: str = "local_key"
    USER_IDENTIFIER: str = "user_identifier"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class DeviceAttribute(ExtendedEnum):
    """
    Devices attribute name

    @package        FastyBird:TuyaConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    MODEL: str = DeviceAttributeName.HARDWARE_MODEL.value
    MAC_ADDRESS: str = DeviceAttributeName.HARDWARE_MAC_ADDRESS.value
    SERIAL_NUMBER: str = "serial_number"
    ENCRYPTED: str = "encrypted"
    PROTOCOL_VERSION: str = "protocol_version"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class DataPointType(ExtendedEnum):
    """
    Device data point type

    @package        FastyBird:TuyaConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    LOCAL: str = "local"
    CLOUD: str = "cloud"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class OpenApiEndpoint(ExtendedEnum):
    """
    Tuya Cloud Open API Endpoint

    @package        FastyBird:TuyaConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    CHINA: str = "https://openapi.tuyacn.com"
    AMERICA: str = "https://openapi.tuyaus.com"
    AMERICA_AZURE: str = "https://openapi-ueaz.tuyaus.com"
    EUROPE: str = "https://openapi.tuyaeu.com"
    EUROPE_MS: str = "https://openapi-weaz.tuyaeu.com"
    INDIA: str = "https://openapi.tuyain.com"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class OpenPulsarEndpoint(ExtendedEnum):
    """
    Tuya Cloud Open Pulsar endpoint

    @package        FastyBird:TuyaConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    CHINA: str = "wss://mqe.tuyacn.com:8285/"
    AMERICA: str = "wss://mqe.tuyaus.com:8285/"
    EUROPE: str = "wss://mqe.tuyaeu.com:8285/"
    INDIA: str = "wss://mqe.tuyain.com:8285/"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class OpenPulsarTopic(ExtendedEnum):
    """
    Tuya Cloud Open Pulsar topic

    @package        FastyBird:TuyaConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    PROD: str = "event"
    TEST: str = "event-test"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class ConnectorAction(ExtendedEnum):
    """
    Connector control action

    @package        FastyBird:TuyaConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    DISCOVER: str = "discover"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member

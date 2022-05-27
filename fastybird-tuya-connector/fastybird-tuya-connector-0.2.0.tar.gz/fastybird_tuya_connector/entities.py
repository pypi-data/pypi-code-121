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
Tuya connector entities module
"""

# Python base dependencies
from typing import Optional, Union

# Library dependencies
from fastybird_devices_module.entities.connector import (
    ConnectorEntity,
    ConnectorStaticPropertyEntity,
)
from fastybird_devices_module.entities.device import DeviceEntity
from fastybird_metadata.types import ConnectorSource, ModuleSource, PluginSource

# Library libs
from fastybird_tuya_connector.types import (
    CONNECTOR_NAME,
    DEVICE_NAME,
    ConnectorMode,
    ConnectorProperty,
    OpenApiEndpoint,
    OpenPulsarEndpoint,
)


class TuyaConnectorEntity(ConnectorEntity):
    """
    Tuya connector entity

    @package        FastyBird:TuyaConnector!
    @module         entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": CONNECTOR_NAME}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> str:
        """Connector type"""
        return CONNECTOR_NAME

    # -----------------------------------------------------------------------------

    @property
    def source(self) -> Union[ModuleSource, ConnectorSource, PluginSource]:
        """Entity source type"""
        return ConnectorSource.TUYA_CONNECTOR

    # -----------------------------------------------------------------------------

    @property
    def communication_mode(self) -> ConnectorMode:
        """Tuya connector communication mode"""
        mode_property = next(
            iter(
                [
                    record
                    for record in self.properties
                    if record.identifier == ConnectorProperty.COMMUNICATION_MODE.value
                ]
            ),
            None,
        )

        if (
            mode_property is None
            or not isinstance(mode_property, ConnectorStaticPropertyEntity)
            or not ConnectorMode.has_value(str(mode_property.value))
        ):
            return ConnectorMode.CLOUD

        return ConnectorMode(mode_property.value)

    # -----------------------------------------------------------------------------

    @property
    def access_id(self) -> Optional[str]:
        """Tuya cloud access identifier"""
        access_id_property = next(
            iter([record for record in self.properties if record.identifier == ConnectorProperty.ACCESS_ID.value]),
            None,
        )

        if (
            access_id_property is None
            or not isinstance(access_id_property, ConnectorStaticPropertyEntity)
            or not isinstance(access_id_property.value, str)
        ):
            return None

        return access_id_property.value

    # -----------------------------------------------------------------------------

    @property
    def access_secret(self) -> Optional[str]:
        """Tuya cloud access secret"""
        access_id_property = next(
            iter([record for record in self.properties if record.identifier == ConnectorProperty.ACCESS_SECRET.value]),
            None,
        )

        if (
            access_id_property is None
            or not isinstance(access_id_property, ConnectorStaticPropertyEntity)
            or not isinstance(access_id_property.value, str)
        ):
            return None

        return access_id_property.value

    # -----------------------------------------------------------------------------

    @property
    def openapi_endpoint(self) -> OpenApiEndpoint:  # pylint: disable=too-many-return-statements
        """Tuya cloud api endpoint"""
        endpoint_property = next(
            iter(
                [record for record in self.properties if record.identifier == ConnectorProperty.OPENAPI_ENDPOINT.value]
            ),
            None,
        )

        if (
            endpoint_property is None
            or not isinstance(endpoint_property, ConnectorStaticPropertyEntity)
            or not OpenApiEndpoint.has_value(str(endpoint_property.value))
        ):
            return OpenApiEndpoint.EUROPE

        if endpoint_property.value == "china":
            return OpenApiEndpoint.CHINA

        if endpoint_property.value == "america":
            return OpenApiEndpoint.AMERICA

        if endpoint_property.value == "america_azure":
            return OpenApiEndpoint.AMERICA_AZURE

        if endpoint_property.value == "europe":
            return OpenApiEndpoint.EUROPE

        if endpoint_property.value == "europe_ms":
            return OpenApiEndpoint.EUROPE_MS

        if endpoint_property.value == "india":
            return OpenApiEndpoint.INDIA

        return OpenApiEndpoint.EUROPE

    # -----------------------------------------------------------------------------

    @property
    def openpulsar_endpoint(self) -> OpenPulsarEndpoint:
        """Tuya cloud api endpoint"""
        endpoint_property = next(
            iter(
                [
                    record
                    for record in self.properties
                    if record.identifier == ConnectorProperty.OPENPULSAR_ENDPOINT.value
                ]
            ),
            None,
        )

        if (
            endpoint_property is None
            or not isinstance(endpoint_property, ConnectorStaticPropertyEntity)
            or not OpenPulsarEndpoint.has_value(str(endpoint_property.value))
        ):
            return OpenPulsarEndpoint.EUROPE

        if endpoint_property.value == "china":
            return OpenPulsarEndpoint.CHINA

        if endpoint_property.value == "america":
            return OpenPulsarEndpoint.AMERICA

        if endpoint_property.value == "europe":
            return OpenPulsarEndpoint.EUROPE

        if endpoint_property.value == "india":
            return OpenPulsarEndpoint.INDIA

        return OpenPulsarEndpoint.EUROPE


class TuyaDeviceEntity(DeviceEntity):  # pylint: disable=too-few-public-methods
    """
    Tuya device entity

    @package        FastyBird:TuyaConnector!
    @module         entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": DEVICE_NAME}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> str:
        """Device type"""
        return DEVICE_NAME

    # -----------------------------------------------------------------------------

    @property
    def source(self) -> Union[ModuleSource, ConnectorSource, PluginSource]:
        """Entity source type"""
        return ConnectorSource.TUYA_CONNECTOR

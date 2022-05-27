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
FastyBird MQTT connector entities module
"""

# Python base dependencies
from typing import Dict, List, Optional, Union

# Library dependencies
from fastybird_devices_module.entities.connector import (
    ConnectorEntity,
    ConnectorStaticPropertyEntity,
)
from fastybird_devices_module.entities.device import DeviceEntity
from fastybird_metadata.types import ConnectorSource, ModuleSource, PluginSource

# Library libs
from fastybird_fb_mqtt_connector.types import (
    CONNECTOR_NAME,
    DEFAULT_SERVER_ADDRESS,
    DEFAULT_SERVER_PORT,
    DEFAULT_SERVER_SECURED_PORT,
    DEVICE_NAME,
    ConnectorAttribute,
    ProtocolVersion,
)


class FbMqttConnectorEntity(ConnectorEntity):
    """
    FastyBird MQTT connector entity

    @package        FastyBird:FbMqttConnector!
    @module         entities/connector

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
        return ConnectorSource.FB_MQTT_CONNECTOR

    # -----------------------------------------------------------------------------

    @property
    def server(self) -> str:
        """Connector server address"""
        server_address_property = next(
            iter([record for record in self.properties if record.identifier == ConnectorAttribute.SERVER.value]),
            None,
        )

        if (
            server_address_property is None
            or not isinstance(server_address_property, ConnectorStaticPropertyEntity)
            or not isinstance(server_address_property.value, str)
        ):
            return DEFAULT_SERVER_ADDRESS

        return server_address_property.value

    # -----------------------------------------------------------------------------

    @property
    def port(self) -> int:
        """Connector server port"""
        port_property = next(
            iter([record for record in self.properties if record.identifier == ConnectorAttribute.PORT.value]),
            None,
        )

        if (
            port_property is None
            or not isinstance(port_property, ConnectorStaticPropertyEntity)
            or not isinstance(port_property.value, int)
        ):
            return DEFAULT_SERVER_PORT

        return port_property.value

    # -----------------------------------------------------------------------------

    @property
    def secured_port(self) -> int:
        """Connector server port"""
        port_property = next(
            iter([record for record in self.properties if record.identifier == ConnectorAttribute.SECURED_PORT.value]),
            None,
        )

        if (
            port_property is None
            or not isinstance(port_property, ConnectorStaticPropertyEntity)
            or not isinstance(port_property.value, int)
        ):
            return DEFAULT_SERVER_SECURED_PORT

        return port_property.value

    # -----------------------------------------------------------------------------

    @property
    def username(self) -> Optional[str]:
        """Connector server username"""
        username_property = next(
            iter([record for record in self.properties if record.identifier == ConnectorAttribute.USERNAME.value]),
            None,
        )

        if (
            username_property is None
            or not isinstance(username_property, ConnectorStaticPropertyEntity)
            or not isinstance(username_property.value, str)
        ):
            return None

        return username_property.value

    # -----------------------------------------------------------------------------

    @property
    def password(self) -> Optional[str]:
        """Connector server password"""
        password_property = next(
            iter([record for record in self.properties if record.identifier == ConnectorAttribute.PASSWORD.value]),
            None,
        )

        if (
            password_property is None
            or not isinstance(password_property, ConnectorStaticPropertyEntity)
            or not isinstance(password_property.value, str)
        ):
            return None

        return password_property.value

    # -----------------------------------------------------------------------------

    @property
    def protocol(self) -> ProtocolVersion:
        """Connector communication protocol version"""
        protocol_property = next(
            iter([record for record in self.properties if record.identifier == ConnectorAttribute.PROTOCOL.value]),
            None,
        )

        if (
            protocol_property is None
            or not isinstance(protocol_property, ConnectorStaticPropertyEntity)
            or not ProtocolVersion.has_value(str(protocol_property.value))
        ):
            return ProtocolVersion.V1

        return ProtocolVersion(protocol_property.value)

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, int, bool, List[str], None]]:
        """Transform entity to dictionary"""
        return {
            **super().to_dict(),
            **{
                "server": self.server,
                "port": self.port,
                "secured_port": self.secured_port,
                "username": self.username,
                "protocol": self.protocol.value,
            },
        }


class FbMqttDeviceEntity(DeviceEntity):  # pylint: disable=too-few-public-methods
    """
    FastyBird MQTT device entity

    @package        FastyBird:FbMqttConnector!
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
        return ConnectorSource.FB_MQTT_CONNECTOR

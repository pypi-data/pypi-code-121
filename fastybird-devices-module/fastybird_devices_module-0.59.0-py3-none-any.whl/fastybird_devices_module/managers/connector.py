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
Devices module connector managers module
"""

# Python base dependencies
import uuid
from typing import Dict, List, Type, Union

# Library libs
from fastybird_devices_module.entities.connector import (
    ConnectorControlEntity,
    ConnectorDynamicPropertyEntity,
    ConnectorEntity,
    ConnectorPropertyEntity,
    ConnectorStaticPropertyEntity,
)
from fastybird_devices_module.managers.base import BaseManager


class ConnectorsManager(BaseManager[ConnectorEntity]):
    """
    Connectors manager

    @package        FastyBird:DevicesModule!
    @module         managers/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __REQUIRED_FIELDS: List[str] = ["identifier"]
    __WRITABLE_FIELDS: List[str] = [
        "name",
        "comment",
        "enabled",
        "owner",
    ]

    # -----------------------------------------------------------------------------

    def create(self, data: Dict, connector_type: Type[ConnectorEntity]) -> ConnectorEntity:
        """Create new connector entity"""
        return super().create_entity(
            data={**data, **{"connector_id": data.get("id", None)}},
            entity_type=connector_type,
            required_fields=self.__REQUIRED_FIELDS,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def update(self, data: Dict, connector: ConnectorEntity) -> ConnectorEntity:
        """Update connector entity"""
        return super().update_entity(
            data=data,
            entity_id=connector.id,
            entity_type=ConnectorEntity,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def delete(self, connector: ConnectorEntity) -> bool:
        """Delete connector entity"""
        return super().delete_entity(entity_id=connector.id, entity_type=ConnectorEntity)


class ConnectorPropertiesManager(BaseManager[ConnectorPropertyEntity]):
    """
    Connector properties manager

    @package        FastyBird:ConnectorsModule!
    @module         managers/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __REQUIRED_FIELDS: List[str] = ["connector", "identifier"]
    __WRITABLE_FIELDS: List[str] = [
        "name",
        "settable",
        "queryable",
        "data_type",
        "unit",
        "format",
        "invalid",
        "number_of_decimals",
        "value",
    ]

    # -----------------------------------------------------------------------------

    def create(
        self,
        data: Dict,
        property_type: Type[Union[ConnectorDynamicPropertyEntity, ConnectorStaticPropertyEntity]],
    ) -> ConnectorPropertyEntity:
        """Create new connector property entity"""
        if "connector_id" in data and "connector" not in data:
            connector_id = data.get("connector_id")

            if isinstance(connector_id, uuid.UUID):
                data["connector"] = self._session.query(ConnectorEntity).get(connector_id.bytes)

        return super().create_entity(
            data={**data, **{"property_id": data.get("id", None)}},
            entity_type=property_type,
            required_fields=self.__REQUIRED_FIELDS,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def update(self, data: Dict, connector_property: ConnectorPropertyEntity) -> ConnectorPropertyEntity:
        """Update connector property entity"""
        return super().update_entity(
            data=data,
            entity_id=connector_property.id,
            entity_type=ConnectorPropertyEntity,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def delete(self, connector_property: ConnectorPropertyEntity) -> bool:
        """Delete connector property entity"""
        return super().delete_entity(entity_id=connector_property.id, entity_type=ConnectorPropertyEntity)


class ConnectorControlsManager(BaseManager[ConnectorControlEntity]):
    """
    Connector controls manager

    @package        FastyBird:DevicesModule!
    @module         managers/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __REQUIRED_FIELDS: List[str] = ["connector", "name"]

    # -----------------------------------------------------------------------------

    def create(self, data: Dict) -> ConnectorControlEntity:
        """Create new connector control entity"""
        if "connector_id" in data and "connector" not in data:
            connector_id = data.get("connector_id")

            if isinstance(connector_id, uuid.UUID):
                data["connector"] = self._session.query(ConnectorEntity).get(connector_id.bytes)

        return super().create_entity(
            data={**data, **{"control_id": data.get("id", None)}},
            entity_type=ConnectorControlEntity,
            required_fields=self.__REQUIRED_FIELDS,
            writable_fields=[],
        )

    # -----------------------------------------------------------------------------

    def delete(self, connector_control: ConnectorControlEntity) -> bool:
        """Delete connector control entity"""
        return super().delete_entity(entity_id=connector_control.id, entity_type=ConnectorControlEntity)

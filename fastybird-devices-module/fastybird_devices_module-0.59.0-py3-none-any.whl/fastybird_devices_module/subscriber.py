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
Devices module subscriber module
"""

# Python base dependencies
import datetime
from typing import Dict, Optional, Type

# Library dependencies
from fastybird_exchange.publisher import Publisher
from fastybird_metadata.routing import RoutingKey
from kink import inject
from sqlalchemy import event
from sqlalchemy.orm import Session as OrmSession

# Library libs
from fastybird_devices_module.entities.base import (
    Base,
    EntityCreatedMixin,
    EntityUpdatedMixin,
)
from fastybird_devices_module.entities.channel import (
    ChannelControlEntity,
    ChannelDynamicPropertyEntity,
    ChannelEntity,
    ChannelMappedPropertyEntity,
    ChannelPropertyEntity,
)
from fastybird_devices_module.entities.connector import (
    ConnectorControlEntity,
    ConnectorDynamicPropertyEntity,
    ConnectorEntity,
    ConnectorPropertyEntity,
)
from fastybird_devices_module.entities.device import (
    DeviceAttributeEntity,
    DeviceControlEntity,
    DeviceDynamicPropertyEntity,
    DeviceEntity,
    DeviceMappedPropertyEntity,
    DevicePropertyEntity,
)
from fastybird_devices_module.managers.state import (
    ChannelPropertiesStatesManager,
    ConnectorPropertiesStatesManager,
    DevicePropertiesStatesManager,
)
from fastybird_devices_module.repositories.state import (
    ChannelPropertiesStatesRepository,
    ConnectorPropertiesStatesRepository,
    DevicePropertiesStatesRepository,
)


class EntityCreatedSubscriber:  # pylint: disable=too-few-public-methods
    """
    New entity creation subscriber

    @package        FastyBird:DevicesModule!
    @module         subscriber

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    def __init__(self) -> None:
        event.listen(
            Base, "before_insert", lambda mapper, connection, target: self.before_insert(target), propagate=True
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def before_insert(target: Base) -> None:
        """Before entity inserted update timestamp"""
        if isinstance(target, EntityCreatedMixin):
            target.created_at = datetime.datetime.now()


class EntityUpdatedSubscriber:  # pylint: disable=too-few-public-methods
    """
    Existing entity update subscriber

    @package        FastyBird:DevicesModule!
    @module         subscriber

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    def __init__(self) -> None:
        event.listen(
            Base, "before_update", lambda mapper, connection, target: self.before_update(target), propagate=True
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def before_update(target: Base) -> None:
        """Before entity updated update timestamp"""
        if isinstance(target, EntityUpdatedMixin):
            target.updated_at = datetime.datetime.now()


@inject(
    bind={
        "publisher": Publisher,
    }
)
class EntitiesSubscriber:  # pylint: disable=too-few-public-methods
    """
    Data exchanges utils

    @package        FastyBird:DevicesModule!
    @module         subscriber

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    CREATED_ENTITIES_ROUTING_KEYS_MAPPING: Dict[Type[Base], RoutingKey] = {
        ConnectorEntity: RoutingKey.CONNECTOR_ENTITY_CREATED,
        ConnectorPropertyEntity: RoutingKey.CONNECTOR_PROPERTY_ENTITY_CREATED,
        ConnectorControlEntity: RoutingKey.CONNECTOR_CONTROL_ENTITY_CREATED,
        DeviceEntity: RoutingKey.DEVICE_ENTITY_CREATED,
        DevicePropertyEntity: RoutingKey.DEVICE_PROPERTY_ENTITY_CREATED,
        DeviceControlEntity: RoutingKey.DEVICE_CONTROL_ENTITY_CREATED,
        DeviceAttributeEntity: RoutingKey.DEVICE_ATTRIBUTE_ENTITY_CREATED,
        ChannelEntity: RoutingKey.CHANNEL_ENTITY_CREATED,
        ChannelPropertyEntity: RoutingKey.CHANNEL_PROPERTY_ENTITY_CREATED,
        ChannelControlEntity: RoutingKey.CHANNEL_CONTROL_ENTITY_CREATED,
    }

    UPDATED_ENTITIES_ROUTING_KEYS_MAPPING: Dict[Type[Base], RoutingKey] = {
        ConnectorEntity: RoutingKey.CONNECTOR_ENTITY_UPDATED,
        ConnectorPropertyEntity: RoutingKey.CONNECTOR_PROPERTY_ENTITY_UPDATED,
        ConnectorControlEntity: RoutingKey.CONNECTOR_CONTROL_ENTITY_UPDATED,
        DeviceEntity: RoutingKey.DEVICE_ENTITY_UPDATED,
        DevicePropertyEntity: RoutingKey.DEVICE_PROPERTY_ENTITY_UPDATED,
        DeviceControlEntity: RoutingKey.DEVICE_CONTROL_ENTITY_UPDATED,
        DeviceAttributeEntity: RoutingKey.DEVICE_ATTRIBUTE_ENTITY_UPDATED,
        ChannelEntity: RoutingKey.CHANNEL_ENTITY_UPDATED,
        ChannelPropertyEntity: RoutingKey.CHANNEL_PROPERTY_ENTITY_UPDATED,
        ChannelControlEntity: RoutingKey.CHANNEL_CONTROL_ENTITY_UPDATED,
    }

    DELETED_ENTITIES_ROUTING_KEYS_MAPPING: Dict[Type[Base], RoutingKey] = {
        ConnectorEntity: RoutingKey.CONNECTOR_ENTITY_DELETED,
        ConnectorPropertyEntity: RoutingKey.CONNECTOR_PROPERTY_ENTITY_DELETED,
        ConnectorControlEntity: RoutingKey.CONNECTOR_CONTROL_ENTITY_DELETED,
        DeviceEntity: RoutingKey.DEVICE_ENTITY_DELETED,
        DevicePropertyEntity: RoutingKey.DEVICE_PROPERTY_ENTITY_DELETED,
        DeviceControlEntity: RoutingKey.DEVICE_CONTROL_ENTITY_DELETED,
        DeviceAttributeEntity: RoutingKey.DEVICE_ATTRIBUTE_ENTITY_DELETED,
        ChannelEntity: RoutingKey.CHANNEL_ENTITY_DELETED,
        ChannelPropertyEntity: RoutingKey.CHANNEL_PROPERTY_ENTITY_DELETED,
        ChannelControlEntity: RoutingKey.CHANNEL_CONTROL_ENTITY_DELETED,
    }

    __publisher: Optional[Publisher] = None

    __connector_properties_states_repository: ConnectorPropertiesStatesRepository
    __connector_properties_states_manager: ConnectorPropertiesStatesManager
    __device_properties_states_repository: DevicePropertiesStatesRepository
    __device_properties_states_manager: DevicePropertiesStatesManager
    __channel_properties_states_repository: ChannelPropertiesStatesRepository
    __channel_properties_states_manager: ChannelPropertiesStatesManager

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        session: OrmSession,
        connector_properties_states_repository: ConnectorPropertiesStatesRepository,
        connector_properties_states_manager: ConnectorPropertiesStatesManager,
        device_properties_states_repository: DevicePropertiesStatesRepository,
        device_properties_states_manager: DevicePropertiesStatesManager,
        channel_properties_states_repository: ChannelPropertiesStatesRepository,
        channel_properties_states_manager: ChannelPropertiesStatesManager,
        publisher: Optional[Publisher] = None,
    ) -> None:
        self.__publisher = publisher

        self.__connector_properties_states_repository = connector_properties_states_repository
        self.__connector_properties_states_manager = connector_properties_states_manager
        self.__device_properties_states_repository = device_properties_states_repository
        self.__device_properties_states_manager = device_properties_states_manager
        self.__channel_properties_states_repository = channel_properties_states_repository
        self.__channel_properties_states_manager = channel_properties_states_manager

        event.listen(session, "after_flush", lambda active_session, transaction: self.after_flush(active_session))

    # -----------------------------------------------------------------------------

    def after_flush(self, session: OrmSession) -> None:  # pylint: disable=too-many-branches
        """Event"""
        if self.__publisher is None:
            return

        for entity in session.new:
            routing_key = self.__get_entity_created_routing_key(entity=type(entity))

            if routing_key is not None:
                exchange_data = {**entity.to_dict(), **self.__get_entity_extended_data(entity=entity)}

                self.__publisher.publish(
                    source=entity.source,
                    routing_key=routing_key,
                    data=exchange_data,
                )

        for entity in session.dirty:
            if not session.is_modified(entity, include_collections=False):
                continue

            routing_key = self.__get_entity_updated_routing_key(entity=type(entity))

            if routing_key is not None:
                exchange_data = {**entity.to_dict(), **self.__get_entity_extended_data(entity=entity)}

                self.__publisher.publish(
                    source=entity.source,
                    routing_key=routing_key,
                    data=exchange_data,
                )

        for entity in session.deleted:
            routing_key = self.__get_entity_deleted_routing_key(entity=type(entity))

            if routing_key is not None:
                self.__publisher.publish(
                    source=entity.source,
                    routing_key=routing_key,
                    data={**entity.to_dict(), **self.__get_entity_extended_data(entity=entity)},
                )

            if isinstance(entity, ConnectorDynamicPropertyEntity):
                try:
                    connector_property_state = self.__connector_properties_states_repository.get_by_id(
                        property_id=entity.id,
                    )

                    if connector_property_state is not None:
                        self.__connector_properties_states_manager.delete(
                            connector_property=entity,
                            state=connector_property_state,
                        )

                except NotImplementedError:
                    pass

            if isinstance(entity, DeviceDynamicPropertyEntity) and entity.parent is None:
                try:
                    device_property_state = self.__device_properties_states_repository.get_by_id(property_id=entity.id)

                    if device_property_state is not None:
                        self.__device_properties_states_manager.delete(
                            device_property=entity,
                            state=device_property_state,
                        )

                except NotImplementedError:
                    pass

            if isinstance(entity, ChannelDynamicPropertyEntity) and entity.parent is None:
                try:
                    channel_property_state = self.__channel_properties_states_repository.get_by_id(
                        property_id=entity.id,
                    )

                    if channel_property_state is not None:
                        self.__channel_properties_states_manager.delete(
                            channel_property=entity,
                            state=channel_property_state,
                        )

                except NotImplementedError:
                    pass

    # -----------------------------------------------------------------------------

    def __get_entity_created_routing_key(self, entity: Type[Base]) -> Optional[RoutingKey]:
        """Get routing key for created entity"""
        for classname, routing_key in self.CREATED_ENTITIES_ROUTING_KEYS_MAPPING.items():
            if issubclass(entity, classname):
                return routing_key

        return None

    # -----------------------------------------------------------------------------

    def __get_entity_updated_routing_key(self, entity: Type[Base]) -> Optional[RoutingKey]:
        """Get routing key for updated entity"""
        for classname, routing_key in self.UPDATED_ENTITIES_ROUTING_KEYS_MAPPING.items():
            if issubclass(entity, classname):
                return routing_key

        return None

    # -----------------------------------------------------------------------------

    def __get_entity_deleted_routing_key(self, entity: Type[Base]) -> Optional[RoutingKey]:
        """Get routing key for deleted entity"""
        for classname, routing_key in self.DELETED_ENTITIES_ROUTING_KEYS_MAPPING.items():
            if issubclass(entity, classname):
                return routing_key

        return None

    # -----------------------------------------------------------------------------

    def __get_entity_extended_data(self, entity: Base) -> Dict:  # pylint: disable=too-many-return-statements
        if isinstance(entity, ConnectorDynamicPropertyEntity):
            try:
                connector_property_state = self.__connector_properties_states_repository.get_by_id(
                    property_id=entity.id,
                )

            except NotImplementedError:
                return {}

            return connector_property_state.to_dict() if connector_property_state is not None else {}

        if isinstance(entity, DeviceDynamicPropertyEntity) or (
            isinstance(entity, DeviceMappedPropertyEntity) and isinstance(entity.parent, DeviceDynamicPropertyEntity)
        ):
            try:
                device_property_state = self.__device_properties_states_repository.get_by_id(property_id=entity.id)

            except NotImplementedError:
                return {}

            return device_property_state.to_dict() if device_property_state is not None else {}

        if isinstance(entity, ChannelDynamicPropertyEntity) or (
            isinstance(entity, ChannelMappedPropertyEntity) and isinstance(entity.parent, ChannelDynamicPropertyEntity)
        ):
            try:
                channel_property_state = self.__channel_properties_states_repository.get_by_id(property_id=entity.id)

            except NotImplementedError:
                return {}

            return channel_property_state.to_dict() if channel_property_state is not None else {}

        return {}

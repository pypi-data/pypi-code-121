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
Devices module connectors connector worker module
"""

# pylint: disable=too-many-lines

# Python base dependencies
import asyncio
import pkgutil
import re
import time
import types
import uuid
from abc import ABC, abstractmethod
from asyncio import AbstractEventLoop
from importlib import util as import_util
from typing import Dict, Optional, Union

from fastybird_metadata.devices_module import ConnectionState, ConnectorPropertyName

# Library libs
from fastybird_metadata.routing import RoutingKey
from fastybird_metadata.types import ControlAction, DataType
from inflection import underscore
from kink import di
from sqlalchemy.orm import close_all_sessions

# Library dependencies
from fastybird_devices_module.connectors.queue import (
    ConnectorQueue,
    ConsumeControlActionMessageQueueItem,
    ConsumeEntityMessageQueueItem,
    ConsumePropertyActionMessageQueueItem,
)
from fastybird_devices_module.entities.channel import (
    ChannelControlEntity,
    ChannelEntity,
    ChannelPropertyEntity,
)
from fastybird_devices_module.entities.connector import (
    ConnectorControlEntity,
    ConnectorDynamicPropertyEntity,
    ConnectorEntity,
)
from fastybird_devices_module.entities.device import (
    DeviceAttributeEntity,
    DeviceControlEntity,
    DeviceEntity,
    DevicePropertyEntity,
)
from fastybird_devices_module.exceptions import (
    RestartConnectorException,
    TerminateConnectorException,
)
from fastybird_devices_module.logger import Logger
from fastybird_devices_module.managers.connector import ConnectorPropertiesManager
from fastybird_devices_module.managers.state import ConnectorPropertiesStatesManager
from fastybird_devices_module.repositories.channel import (
    ChannelControlsRepository,
    ChannelPropertiesRepository,
    ChannelsRepository,
)
from fastybird_devices_module.repositories.connector import (
    ConnectorControlsRepository,
    ConnectorPropertiesRepository,
    ConnectorsRepository,
)
from fastybird_devices_module.repositories.device import (
    DeviceAttributesRepository,
    DeviceControlsRepository,
    DevicePropertiesRepository,
    DevicesRepository,
)
from fastybird_devices_module.repositories.state import (
    ConnectorPropertiesStatesRepository,
)


class IConnector(ABC):  # pylint: disable=too-many-public-methods
    """
    Connector interface

    @package        FastyBird:DevicesModule!
    @module         connectors/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    # -----------------------------------------------------------------------------

    @property
    @abstractmethod
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Connector identifier"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def initialize(self, connector: ConnectorEntity) -> None:
        """Set connector to initial state"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def initialize_device(self, device: DeviceEntity) -> None:
        """Initialize device in connector"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def remove_device(self, device_id: uuid.UUID) -> None:
        """Remove device from connector"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def reset_devices(self) -> None:
        """Reset devices to initial state"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def initialize_device_property(self, device: DeviceEntity, device_property: DevicePropertyEntity) -> None:
        """Initialize device property in connector"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def notify_device_property(self, device: DeviceEntity, device_property: DevicePropertyEntity) -> None:
        """Notify device property was reported to connector"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def remove_device_property(self, device: DeviceEntity, property_id: uuid.UUID) -> None:
        """Remove device property from connector"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def reset_devices_properties(self, device: DeviceEntity) -> None:
        """Reset devices properties to initial state"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def initialize_device_attribute(self, device: DeviceEntity, device_attribute: DeviceAttributeEntity) -> None:
        """Initialize device attribute in connector"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def notify_device_attribute(self, device: DeviceEntity, device_attribute: DeviceAttributeEntity) -> None:
        """Notify device attribute was reported to connector"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def remove_device_attribute(self, device: DeviceEntity, attribute_id: uuid.UUID) -> None:
        """Remove device attribute from connector"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def reset_devices_attributes(self, device: DeviceEntity) -> None:
        """Reset devices attributes to initial state"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def initialize_device_channel(self, device: DeviceEntity, channel: ChannelEntity) -> None:
        """Initialize device channel in connector"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def remove_device_channel(self, device: DeviceEntity, channel_id: uuid.UUID) -> None:
        """Remove device channel from connector"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def reset_devices_channels(self, device: DeviceEntity) -> None:
        """Reset devices channels to initial state"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def initialize_device_channel_property(
        self,
        channel: ChannelEntity,
        channel_property: ChannelPropertyEntity,
    ) -> None:
        """Initialize device channel property in connector"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def notify_device_channel_property(
        self,
        channel: ChannelEntity,
        channel_property: ChannelPropertyEntity,
    ) -> None:
        """Notify device channel property was reported to connector"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def remove_device_channel_property(self, channel: ChannelEntity, property_id: uuid.UUID) -> None:
        """Remove device channel property from connector"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def reset_devices_channels_properties(self, channel: ChannelEntity) -> None:
        """Reset devices channels properties to initial state"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    async def start(self) -> None:
        """Start connector service"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def stop(self) -> None:
        """Stop connector service"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def has_unfinished_tasks(self) -> bool:
        """Check if connector has some unfinished tasks"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    async def write_property(self, property_item: Union[DevicePropertyEntity, ChannelPropertyEntity], data: Dict) -> None:
        """Write device or channel property value to device"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    async def write_control(
        self,
        control_item: Union[ConnectorControlEntity, DeviceControlEntity, ChannelControlEntity],
        data: Optional[Dict],
        action: ControlAction,
    ) -> None:
        """Write connector control action"""


class Connector:  # pylint: disable=too-many-instance-attributes
    """
    Connector container

    @package        FastyBird:DevicesModule!
    @module         connectors/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __stopped: bool = False

    __queue: ConnectorQueue

    __connector: Optional[IConnector] = None

    __devices_repository: DevicesRepository
    __devices_properties_repository: DevicePropertiesRepository
    __devices_control_repository: DeviceControlsRepository
    __devices_attributes_repository: DeviceAttributesRepository

    __channels_repository: ChannelsRepository
    __channels_properties_repository: ChannelPropertiesRepository
    __channels_control_repository: ChannelControlsRepository

    __connectors_repository: ConnectorsRepository
    __connectors_properties_repository: ConnectorPropertiesRepository
    __connectors_properties_manager: ConnectorPropertiesManager
    __connectors_control_repository: ConnectorControlsRepository
    __connectors_properties_states_repository: ConnectorPropertiesStatesRepository
    __connectors_properties_states_manager: ConnectorPropertiesStatesManager

    __logger: Logger

    __loop: AbstractEventLoop

    __SHUTDOWN_WAITING_DELAY: float = 3.0

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        queue: ConnectorQueue,
        devices_repository: DevicesRepository,
        devices_properties_repository: DevicePropertiesRepository,
        devices_control_repository: DeviceControlsRepository,
        devices_attributes_repository: DeviceAttributesRepository,
        channels_repository: ChannelsRepository,
        channels_properties_repository: ChannelPropertiesRepository,
        channels_control_repository: ChannelControlsRepository,
        connectors_repository: ConnectorsRepository,
        connectors_properties_repository: ConnectorPropertiesRepository,
        connectors_properties_manager: ConnectorPropertiesManager,
        connectors_control_repository: ConnectorControlsRepository,
        connectors_properties_states_repository: ConnectorPropertiesStatesRepository,
        connectors_properties_states_manager: ConnectorPropertiesStatesManager,
        logger: Logger,
        loop: AbstractEventLoop,
    ) -> None:
        self.__queue = queue

        self.__devices_repository = devices_repository
        self.__devices_properties_repository = devices_properties_repository
        self.__devices_control_repository = devices_control_repository
        self.__devices_attributes_repository = devices_attributes_repository

        self.__channels_repository = channels_repository
        self.__channels_properties_repository = channels_properties_repository
        self.__connectors_control_repository = connectors_control_repository

        self.__connectors_repository = connectors_repository
        self.__connectors_properties_repository = connectors_properties_repository
        self.__connectors_properties_manager = connectors_properties_manager
        self.__channels_control_repository = channels_control_repository
        self.__connectors_properties_states_repository = connectors_properties_states_repository
        self.__connectors_properties_states_manager = connectors_properties_states_manager

        self.__logger = logger

        self.__loop = loop

    # -----------------------------------------------------------------------------

    async def start(self) -> None:
        """Start connector service"""
        self.__stopped = False

        try:
            if self.__connector is not None:
                self.__set_state(state=ConnectionState.RUNNING)

                # Register queue coroutine
                asyncio.ensure_future(self.__queue_process())

                # Send start command to loaded connector
                await self.__connector.start()

        except Exception as ex:  # pylint: disable=broad-except
            self.__logger.exception(ex)
            self.__logger.error(
                "Connector couldn't be started. An unexpected error occurred",
                extra={
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )

            raise TerminateConnectorException("Connector couldn't be started. An unexpected error occurred") from ex

    # -----------------------------------------------------------------------------

    def stop(self) -> None:
        """Stop connector service"""
        self.__stopped = True

        self.__logger.info("Stopping connector...")

        try:
            # Send terminate command to...

            # ...connector
            if self.__connector is not None:
                self.__connector.stop()

                now = time.time()

                waiting_for_closing = True

                # Wait until connector is fully terminated
                while waiting_for_closing and time.time() - now < self.__SHUTDOWN_WAITING_DELAY:
                    if not self.__connector.has_unfinished_tasks():
                        waiting_for_closing = False

                self.__set_state(state=ConnectionState.STOPPED)

        except Exception as ex:  # pylint: disable=broad-except
            self.__logger.error(
                "Connector couldn't be stopped. An unexpected error occurred",
                extra={
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )

            raise TerminateConnectorException("Connector couldn't be stopped. An unexpected error occurred") from ex

    # -----------------------------------------------------------------------------

    def load(self, connector_id: uuid.UUID) -> None:
        """Try to load connector"""
        try:
            connectors = self.__import_connectors()

            connector = self.__connectors_repository.get_by_id(connector_id=connector_id)

            if connector is None:
                raise AttributeError(f"Connector {connector_id} was not found in database")

            if underscore(connector.type) not in connectors:
                raise AttributeError(f"Connector {connector.type} couldn't be loaded")

            module = connectors[underscore(connector.type)]

            # Add loaded connector to container to be accessible & autowired
            di["connector"] = connector

            self.__connector = getattr(module, "create_connector")(connector=connector, logger=self.__logger)

            if not isinstance(self.__connector, IConnector):
                raise AttributeError(f"Instance of connector {connector.type} couldn't be created")

            self.__connector.initialize(connector=connector)

        except Exception as ex:  # pylint: disable=broad-except
            self.__logger.exception(ex)
            raise Exception("Connector could not be loaded") from ex

    # -----------------------------------------------------------------------------

    @staticmethod
    def __import_connectors() -> Dict[str, types.ModuleType]:
        connectors: Dict[str, types.ModuleType] = {}

        for module in pkgutil.iter_modules():
            match = re.compile("fastybird_(?P<name>[a-zA-Z_]+)_connector")
            parsed_module_name = match.fullmatch(module.name)

            if parsed_module_name is not None:
                module_spec = import_util.find_spec(name=module.name)

                if module_spec is not None:
                    loaded_module = import_util.module_from_spec(module_spec)
                    module_spec.loader.exec_module(loaded_module)  # type: ignore[union-attr]

                    if hasattr(loaded_module, "create_connector"):
                        connectors[parsed_module_name.group("name")] = loaded_module

        return connectors

    # -----------------------------------------------------------------------------

    async def __queue_process(self) -> None:
        while True:
            # All records have to be processed before process is closed
            if self.__stopped and self.__queue.is_empty():
                return

            queue_item = self.__queue.get()

            if queue_item is not None:
                try:
                    if isinstance(queue_item, ConsumePropertyActionMessageQueueItem):
                        await self.__write_property_command(item=queue_item)

                    if isinstance(queue_item, ConsumeControlActionMessageQueueItem):
                        await self.__write_control_command(item=queue_item)

                    if isinstance(queue_item, ConsumeEntityMessageQueueItem):
                        self.__handle_entity_event(item=queue_item)

                except Exception as ex:  # pylint: disable=broad-except
                    self.__logger.exception(ex)
                    self.__logger.error(
                        "An unexpected error occurred during processing queue item",
                        extra={
                            "exception": {
                                "message": str(ex),
                                "code": type(ex).__name__,
                            },
                        },
                    )

                    self.__loop.stop()

                    return

            await asyncio.sleep(0.01)

    # -----------------------------------------------------------------------------

    async def __write_property_command(  # pylint: disable=too-many-return-statements
        self,
        item: ConsumePropertyActionMessageQueueItem,
    ) -> None:
        if self.__connector is None:
            return

        if item.routing_key == RoutingKey.DEVICE_PROPERTY_ACTION:
            try:
                device_property = self.__devices_properties_repository.get_by_id(
                    property_id=uuid.UUID(item.data.get("property"), version=4),
                )

            except ValueError:
                return

            if device_property is None:
                return

            if device_property.parent_id is not None:
                device_property = self.__devices_properties_repository.get_by_id(
                    property_id=uuid.UUID(bytes=device_property.parent_id, version=4),
                )

            if device_property is None:
                self.__logger.warning("Device property was not found in database")

                return

            await self.__connector.write_property(device_property, item.data)

        if item.routing_key == RoutingKey.CHANNEL_PROPERTY_ACTION:
            try:
                channel_property = self.__channels_properties_repository.get_by_id(
                    property_id=uuid.UUID(item.data.get("property"), version=4),
                )

            except ValueError:
                return

            if channel_property is None:
                return

            if channel_property.parent_id is not None:
                channel_property = self.__channels_properties_repository.get_by_id(
                    property_id=uuid.UUID(bytes=channel_property.parent_id, version=4),
                )

            if channel_property is None:
                self.__logger.warning("Channel property was not found in database")

                return

            await self.__connector.write_property(channel_property, item.data)

    # -----------------------------------------------------------------------------

    async def __write_control_command(  # pylint: disable=too-many-return-statements
        self,
        item: ConsumeControlActionMessageQueueItem,
    ) -> None:
        if self.__connector is None:
            return

        if item.routing_key == RoutingKey.DEVICE_ACTION and ControlAction.has_value(str(item.data.get("name"))):
            try:
                device_control = self.__connectors_control_repository.get_by_name(
                    connector_id=uuid.UUID(item.data.get("connector"), version=4),
                    control_name=str(item.data.get("name")),
                )

            except ValueError:
                return

            if device_control is None:
                self.__logger.warning("Device control was not found in database")

                return

            await self.__connector.write_control(
                control_item=device_control,
                data=item.data,
                action=ControlAction(item.data.get("name")),
            )

        if item.routing_key == RoutingKey.CHANNEL_ACTION and ControlAction.has_value(str(item.data.get("name"))):
            try:
                channel_control = self.__devices_control_repository.get_by_name(
                    device_id=uuid.UUID(item.data.get("device"), version=4), control_name=str(item.data.get("name"))
                )

            except ValueError:
                return

            if channel_control is None:
                self.__logger.warning("Channel control was not found in database")

                return

            await self.__connector.write_control(
                control_item=channel_control,
                data=item.data,
                action=ControlAction(item.data.get("name")),
            )

        if item.routing_key == RoutingKey.CONNECTOR_ACTION and ControlAction.has_value(str(item.data.get("name"))):
            try:
                connector_control = self.__channels_control_repository.get_by_name(
                    channel_id=uuid.UUID(item.data.get("channel"), version=4), control_name=str(item.data.get("name"))
                )

            except ValueError:
                return

            if connector_control is None:
                self.__logger.warning("Connector control was not found in database")

                return

            await self.__connector.write_control(
                control_item=connector_control,
                data=item.data,
                action=ControlAction(item.data.get("name")),
            )

    # -----------------------------------------------------------------------------

    def __handle_entity_event(  # pylint: disable=too-many-branches,too-many-return-statements,too-many-statements
        self,
        item: ConsumeEntityMessageQueueItem,
    ) -> None:
        if self.__connector is None:
            return

        if item.routing_key == RoutingKey.CONNECTOR_ENTITY_UPDATED:
            close_all_sessions()

            try:
                connector_entity = self.__connectors_repository.get_by_id(
                    connector_id=uuid.UUID(item.data.get("id"), version=4),
                )

                if connector_entity is None or not connector_entity.id.__eq__(di["connector"].id):
                    return

            except ValueError:
                return

            if connector_entity is None:
                self.__logger.warning("Connector was not found in database")

                return

            raise RestartConnectorException(
                "Connector was updated in database, terminating connector service in favor of restarting service"
            )

        if item.routing_key == RoutingKey.CONNECTOR_ENTITY_DELETED:
            close_all_sessions()

            try:
                if not di["connector"].id.__eq__(uuid.UUID(item.data.get("id"), version=4)):
                    return

                raise TerminateConnectorException("Connector was removed from database, terminating connector service")

            except ValueError:
                return

        if item.routing_key in (RoutingKey.DEVICE_ENTITY_CREATED, RoutingKey.DEVICE_ENTITY_UPDATED):
            close_all_sessions()

            try:
                device_entity = self.__devices_repository.get_by_id(
                    device_id=uuid.UUID(item.data.get("id"), version=4),
                )

            except ValueError:
                return

            if device_entity is None:
                self.__logger.warning("Device was not found in database")

                return

            self.__connector.initialize_device(device=device_entity)

        if item.routing_key == RoutingKey.DEVICE_ENTITY_DELETED:
            close_all_sessions()

            try:
                self.__connector.remove_device(uuid.UUID(item.data.get("id"), version=4))

            except ValueError:
                return

        if item.routing_key in (
            RoutingKey.DEVICE_PROPERTY_ENTITY_CREATED,
            RoutingKey.DEVICE_PROPERTY_ENTITY_UPDATED,
            RoutingKey.DEVICE_PROPERTY_ENTITY_REPORTED,
        ):
            close_all_sessions()

            try:
                device_entity = self.__devices_repository.get_by_id(
                    device_id=uuid.UUID(item.data.get("device"), version=4),
                )

            except ValueError:
                return

            if device_entity is None:
                return

            try:
                device_property_entity = self.__devices_properties_repository.get_by_id(
                    property_id=uuid.UUID(item.data.get("id"), version=4),
                )

            except ValueError:
                return

            if device_property_entity is None:
                self.__logger.warning("Device property was not found in database")

                return

            if item.routing_key == RoutingKey.DEVICE_PROPERTY_ENTITY_REPORTED:
                self.__connector.notify_device_property(device=device_entity, device_property=device_property_entity)

            else:
                self.__connector.initialize_device_property(
                    device=device_entity,
                    device_property=device_property_entity,
                )

        if item.routing_key == RoutingKey.DEVICE_PROPERTY_ENTITY_DELETED:
            close_all_sessions()

            try:
                device_entity = self.__devices_repository.get_by_id(
                    device_id=uuid.UUID(item.data.get("device"), version=4),
                )

            except ValueError:
                return

            if device_entity is None:
                return

            try:
                self.__connector.remove_device_property(
                    device=device_entity,
                    property_id=uuid.UUID(item.data.get("id"), version=4),
                )

            except ValueError:
                return

        if item.routing_key in (
            RoutingKey.DEVICE_ATTRIBUTE_ENTITY_CREATED,
            RoutingKey.DEVICE_ATTRIBUTE_ENTITY_UPDATED,
            RoutingKey.DEVICE_ATTRIBUTE_ENTITY_REPORTED,
        ):
            close_all_sessions()

            try:
                device_entity = self.__devices_repository.get_by_id(
                    device_id=uuid.UUID(item.data.get("device"), version=4),
                )

            except ValueError:
                return

            if device_entity is None:
                return

            try:
                device_attribute_entity = self.__devices_attributes_repository.get_by_id(
                    attribute_id=uuid.UUID(item.data.get("id"), version=4),
                )

            except ValueError:
                return

            if device_attribute_entity is None:
                self.__logger.warning("Device attribute was not found in database")

                return

            if item.routing_key == RoutingKey.DEVICE_ATTRIBUTE_ENTITY_REPORTED:
                self.__connector.notify_device_attribute(device=device_entity, device_attribute=device_attribute_entity)

            else:
                self.__connector.initialize_device_attribute(
                    device=device_entity,
                    device_attribute=device_attribute_entity,
                )

        if item.routing_key == RoutingKey.DEVICE_ATTRIBUTE_ENTITY_DELETED:
            close_all_sessions()

            try:
                device_entity = self.__devices_repository.get_by_id(
                    device_id=uuid.UUID(item.data.get("device"), version=4),
                )

            except ValueError:
                return

            if device_entity is None:
                return

            try:
                self.__connector.remove_device_attribute(
                    device=device_entity,
                    attribute_id=uuid.UUID(item.data.get("id"), version=4),
                )

            except ValueError:
                return

        if item.routing_key in (RoutingKey.CHANNEL_ENTITY_CREATED, RoutingKey.CHANNEL_ENTITY_UPDATED):
            close_all_sessions()

            try:
                channel_entity = self.__channels_repository.get_by_id(
                    channel_id=uuid.UUID(item.data.get("id"), version=4),
                )

            except ValueError:
                return

            if channel_entity is None:
                self.__logger.warning("Channel was not found in database")

                return

            try:
                device_entity = self.__devices_repository.get_by_id(
                    device_id=uuid.UUID(item.data.get("device"), version=4),
                )

            except ValueError:
                return

            if device_entity is None:
                self.__logger.warning("Device was not found in database")

                return

            self.__connector.initialize_device_channel(device=device_entity, channel=channel_entity)

        if item.routing_key == RoutingKey.CHANNEL_ENTITY_DELETED:
            close_all_sessions()

            try:
                device_entity = self.__devices_repository.get_by_id(
                    device_id=uuid.UUID(item.data.get("device"), version=4),
                )

            except ValueError:
                return

            if device_entity is None:
                return

            try:
                self.__connector.remove_device_channel(
                    device=device_entity,
                    channel_id=uuid.UUID(item.data.get("id"), version=4),
                )

            except ValueError:
                return

        if item.routing_key in (
            RoutingKey.CHANNEL_PROPERTY_ENTITY_CREATED,
            RoutingKey.CHANNEL_PROPERTY_ENTITY_UPDATED,
            RoutingKey.CHANNEL_PROPERTY_ENTITY_REPORTED,
        ):
            close_all_sessions()

            try:
                channel_property_entity = self.__channels_properties_repository.get_by_id(
                    property_id=uuid.UUID(item.data.get("id"), version=4),
                )

            except ValueError:
                return

            if channel_property_entity is None:
                self.__logger.warning("Channel property was not found in database")

                return

            try:
                channel_entity = self.__channels_repository.get_by_id(
                    channel_id=uuid.UUID(item.data.get("channel"), version=4),
                )

            except ValueError:
                return

            if channel_entity is None:
                return

            if item.routing_key == RoutingKey.CHANNEL_PROPERTY_ENTITY_REPORTED:
                self.__connector.notify_device_channel_property(
                    channel=channel_entity, channel_property=channel_property_entity
                )

            else:
                self.__connector.initialize_device_channel_property(
                    channel=channel_entity, channel_property=channel_property_entity
                )

        if item.routing_key == RoutingKey.CHANNEL_PROPERTY_ENTITY_DELETED:
            close_all_sessions()

            try:
                channel_entity = self.__channels_repository.get_by_id(
                    channel_id=uuid.UUID(item.data.get("channel"), version=4),
                )

            except ValueError:
                return

            if channel_entity is None:
                return

            try:
                self.__connector.remove_device_channel_property(
                    channel=channel_entity,
                    property_id=uuid.UUID(item.data.get("id"), version=4),
                )

            except ValueError:
                return

    # -----------------------------------------------------------------------------

    def __set_state(self, state: ConnectionState) -> None:
        if self.__connector is not None:
            state_property = self.__connectors_properties_repository.get_by_identifier(
                connector_id=self.__connector.id,
                property_identifier=ConnectorPropertyName.STATE.value,
            )

            if state_property is None:
                property_data = {
                    "connector_id": self.__connector.id,
                    "identifier": ConnectorPropertyName.STATE.value,
                    "data_type": DataType.ENUM,
                    "unit": None,
                    "format": [
                        ConnectionState.RUNNING.value,
                        ConnectionState.STOPPED.value,
                        ConnectionState.UNKNOWN.value,
                        ConnectionState.SLEEPING.value,
                        ConnectionState.ALERT.value,
                    ],
                    "settable": False,
                    "queryable": False,
                }

                state_property = self.__connectors_properties_manager.create(
                    data=property_data,
                    property_type=ConnectorDynamicPropertyEntity,
                )

            state_property_state = self.__connectors_properties_states_repository.get_by_id(
                property_id=state_property.id,
            )

            if state_property_state is None:
                self.__connectors_properties_states_manager.create(
                    connector_property=state_property,
                    data={
                        "actual_value": state.value,
                        "expected_value": None,
                        "pending": False,
                    },
                )

            else:
                self.__connectors_properties_states_manager.update(
                    connector_property=state_property,
                    state=state_property_state,
                    data={
                        "actual_value": state.value,
                        "expected_value": None,
                        "pending": False,
                    },
                )

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
Devices module device states managers module
"""

# Python base dependencies
from abc import abstractmethod
from datetime import datetime
from typing import Dict, Optional, Union

# Library dependencies
from fastybird_exchange.publisher import Publisher
from fastybird_metadata.routing import RoutingKey
from fastybird_metadata.types import ButtonPayload, SwitchPayload
from kink import inject

# Library libs
from fastybird_devices_module.entities.channel import ChannelPropertyEntity
from fastybird_devices_module.entities.connector import ConnectorPropertyEntity
from fastybird_devices_module.entities.device import DevicePropertyEntity
from fastybird_devices_module.repositories.channel import ChannelPropertiesRepository
from fastybird_devices_module.state.property import (
    IChannelPropertyState,
    IConnectorPropertyState,
    IDevicePropertyState,
)
from fastybird_devices_module.utils import normalize_value


class IConnectorPropertiesStatesManager:
    """
    Connector properties states manager

    @package        FastyBird:ConnectorsModule!
    @module         managers/state

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @abstractmethod
    def create(
        self,
        connector_property: ConnectorPropertyEntity,
        data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
    ) -> IConnectorPropertyState:
        """Create new connector property state record"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def update(
        self,
        connector_property: ConnectorPropertyEntity,
        state: IConnectorPropertyState,
        data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
    ) -> IConnectorPropertyState:
        """Update existing connector property state record"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def delete(
        self,
        connector_property: ConnectorPropertyEntity,
        state: IConnectorPropertyState,
    ) -> bool:
        """Delete existing connector property state"""


class IDevicePropertiesStatesManager:
    """
    Device properties states manager

    @package        FastyBird:DevicesModule!
    @module         managers/state

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @abstractmethod
    def create(
        self,
        device_property: DevicePropertyEntity,
        data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
    ) -> IDevicePropertyState:
        """Create new device property state record"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def update(
        self,
        device_property: DevicePropertyEntity,
        state: IDevicePropertyState,
        data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
    ) -> IDevicePropertyState:
        """Update existing device property state record"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def delete(
        self,
        device_property: DevicePropertyEntity,
        state: IDevicePropertyState,
    ) -> bool:
        """Delete existing device property state"""


class IChannelPropertiesStatesManager:
    """
    Channel properties states manager

    @package        FastyBird:DevicesModule!
    @module         managers/state

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @abstractmethod
    def create(
        self,
        channel_property: ChannelPropertyEntity,
        data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
    ) -> IChannelPropertyState:
        """Create new channel property state record"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def update(
        self,
        channel_property: ChannelPropertyEntity,
        state: IChannelPropertyState,
        data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
    ) -> IChannelPropertyState:
        """Update existing channel property state record"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def delete(
        self,
        channel_property: ChannelPropertyEntity,
        state: IChannelPropertyState,
    ) -> bool:
        """Delete existing channel property state"""


@inject(
    bind={
        "manager": IConnectorPropertiesStatesManager,
        "publisher": Publisher,
    }
)
class ConnectorPropertiesStatesManager:
    """
    Connector properties states manager

    @package        FastyBird:ConnectorsModule!
    @module         managers/state

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __manager: Optional[IConnectorPropertiesStatesManager] = None

    __publisher: Optional[Publisher] = None

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        manager: Optional[IConnectorPropertiesStatesManager] = None,
        publisher: Optional[Publisher] = None,
    ) -> None:
        self.__manager = manager
        self.__publisher = publisher

    # -----------------------------------------------------------------------------

    def create(
        self,
        connector_property: ConnectorPropertyEntity,
        data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
        publish_state: bool = True,
    ) -> IConnectorPropertyState:
        """Create new connector property state record"""
        if self.__manager is None:
            raise NotImplementedError("Connector properties states manager is not implemented")

        created_state = self.__manager.create(connector_property=connector_property, data=data)

        if publish_state:
            self.__publish_entity(
                connector_property=connector_property,
                state=created_state,
            )

        return created_state

    # -----------------------------------------------------------------------------

    def update(
        self,
        connector_property: ConnectorPropertyEntity,
        state: IConnectorPropertyState,
        data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
        publish_state: bool = True,
    ) -> IConnectorPropertyState:
        """Update existing connector property state record"""
        if self.__manager is None:
            raise NotImplementedError("Connector properties states manager is not implemented")

        stored_data = state.to_dict()

        updated_state = self.__manager.update(connector_property=connector_property, state=state, data=data)

        if stored_data != updated_state.to_dict() and publish_state:
            self.__publish_entity(
                connector_property=connector_property,
                state=updated_state,
            )

        return updated_state

    # -----------------------------------------------------------------------------

    def delete(
        self,
        connector_property: ConnectorPropertyEntity,
        state: IConnectorPropertyState,
        publish_state: bool = True,
    ) -> bool:
        """Delete existing connector property state"""
        if self.__manager is None:
            raise NotImplementedError("Connector properties states manager is not implemented")

        result = self.__manager.delete(connector_property=connector_property, state=state)

        if result is True and publish_state:
            self.__publish_entity(
                connector_property=connector_property,
                state=None,
            )

        return result

    # -----------------------------------------------------------------------------

    def __publish_entity(
        self,
        connector_property: ConnectorPropertyEntity,
        state: Optional[IConnectorPropertyState],
    ) -> None:
        if self.__publisher is None:
            return

        actual_value = (
            normalize_value(
                data_type=connector_property.data_type,
                value=state.actual_value,
                value_format=connector_property.format,
                value_invalid=connector_property.invalid,
            )
            if state is not None
            else None
        )
        expected_value = (
            normalize_value(
                data_type=connector_property.data_type,
                value=state.expected_value,
                value_format=connector_property.format,
                value_invalid=connector_property.invalid,
            )
            if state is not None
            else None
        )

        self.__publisher.publish(
            source=connector_property.source,
            routing_key=RoutingKey.CONNECTOR_PROPERTY_ENTITY_REPORTED,
            data={
                **connector_property.to_dict(),
                **{
                    "actual_value": actual_value
                    if isinstance(actual_value, (str, int, float, bool)) or actual_value is None
                    else str(actual_value),
                    "expected_value": expected_value
                    if isinstance(expected_value, (str, int, float, bool)) or expected_value is None
                    else str(expected_value),
                    "pending": state.pending if state is not None else False,
                    "valid": state.valid if state is not None else False,
                },
            },
        )


@inject(
    bind={
        "manager": IDevicePropertiesStatesManager,
        "publisher": Publisher,
    }
)
class DevicePropertiesStatesManager:
    """
    Device properties states manager

    @package        FastyBird:DevicesModule!
    @module         managers/state

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __manager: Optional[IDevicePropertiesStatesManager] = None

    __publisher: Optional[Publisher] = None

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        manager: Optional[IDevicePropertiesStatesManager] = None,
        publisher: Optional[Publisher] = None,
    ) -> None:
        self.__manager = manager
        self.__publisher = publisher

    # -----------------------------------------------------------------------------

    def create(
        self,
        device_property: DevicePropertyEntity,
        data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
        publish_state: bool = True,
    ) -> IDevicePropertyState:
        """Create new device property state record"""
        if self.__manager is None:
            raise NotImplementedError("Device properties states manager is not implemented")

        if device_property.parent is not None:
            raise AttributeError("Child property can't have state")

        created_state = self.__manager.create(device_property=device_property, data=data)

        if publish_state:
            self.__publish_entity(
                device_property=device_property,
                state=created_state,
            )

        return created_state

    # -----------------------------------------------------------------------------

    def update(
        self,
        device_property: DevicePropertyEntity,
        state: IDevicePropertyState,
        data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
        publish_state: bool = True,
    ) -> IDevicePropertyState:
        """Update existing device property state record"""
        if self.__manager is None:
            raise NotImplementedError("Device properties states manager is not implemented")

        if device_property.parent is not None:
            raise AttributeError("Child property can't have state")

        stored_data = state.to_dict()

        updated_state = self.__manager.update(device_property=device_property, state=state, data=data)

        if stored_data != updated_state.to_dict() and publish_state:
            self.__publish_entity(
                device_property=device_property,
                state=updated_state,
            )

            for child in device_property.children:
                self.__publish_entity(
                    device_property=child,
                    state=updated_state,
                )

        return updated_state

    # -----------------------------------------------------------------------------

    def delete(
        self,
        device_property: DevicePropertyEntity,
        state: IDevicePropertyState,
        publish_state: bool = True,
    ) -> bool:
        """Delete existing device property state"""
        if self.__manager is None:
            raise NotImplementedError("Device properties states manager is not implemented")

        if device_property.parent is not None:
            raise AttributeError("Child property can't have state")

        result = self.__manager.delete(device_property=device_property, state=state)

        if result is True and publish_state:
            self.__publish_entity(
                device_property=device_property,
                state=None,
            )

            for child in device_property.children:
                self.__publish_entity(
                    device_property=child,
                    state=None,
                )

        return result

    # -----------------------------------------------------------------------------

    def __publish_entity(
        self,
        device_property: DevicePropertyEntity,
        state: Optional[IDevicePropertyState],
    ) -> None:
        if self.__publisher is None:
            return

        actual_value = (
            normalize_value(
                data_type=device_property.data_type,
                value=state.actual_value,
                value_format=device_property.format,
                value_invalid=device_property.invalid,
            )
            if state is not None
            else None
        )
        expected_value = (
            normalize_value(
                data_type=device_property.data_type,
                value=state.expected_value,
                value_format=device_property.format,
                value_invalid=device_property.invalid,
            )
            if state is not None
            else None
        )

        self.__publisher.publish(
            source=device_property.source,
            routing_key=RoutingKey.DEVICE_PROPERTY_ENTITY_REPORTED,
            data={
                **device_property.to_dict(),
                **{
                    "actual_value": actual_value
                    if isinstance(actual_value, (str, int, float, bool)) or actual_value is None
                    else str(actual_value),
                    "expected_value": expected_value
                    if isinstance(expected_value, (str, int, float, bool)) or expected_value is None
                    else str(expected_value),
                    "pending": state.pending if state is not None else False,
                    "valid": state.valid if state is not None else False,
                },
            },
        )


@inject(
    bind={
        "manager": IChannelPropertiesStatesManager,
        "publisher": Publisher,
    }
)
class ChannelPropertiesStatesManager:
    """
    Channel properties states manager

    @package        FastyBird:DevicesModule!
    @module         managers/state

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __repository: ChannelPropertiesRepository
    __manager: Optional[IChannelPropertiesStatesManager] = None

    __publisher: Optional[Publisher] = None

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        repository: ChannelPropertiesRepository,
        manager: Optional[IChannelPropertiesStatesManager] = None,
        publisher: Optional[Publisher] = None,
    ) -> None:
        self.__repository = repository
        self.__manager = manager
        self.__publisher = publisher

    # -----------------------------------------------------------------------------

    def create(
        self,
        channel_property: ChannelPropertyEntity,
        data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
        publish_state: bool = True,
    ) -> IChannelPropertyState:
        """Create new channel property state record"""
        if self.__manager is None:
            raise NotImplementedError("Channel properties states manager is not implemented")

        if channel_property.parent is not None:
            raise AttributeError("Child property can't have state")

        created_state = self.__manager.create(channel_property=channel_property, data=data)

        if publish_state:
            self.__publish_entity(
                channel_property=channel_property,
                state=created_state,
            )

        return created_state

    # -----------------------------------------------------------------------------

    def update(
        self,
        channel_property: ChannelPropertyEntity,
        state: IChannelPropertyState,
        data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
        publish_state: bool = True,
    ) -> IChannelPropertyState:
        """Update existing channel property state record"""
        if self.__manager is None:
            raise NotImplementedError("Channel properties states manager is not implemented")

        if channel_property.parent is not None:
            raise AttributeError("Child property can't have state")

        stored_data = state.to_dict()

        updated_state = self.__manager.update(channel_property=channel_property, state=state, data=data)

        if stored_data != updated_state.to_dict() and publish_state:
            self.__publish_entity(
                channel_property=channel_property,
                state=updated_state,
            )

            for child in self.__repository.get_all_by_parent(property_id=channel_property.id):
                self.__publish_entity(
                    channel_property=child,
                    state=updated_state,
                )

        return updated_state

    # -----------------------------------------------------------------------------

    def delete(
        self,
        channel_property: ChannelPropertyEntity,
        state: IChannelPropertyState,
        publish_state: bool = True,
    ) -> bool:
        """Delete existing channel property state"""
        if self.__manager is None:
            raise NotImplementedError("Channel properties states manager is not implemented")

        if channel_property.parent is not None:
            raise AttributeError("Child property can't have state")

        result = self.__manager.delete(channel_property=channel_property, state=state)

        if result is True and publish_state:
            self.__publish_entity(
                channel_property=channel_property,
                state=None,
            )

        for child in self.__repository.get_all_by_parent(property_id=channel_property.id):
            self.__publish_entity(
                channel_property=child,
                state=None,
            )

        return result

    # -----------------------------------------------------------------------------

    def __publish_entity(
        self,
        channel_property: ChannelPropertyEntity,
        state: Optional[IChannelPropertyState],
    ) -> None:
        if self.__publisher is None:
            return

        actual_value = (
            normalize_value(
                data_type=channel_property.data_type,
                value=state.actual_value,
                value_format=channel_property.format,
                value_invalid=channel_property.invalid,
            )
            if state is not None
            else None
        )
        expected_value = (
            normalize_value(
                data_type=channel_property.data_type,
                value=state.expected_value,
                value_format=channel_property.format,
                value_invalid=channel_property.invalid,
            )
            if state is not None
            else None
        )

        self.__publisher.publish(
            source=channel_property.source,
            routing_key=RoutingKey.CHANNEL_PROPERTY_ENTITY_REPORTED,
            data={
                **channel_property.to_dict(),
                **{
                    "actual_value": actual_value
                    if isinstance(actual_value, (str, int, float, bool)) or actual_value is None
                    else str(actual_value),
                    "expected_value": expected_value
                    if isinstance(expected_value, (str, int, float, bool)) or expected_value is None
                    else str(expected_value),
                    "pending": state.pending if state is not None else False,
                    "valid": state.valid if state is not None else False,
                },
            },
        )

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
FastyBird MQTT connector registry module models
"""

# pylint: disable=too-many-lines

# Python base dependencies
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

# Library dependencies
from fastybird_devices_module.repositories.state import (
    ChannelPropertiesStatesRepository,
    DevicePropertiesStatesRepository,
)
from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.types import ButtonPayload, DataType, SwitchPayload
from kink import inject
from whistle import EventDispatcher

# Library libs
from fastybird_fb_mqtt_connector.events.events import (
    ChannelPropertyActualValueEvent,
    ChannelPropertyRecordCreatedOrUpdatedEvent,
    ChannelPropertyRecordDeletedEvent,
    ChannelRecordCreatedOrUpdatedEvent,
    ChannelRecordDeletedEvent,
    DeviceAttributeRecordCreatedOrUpdatedEvent,
    DeviceAttributeRecordDeletedEvent,
    DevicePropertyActualValueEvent,
    DevicePropertyRecordCreatedOrUpdatedEvent,
    DevicePropertyRecordDeletedEvent,
    DeviceRecordUpdatedEvent,
    DeviceStateChangedEvent,
)
from fastybird_fb_mqtt_connector.exceptions import InvalidStateException
from fastybird_fb_mqtt_connector.registry.records import (
    ChannelPropertyRecord,
    ChannelRecord,
    DeviceAttributeRecord,
    DevicePropertyRecord,
    DeviceRecord,
)


class DevicesRegistry:
    """
    Devices registry

    @package        FastyBird:FbMqttConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, DeviceRecord] = {}

    __iterator_index = 0

    __properties_registry: "DevicesPropertiesRegistry"
    __attributes_registry: "DevicesAttributesRegistry"
    __channels_registry: "ChannelsRegistry"

    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        properties_registry: "DevicesPropertiesRegistry",
        attributes_registry: "DevicesAttributesRegistry",
        channels_registry: "ChannelsRegistry",
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.__items = {}

        self.__properties_registry = properties_registry
        self.__attributes_registry = attributes_registry
        self.__channels_registry = channels_registry

        self.__event_dispatcher = event_dispatcher

    # -----------------------------------------------------------------------------

    def get_by_id(self, device_id: uuid.UUID) -> Optional[DeviceRecord]:
        """Find device in registry by given unique identifier"""
        items = self.__items.copy()

        return next(
            iter([record for record in items.values() if device_id.__eq__(record.id)]),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_by_identifier(self, device_identifier: str) -> Optional[DeviceRecord]:
        """Find device in registry by given unique identifier"""
        items = self.__items.copy()

        return next(iter([record for record in items.values() if record.identifier == device_identifier]), None)

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        device_identifier: str,
        device_name: Optional[str],
        device_state: ConnectionState = ConnectionState.UNKNOWN,
        controls: Union[List[str], None] = None,
    ) -> DeviceRecord:
        """Append device record into registry"""
        device_record = DeviceRecord(
            device_id=device_id,
            device_identifier=device_identifier,
            device_name=device_name,
            device_state=device_state,
            controls=controls,
        )

        self.__items[device_record.id.__str__()] = device_record

        return device_record

    # -----------------------------------------------------------------------------

    def update(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        device_identifier: str,
        device_name: Optional[str],
        controls: Union[List[str], None] = None,
    ) -> DeviceRecord:
        """Create or update device record"""
        device_record = self.append(
            device_id=device_id,
            device_identifier=device_identifier,
            device_name=device_name,
            controls=controls,
        )

        self.__event_dispatcher.dispatch(
            event_id=DeviceRecordUpdatedEvent.EVENT_NAME,
            event=DeviceRecordUpdatedEvent(record=device_record),
        )

        return device_record

    # -----------------------------------------------------------------------------

    def remove(self, device_id: uuid.UUID) -> None:
        """Remove device from registry"""
        items = self.__items.copy()

        for record in items.values():
            if device_id.__eq__(record.id):
                try:
                    del self.__items[record.id.__str__()]

                    self.__properties_registry.reset(device_id=record.id)
                    self.__attributes_registry.reset(device_id=record.id)
                    self.__channels_registry.reset(device_id=record.id)

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self) -> None:
        """Reset devices registry to initial state"""
        items = self.__items.copy()

        for record in items.values():
            self.__properties_registry.reset(device_id=record.id)
            self.__attributes_registry.reset(device_id=record.id)
            self.__channels_registry.reset(device_id=record.id)

        self.__items = {}

    # -----------------------------------------------------------------------------

    def set_state(
        self,
        device: DeviceRecord,
        state: ConnectionState,
    ) -> DeviceRecord:
        """Set device last received communication timestamp"""
        device.state = state

        self.__update(device=device)

        updated_device = self.get_by_id(device_id=device.id)

        if updated_device is None:
            raise InvalidStateException("Device record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=DeviceStateChangedEvent.EVENT_NAME,
            event=DeviceStateChangedEvent(record=updated_device),
        )

        return updated_device

    # -----------------------------------------------------------------------------

    def __update(self, device: DeviceRecord) -> bool:
        items = self.__items.copy()

        for record in items.values():
            if record.id == device.id:
                self.__items[device.id.__str__()] = device

                return True

        return False

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "DevicesRegistry":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.__items.values())

    # -----------------------------------------------------------------------------

    def __next__(self) -> DeviceRecord:
        if self.__iterator_index < len(self.__items.values()):
            items: List[DeviceRecord] = list(self.__items.values())

            result: DeviceRecord = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration


@inject
class DevicesPropertiesRegistry:
    """
    Devices properties registry

    @package        FastyBird:FbMqttConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, DevicePropertyRecord] = {}

    __iterator_index = 0

    __event_dispatcher: EventDispatcher

    __device_property_state_repository: DevicePropertiesStatesRepository

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        event_dispatcher: EventDispatcher,
        device_property_state_repository: DevicePropertiesStatesRepository,
    ) -> None:
        self.__items = {}

        self.__event_dispatcher = event_dispatcher

        self.__device_property_state_repository = device_property_state_repository

    # -----------------------------------------------------------------------------

    def get_by_id(self, property_id: uuid.UUID) -> Optional[DevicePropertyRecord]:
        """Find property in registry by given unique identifier"""
        items = self.__items.copy()

        return next(
            iter([record for record in items.values() if property_id.__eq__(record.id)]),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_by_identifier(self, device_id: uuid.UUID, property_identifier: str) -> Optional[DevicePropertyRecord]:
        """Find property in registry by given device unique identifier and property unique identifier"""
        items = self.__items.copy()

        return next(
            iter(
                [
                    record
                    for record in items.values()
                    if device_id.__eq__(record.device_id) and record.identifier == property_identifier
                ]
            ),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_all_for_device(self, device_id: uuid.UUID) -> List[DevicePropertyRecord]:
        """Find properties in registry by device unique identifier"""
        items = self.__items.copy()

        return [record for record in items.values() if device_id.__eq__(record.device_id)]

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        property_id: uuid.UUID,
        property_identifier: str,
        property_name: Optional[str] = None,
        property_data_type: DataType = DataType.UNKNOWN,
        property_value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ] = None,
        property_unit: Optional[str] = None,
        property_queryable: bool = False,
        property_settable: bool = False,
    ) -> DevicePropertyRecord:
        """Append property record into registry"""
        existing_property = self.get_by_id(property_id=property_id)

        property_record: DevicePropertyRecord = DevicePropertyRecord(
            device_id=device_id,
            property_id=property_id,
            property_identifier=property_identifier,
            property_name=property_name,
            property_data_type=property_data_type,
            property_value_format=property_value_format,
            property_unit=property_unit,
            property_queryable=property_queryable,
            property_settable=property_settable,
        )

        if existing_property is None:
            try:
                stored_state = self.__device_property_state_repository.get_by_id(property_id=property_id)

                if stored_state is not None:
                    property_record.actual_value = stored_state.actual_value
                    property_record.expected_value = stored_state.expected_value
                    property_record.expected_pending = stored_state.pending

            except (NotImplementedError, AttributeError):
                pass

        self.__items[property_record.id.__str__()] = property_record

        return property_record

    # -----------------------------------------------------------------------------

    def create_or_update(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        property_id: uuid.UUID,
        property_identifier: str,
        property_name: Optional[str] = None,
        property_data_type: DataType = DataType.UNKNOWN,
        property_value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ] = None,
        property_unit: Optional[str] = None,
        property_queryable: bool = False,
        property_settable: bool = False,
    ) -> DevicePropertyRecord:
        """Create or update property record"""
        property_record = self.append(
            device_id=device_id,
            property_id=property_id,
            property_identifier=property_identifier,
            property_name=property_name,
            property_data_type=property_data_type,
            property_value_format=property_value_format,
            property_unit=property_unit,
            property_queryable=property_queryable,
            property_settable=property_settable,
        )

        self.__event_dispatcher.dispatch(
            event_id=DevicePropertyRecordCreatedOrUpdatedEvent.EVENT_NAME,
            event=DevicePropertyRecordCreatedOrUpdatedEvent(record=property_record),
        )

        return property_record

    # -----------------------------------------------------------------------------

    def remove(self, property_id: uuid.UUID, propagate: bool = True) -> None:
        """Remove property from registry"""
        items = self.__items.copy()

        for record in items.values():
            if property_id.__eq__(record.id):
                try:
                    del self.__items[record.id.__str__()]

                    if propagate:
                        self.__event_dispatcher.dispatch(
                            event_id=DevicePropertyRecordDeletedEvent.EVENT_NAME,
                            event=DevicePropertyRecordDeletedEvent(record=record),
                        )

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self, device_id: Optional[uuid.UUID] = None) -> None:
        """Reset properties registry to initial state"""
        items = self.__items.copy()

        if device_id is not None:
            for record in items.values():
                if device_id.__eq__(record.device_id):
                    self.remove(property_id=record.id)

        else:
            self.__items = {}

    # -----------------------------------------------------------------------------

    def set_actual_value(
        self,
        device_property: DevicePropertyRecord,
        value: Union[str, int, float, bool, datetime, SwitchPayload, ButtonPayload, None],
    ) -> DevicePropertyRecord:
        """Set property actual value"""
        existing_record = self.get_by_id(property_id=device_property.id)

        device_property.actual_value = value

        self.__update(device_property=device_property)

        updated_device_property = self.get_by_id(property_id=device_property.id)

        if updated_device_property is None:
            raise InvalidStateException("Device property record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=DevicePropertyActualValueEvent.EVENT_NAME,
            event=DevicePropertyActualValueEvent(
                original_record=existing_record,
                updated_record=updated_device_property,
            ),
        )

        return updated_device_property

    # -----------------------------------------------------------------------------

    def set_expected_value(
        self,
        device_property: DevicePropertyRecord,
        value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None],
    ) -> DevicePropertyRecord:
        """Set property expected value"""
        existing_record = self.get_by_id(property_id=device_property.id)

        device_property.expected_value = value

        self.__update(device_property=device_property)

        updated_device_property = self.get_by_id(device_property.id)

        if updated_device_property is None:
            raise InvalidStateException("Device property record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=DevicePropertyActualValueEvent.EVENT_NAME,
            event=DevicePropertyActualValueEvent(
                original_record=existing_record,
                updated_record=updated_device_property,
            ),
        )

        return updated_device_property

    # -----------------------------------------------------------------------------

    def set_expected_pending(self, device_property: DevicePropertyRecord, timestamp: float) -> DevicePropertyRecord:
        """Set property expected value transmit timestamp"""
        existing_record = self.get_by_id(property_id=device_property.id)

        device_property.expected_pending = timestamp

        self.__update(device_property=device_property)

        updated_device_property = self.get_by_id(device_property.id)

        if updated_device_property is None:
            raise InvalidStateException("Device property record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=DevicePropertyActualValueEvent.EVENT_NAME,
            event=DevicePropertyActualValueEvent(
                original_record=existing_record,
                updated_record=updated_device_property,
            ),
        )

        return updated_device_property

    # -----------------------------------------------------------------------------

    def __update(self, device_property: DevicePropertyRecord) -> bool:
        items = self.__items.copy()

        for record in items.values():
            if record.id == device_property.id:
                self.__items[device_property.id.__str__()] = device_property

                return True

        return False

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "DevicesPropertiesRegistry":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.__items.values())

    # -----------------------------------------------------------------------------

    def __next__(self) -> DevicePropertyRecord:
        if self.__iterator_index < len(self.__items.values()):
            items: List[DevicePropertyRecord] = list(self.__items.values())

            result: DevicePropertyRecord = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration


@inject
class DevicesAttributesRegistry:
    """
    Devices attributes registry

    @package        FastyBird:FbMqttConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, DeviceAttributeRecord] = {}

    __iterator_index = 0

    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.__items = {}

        self.__event_dispatcher = event_dispatcher

    # -----------------------------------------------------------------------------

    def get_by_id(self, attribute_id: uuid.UUID) -> Optional[DeviceAttributeRecord]:
        """Find attribute in registry by given unique identifier"""
        items = self.__items.copy()

        return next(
            iter([record for record in items.values() if attribute_id.__eq__(record.id)]),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_by_identifier(self, device_id: uuid.UUID, attribute_identifier: str) -> Optional[DeviceAttributeRecord]:
        """Find attribute in registry by given device unique identifier and attribute unique identifier"""
        items = self.__items.copy()

        return next(
            iter(
                [
                    record
                    for record in items.values()
                    if device_id.__eq__(record.device_id) and record.identifier == attribute_identifier
                ]
            ),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_all_for_device(self, device_id: uuid.UUID) -> List[DeviceAttributeRecord]:
        """Find attributes in registry by device unique identifier"""
        items = self.__items.copy()

        return [record for record in items.values() if device_id.__eq__(record.device_id)]

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        attribute_id: uuid.UUID,
        attribute_identifier: str,
        attribute_name: Optional[str] = None,
        attribute_value: Optional[str] = None,
    ) -> DeviceAttributeRecord:
        """Append attribute record into registry"""
        attribute_record: DeviceAttributeRecord = DeviceAttributeRecord(
            device_id=device_id,
            attribute_id=attribute_id,
            attribute_identifier=attribute_identifier,
            attribute_name=attribute_name,
            attribute_value=attribute_value,
        )

        self.__items[attribute_record.id.__str__()] = attribute_record

        return attribute_record

    # -----------------------------------------------------------------------------

    def create_or_update(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        attribute_id: uuid.UUID,
        attribute_identifier: str,
        attribute_name: Optional[str] = None,
        attribute_value: Optional[str] = None,
    ) -> DeviceAttributeRecord:
        """Create or update attribute record"""
        attribute_record = self.append(
            device_id=device_id,
            attribute_id=attribute_id,
            attribute_identifier=attribute_identifier,
            attribute_name=attribute_name,
            attribute_value=attribute_value,
        )

        self.__event_dispatcher.dispatch(
            event_id=DeviceAttributeRecordCreatedOrUpdatedEvent.EVENT_NAME,
            event=DeviceAttributeRecordCreatedOrUpdatedEvent(record=attribute_record),
        )

        return attribute_record

    # -----------------------------------------------------------------------------

    def remove(self, attribute_id: uuid.UUID, propagate: bool = True) -> None:
        """Remove attribute from registry"""
        items = self.__items.copy()

        for record in items.values():
            if attribute_id.__eq__(record.id):
                try:
                    del self.__items[record.id.__str__()]

                    if propagate:
                        self.__event_dispatcher.dispatch(
                            event_id=DeviceAttributeRecordDeletedEvent.EVENT_NAME,
                            event=DeviceAttributeRecordDeletedEvent(record=record),
                        )

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self, device_id: Optional[uuid.UUID] = None) -> None:
        """Reset attributes registry to initial state"""
        items = self.__items.copy()

        if device_id is not None:
            for record in items.values():
                if device_id.__eq__(record.device_id):
                    self.remove(attribute_id=record.id)

        else:
            self.__items = {}

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "DevicesAttributesRegistry":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.__items.values())

    # -----------------------------------------------------------------------------

    def __next__(self) -> DeviceAttributeRecord:
        if self.__iterator_index < len(self.__items.values()):
            items: List[DeviceAttributeRecord] = list(self.__items.values())

            result: DeviceAttributeRecord = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration


class ChannelsRegistry:
    """
    Channels registry

    @package        FastyBird:FbMqttConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, ChannelRecord] = {}

    __properties_registry: "ChannelsPropertiesRegistry"

    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        properties_registry: "ChannelsPropertiesRegistry",
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.__items = {}

        self.__properties_registry = properties_registry

        self.__event_dispatcher = event_dispatcher

    # -----------------------------------------------------------------------------

    def get_by_id(self, channel_id: uuid.UUID) -> Optional[ChannelRecord]:
        """Find channel in registry by given unique identifier"""
        items = self.__items.copy()

        return next(
            iter([record for record in items.values() if channel_id.__eq__(record.id)]),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_by_identifier(self, device_id: uuid.UUID, channel_identifier: str) -> Optional[ChannelRecord]:
        """Find channel in registry by given unique identifier and device unique identifier"""
        items = self.__items.copy()

        return next(
            iter(
                [
                    record
                    for record in items.values()
                    if device_id.__eq__(record.device_id) and record.identifier == channel_identifier
                ]
            ),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_all_by_device(self, device_id: uuid.UUID) -> List[ChannelRecord]:
        """Find channels in registry by device unique identifier"""
        items = self.__items.copy()

        return list(iter([record for record in items.values() if device_id.__eq__(record.device_id)]))

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        channel_id: uuid.UUID,
        channel_identifier: str,
        channel_name: Optional[str] = None,
        controls: Union[List[str], None] = None,
    ) -> ChannelRecord:
        """Append channel record into registry"""
        channel_record: ChannelRecord = ChannelRecord(
            device_id=device_id,
            channel_id=channel_id,
            channel_identifier=channel_identifier,
            channel_name=channel_name,
            controls=controls,
        )

        self.__items[channel_record.id.__str__()] = channel_record

        return channel_record

    # -----------------------------------------------------------------------------

    def create_or_update(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        channel_id: uuid.UUID,
        channel_identifier: str,
        channel_name: Optional[str] = None,
        controls: Union[List[str], None] = None,
    ) -> ChannelRecord:
        """Create or update channel record"""
        channel_record = self.append(
            device_id=device_id,
            channel_id=channel_id,
            channel_identifier=channel_identifier,
            channel_name=channel_name,
            controls=controls,
        )

        self.__event_dispatcher.dispatch(
            event_id=ChannelRecordCreatedOrUpdatedEvent.EVENT_NAME,
            event=ChannelRecordCreatedOrUpdatedEvent(record=channel_record),
        )

        return channel_record

    # -----------------------------------------------------------------------------

    def remove(self, channel_id: uuid.UUID, propagate: bool = True) -> None:
        """Remove channel from registry"""
        items = self.__items.copy()

        for record in items.values():
            if channel_id.__eq__(record.id):
                try:
                    del self.__items[record.id.__str__()]

                    if propagate:
                        self.__event_dispatcher.dispatch(
                            event_id=ChannelRecordDeletedEvent.EVENT_NAME,
                            event=ChannelRecordDeletedEvent(record=record),
                        )

                    self.__properties_registry.reset(channel_id=record.id)

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self, device_id: Optional[uuid.UUID] = None) -> None:
        """Reset channels registry to initial state"""
        items = self.__items.copy()

        if device_id is not None:
            for record in items.values():
                if device_id.__eq__(record.device_id):
                    self.remove(channel_id=record.id)

        else:
            for record in items.values():
                self.__properties_registry.reset(channel_id=record.id)

            self.__items = {}


@inject
class ChannelsPropertiesRegistry:
    """
    Channels properties registry

    @package        FastyBird:FbMqttConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, ChannelPropertyRecord] = {}

    __iterator_index = 0

    __event_dispatcher: EventDispatcher

    __channel_property_state_repository: ChannelPropertiesStatesRepository

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        event_dispatcher: EventDispatcher,
        channel_property_state_repository: ChannelPropertiesStatesRepository,
    ) -> None:
        self.__items = {}

        self.__event_dispatcher = event_dispatcher

        self.__channel_property_state_repository = channel_property_state_repository

    # -----------------------------------------------------------------------------

    def get_by_id(self, property_id: uuid.UUID) -> Optional[ChannelPropertyRecord]:
        """Find property in registry by given unique identifier"""
        items = self.__items.copy()

        return next(
            iter([record for record in items.values() if property_id.__eq__(record.id)]),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_by_identifier(self, channel_id: uuid.UUID, property_identifier: str) -> Optional[ChannelPropertyRecord]:
        """Find property in registry by given channel unique database identifier and property unique identifier"""
        items = self.__items.copy()

        return next(
            iter(
                [
                    record
                    for record in items.values()
                    if channel_id.__eq__(record.channel_id) and record.identifier == property_identifier
                ]
            ),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_all_for_channel(self, channel_id: uuid.UUID) -> List[ChannelPropertyRecord]:
        """Find properties in registry by channel unique identifier"""
        items = self.__items.copy()

        return [record for record in items.values() if channel_id.__eq__(record.channel_id)]

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-arguments
        self,
        channel_id: uuid.UUID,
        property_id: uuid.UUID,
        property_identifier: str,
        property_name: Optional[str] = None,
        property_data_type: DataType = DataType.UNKNOWN,
        property_value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ] = None,
        property_unit: Optional[str] = None,
        property_queryable: bool = False,
        property_settable: bool = False,
    ) -> ChannelPropertyRecord:
        """Append property record into registry"""
        existing_property = self.get_by_id(property_id=property_id)

        property_record: ChannelPropertyRecord = ChannelPropertyRecord(
            channel_id=channel_id,
            property_id=property_id,
            property_identifier=property_identifier,
            property_name=property_name,
            property_data_type=property_data_type,
            property_value_format=property_value_format,
            property_unit=property_unit,
            property_queryable=property_queryable,
            property_settable=property_settable,
        )

        if existing_property is None:
            try:
                stored_state = self.__channel_property_state_repository.get_by_id(property_id=property_id)

                if stored_state is not None:
                    property_record.actual_value = stored_state.actual_value
                    property_record.expected_value = stored_state.expected_value
                    property_record.expected_pending = stored_state.pending

            except (NotImplementedError, AttributeError):
                pass

        self.__items[property_record.id.__str__()] = property_record

        return property_record

    # -----------------------------------------------------------------------------

    def create_or_update(  # pylint: disable=too-many-arguments
        self,
        channel_id: uuid.UUID,
        property_id: uuid.UUID,
        property_identifier: str,
        property_name: Optional[str] = None,
        property_data_type: DataType = DataType.UNKNOWN,
        property_value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ] = None,
        property_unit: Optional[str] = None,
        property_queryable: bool = False,
        property_settable: bool = False,
    ) -> ChannelPropertyRecord:
        """Create or update property record"""
        property_record = self.append(
            channel_id=channel_id,
            property_id=property_id,
            property_identifier=property_identifier,
            property_name=property_name,
            property_data_type=property_data_type,
            property_value_format=property_value_format,
            property_unit=property_unit,
            property_queryable=property_queryable,
            property_settable=property_settable,
        )

        self.__event_dispatcher.dispatch(
            event_id=ChannelPropertyRecordCreatedOrUpdatedEvent.EVENT_NAME,
            event=ChannelPropertyRecordCreatedOrUpdatedEvent(record=property_record),
        )

        return property_record

    # -----------------------------------------------------------------------------

    def remove(self, property_id: uuid.UUID, propagate: bool = True) -> None:
        """Remove property from registry"""
        items = self.__items.copy()

        for record in items.values():
            if property_id.__eq__(record.id):
                try:
                    del self.__items[record.id.__str__()]

                    if propagate:
                        self.__event_dispatcher.dispatch(
                            event_id=ChannelPropertyRecordDeletedEvent.EVENT_NAME,
                            event=ChannelPropertyRecordDeletedEvent(record=record),
                        )

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self, channel_id: Optional[uuid.UUID] = None) -> None:
        """Reset properties registry to initial state"""
        items = self.__items.copy()

        if channel_id is not None:
            for record in items.values():
                if channel_id.__eq__(record.channel_id):
                    self.remove(property_id=record.id)

        else:
            self.__items = {}

    # -----------------------------------------------------------------------------

    def set_actual_value(
        self,
        channel_property: ChannelPropertyRecord,
        value: Union[str, int, float, bool, datetime, SwitchPayload, ButtonPayload, None],
    ) -> ChannelPropertyRecord:
        """Set property actual value"""
        existing_record = self.get_by_id(property_id=channel_property.id)

        channel_property.actual_value = value

        self.__update(channel_property=channel_property)

        updated_channel_property = self.get_by_id(property_id=channel_property.id)

        if updated_channel_property is None:
            raise InvalidStateException("Channel property record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=ChannelPropertyActualValueEvent.EVENT_NAME,
            event=ChannelPropertyActualValueEvent(
                original_record=existing_record,
                updated_record=updated_channel_property,
            ),
        )

        return updated_channel_property

    # -----------------------------------------------------------------------------

    def set_expected_value(
        self,
        channel_property: ChannelPropertyRecord,
        value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None],
    ) -> ChannelPropertyRecord:
        """Set property expected value"""
        existing_record = self.get_by_id(property_id=channel_property.id)

        channel_property.expected_value = value

        self.__update(channel_property=channel_property)

        updated_channel_property = self.get_by_id(channel_property.id)

        if updated_channel_property is None:
            raise InvalidStateException("Channel property record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=ChannelPropertyActualValueEvent.EVENT_NAME,
            event=ChannelPropertyActualValueEvent(
                original_record=existing_record,
                updated_record=updated_channel_property,
            ),
        )

        return updated_channel_property

    # -----------------------------------------------------------------------------

    def set_expected_pending(self, channel_property: ChannelPropertyRecord, timestamp: float) -> ChannelPropertyRecord:
        """Set property expected value transmit timestamp"""
        existing_record = self.get_by_id(property_id=channel_property.id)

        channel_property.expected_pending = timestamp

        self.__update(channel_property=channel_property)

        updated_channel_property = self.get_by_id(channel_property.id)

        if updated_channel_property is None:
            raise InvalidStateException("Channel property record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=ChannelPropertyActualValueEvent.EVENT_NAME,
            event=ChannelPropertyActualValueEvent(
                original_record=existing_record,
                updated_record=updated_channel_property,
            ),
        )

        return updated_channel_property

    # -----------------------------------------------------------------------------

    def __update(self, channel_property: ChannelPropertyRecord) -> bool:
        items = self.__items.copy()

        for record in items.values():
            if record.id == channel_property.id:
                self.__items[channel_property.id.__str__()] = channel_property

                return True

        return False

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "ChannelsPropertiesRegistry":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.__items.values())

    # -----------------------------------------------------------------------------

    def __next__(self) -> ChannelPropertyRecord:
        if self.__iterator_index < len(self.__items.values()):
            items: List[ChannelPropertyRecord] = list(self.__items.values())

            result: ChannelPropertyRecord = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration

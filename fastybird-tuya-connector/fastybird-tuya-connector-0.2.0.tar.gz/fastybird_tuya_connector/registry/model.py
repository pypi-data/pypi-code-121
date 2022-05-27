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

# pylint: disable=too-many-lines

"""
Tuya connector registry module models
"""

# Python base dependencies
import uuid
from typing import Dict, List, Optional, Set, Tuple, Union

# Library dependencies
from fastybird_devices_module.repositories.state import (
    ChannelPropertiesStatesRepository,
)
from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.types import DataType
from kink import inject
from whistle import EventDispatcher

# Library libs
from fastybird_tuya_connector.events.events import (
    AttributeActualValueEvent,
    DataPointActualValueEvent,
    DataPointRecordCreatedOrUpdatedEvent,
    DeviceAttributeRecordCreatedOrUpdatedEvent,
    DevicePropertyRecordCreatedOrUpdatedEvent,
    DeviceRecordCreatedOrUpdatedEvent,
    PropertyActualValueEvent,
)
from fastybird_tuya_connector.exceptions import InvalidStateException
from fastybird_tuya_connector.registry.records import (
    AttributeRecord,
    DataPointRecord,
    DeviceRecord,
    DiscoveredDataPoint,
    DiscoveredDevice,
    PropertyRecord,
    TuyaCloudDataPoint,
    TuyaCloudDevice,
)
from fastybird_tuya_connector.types import (
    DataPointType,
    DeviceAttribute,
    DeviceProperty,
)


class DevicesRegistry:  # pylint: disable=too-many-instance-attributes
    """
    Devices registry

    @package        FastyBird:TuyaConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, DeviceRecord] = {}

    __iterator_index = 0

    __data_points_registry: "DataPointsRegistry"
    __attributes_registry: "AttributesRegistry"
    __properties_registry: "PropertiesRegistry"

    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        data_points_registry: "DataPointsRegistry",
        attributes_registry: "AttributesRegistry",
        properties_registry: "PropertiesRegistry",
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.__items = {}

        self.__data_points_registry = data_points_registry
        self.__attributes_registry = attributes_registry
        self.__properties_registry = properties_registry

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

    def append(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: uuid.UUID,
        device_identifier: str,
        device_name: Optional[str] = None,
    ) -> DeviceRecord:
        """Append device record into registry"""
        device_record = DeviceRecord(
            device_id=device_id,
            device_identifier=device_identifier,
            device_name=device_name,
        )

        self.__items[device_record.id.__str__()] = device_record

        return device_record

    # -----------------------------------------------------------------------------

    def create_or_update(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: uuid.UUID,
        device_identifier: str,
        device_name: Optional[str] = None,
    ) -> DeviceRecord:
        """Create or update device record"""
        device_record = self.append(
            device_id=device_id,
            device_identifier=device_identifier,
            device_name=device_name,
        )

        self.__event_dispatcher.dispatch(
            event_id=DeviceRecordCreatedOrUpdatedEvent.EVENT_NAME,
            event=DeviceRecordCreatedOrUpdatedEvent(record=device_record),
        )

        state_property = self.__properties_registry.get_by_property(
            device_id=device_record.id,
            property_type=DeviceProperty.STATE,
        )

        if state_property is None:
            self.__properties_registry.create_or_update(
                device_id=device_record.id,
                property_type=DeviceProperty.STATE,
                property_value=ConnectionState.UNKNOWN.value,
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

                    self.__data_points_registry.reset(device_id=record.id)
                    self.__attributes_registry.reset(device_id=record.id)
                    self.__properties_registry.reset(device_id=record.id)

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self) -> None:
        """Reset devices registry to initial state"""
        items = self.__items.copy()

        for record in items.values():
            self.__data_points_registry.reset(device_id=record.id)
            self.__attributes_registry.reset(device_id=record.id)
            self.__properties_registry.reset(device_id=record.id)

        self.__items = {}

    # -----------------------------------------------------------------------------

    def set_last_communication_timestamp(
        self,
        device: DeviceRecord,
        last_communication_timestamp: Optional[float],
    ) -> DeviceRecord:
        """Set device last received communication timestamp"""
        device.last_communication_timestamp = last_communication_timestamp

        self.__update(device=device)

        updated_device = self.get_by_id(device_id=device.id)

        if updated_device is None:
            raise InvalidStateException("Device record could not be re-fetched from registry after update")

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
class DataPointsRegistry:
    """
    DataPoints registry

    @package        FastyBird:TuyaConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, DataPointRecord] = {}

    __event_dispatcher: EventDispatcher

    __channel_property_state_repository: ChannelPropertiesStatesRepository

    __iterator_index = 0

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

    def get_by_id(self, dp_id: uuid.UUID) -> Optional[DataPointRecord]:
        """Find data point in registry by given unique identifier"""
        items = self.__items.copy()

        return next(
            iter([record for record in items.values() if dp_id.__eq__(record.id)]),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_by_index(self, device_id: uuid.UUID, dp_index: int) -> Optional[DataPointRecord]:
        """Find data point in registry by given unique identifier and device unique index"""
        items = self.__items.copy()

        return next(
            iter(
                [record for record in items.values() if device_id.__eq__(record.device_id) and record.index == dp_index]
            ),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_by_identifier(self, device_id: uuid.UUID, dp_identifier: str) -> Optional[DataPointRecord]:
        """Find data point in registry by given unique identifier and device unique identifier"""
        items = self.__items.copy()

        return next(
            iter(
                [
                    record
                    for record in items.values()
                    if device_id.__eq__(record.device_id) and record.identifier == dp_identifier
                ]
            ),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_all_by_device(self, device_id: uuid.UUID) -> List[DataPointRecord]:
        """Find data points in registry by device unique identifier"""
        items = self.__items.copy()

        return list(iter([record for record in items.values() if device_id.__eq__(record.device_id)]))

    # -----------------------------------------------------------------------------

    def get_all_by_type(self, dp_type: DataPointType) -> List[DataPointRecord]:
        """Find data points in registry by data point type"""
        items = self.__items.copy()

        return list(iter([record for record in items.values() if dp_type == record.type]))

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: uuid.UUID,
        dp_id: uuid.UUID,
        dp_type: DataPointType,
        dp_data_type: DataType,
        dp_identifier: Optional[str] = None,
        dp_index: Optional[int] = None,
        dp_name: Optional[str] = None,
        dp_unit: Optional[str] = None,
        dp_value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ] = None,
        dp_queryable: bool = False,
        dp_settable: bool = False,
    ) -> DataPointRecord:
        """Append data point record into registry"""
        existing_dp = self.get_by_id(dp_id=dp_id)

        dp_record: DataPointRecord = DataPointRecord(
            device_id=device_id,
            dp_id=dp_id,
            dp_identifier=dp_identifier,
            dp_index=dp_index,
            dp_type=dp_type,
            dp_name=dp_name,
            dp_unit=dp_unit,
            dp_data_type=dp_data_type,
            dp_value_format=dp_value_format,
            dp_queryable=dp_queryable,
            dp_settable=dp_settable,
        )

        if existing_dp is None:
            try:
                stored_state = self.__channel_property_state_repository.get_by_id(property_id=dp_id)

                if stored_state is not None:
                    if isinstance(stored_state.actual_value, (str, int, bool)):
                        dp_record.actual_value = stored_state.actual_value

                    if isinstance(stored_state.expected_value, (str, int, bool)):
                        dp_record.expected_value = stored_state.expected_value

                    dp_record.expected_pending = None

            except (NotImplementedError, AttributeError):
                pass

        self.__items[dp_record.id.__str__()] = dp_record

        return dp_record

    # -----------------------------------------------------------------------------

    def create_or_update(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: uuid.UUID,
        dp_id: uuid.UUID,
        dp_type: DataPointType,
        dp_data_type: DataType,
        dp_identifier: Optional[str] = None,
        dp_index: Optional[int] = None,
        dp_name: Optional[str] = None,
        dp_unit: Optional[str] = None,
        dp_value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ] = None,
        dp_queryable: bool = False,
        dp_settable: bool = False,
    ) -> DataPointRecord:
        """Create or update data point record"""
        dp_record = self.append(
            device_id=device_id,
            dp_id=dp_id,
            dp_identifier=dp_identifier,
            dp_index=dp_index,
            dp_type=dp_type,
            dp_name=dp_name,
            dp_unit=dp_unit,
            dp_data_type=dp_data_type,
            dp_value_format=dp_value_format,
            dp_queryable=dp_queryable,
            dp_settable=dp_settable,
        )

        self.__event_dispatcher.dispatch(
            event_id=DataPointRecordCreatedOrUpdatedEvent.EVENT_NAME,
            event=DataPointRecordCreatedOrUpdatedEvent(record=dp_record),
        )

        return dp_record

    # -----------------------------------------------------------------------------

    def remove(self, dp_id: uuid.UUID) -> None:
        """Remove data point from registry"""
        items = self.__items.copy()

        for record in items.values():
            if dp_id.__eq__(record.id):
                try:
                    del self.__items[record.id.__str__()]

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self, device_id: Optional[uuid.UUID] = None) -> None:
        """Reset data points registry to initial state"""
        items = self.__items.copy()

        if device_id is not None:
            for record in items.values():
                if device_id.__eq__(record.device_id):
                    self.remove(dp_id=record.id)

        else:
            self.__items = {}

    # -----------------------------------------------------------------------------

    def set_actual_value(
        self,
        data_point: DataPointRecord,
        value: Union[str, int, bool, None],
    ) -> DataPointRecord:
        """Set data point actual value"""
        existing_record = self.get_by_id(dp_id=data_point.id)

        data_point.actual_value = value
        data_point.actual_value_valid = True

        self.__update(data_point=data_point)

        updated_data_point = self.get_by_id(dp_id=data_point.id)

        if updated_data_point is None:
            raise InvalidStateException("Data point record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=DataPointActualValueEvent.EVENT_NAME,
            event=DataPointActualValueEvent(
                original_record=existing_record,
                updated_record=updated_data_point,
            ),
        )

        return updated_data_point

    # -----------------------------------------------------------------------------

    def set_expected_value(
        self,
        data_point: DataPointRecord,
        value: Union[str, int, bool, None],
    ) -> DataPointRecord:
        """Set data point expected value"""
        existing_record = self.get_by_id(dp_id=data_point.id)

        data_point.expected_value = value

        self.__update(data_point=data_point)

        updated_data_point = self.get_by_id(data_point.id)

        if updated_data_point is None:
            raise InvalidStateException("Data point record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=DataPointActualValueEvent.EVENT_NAME,
            event=DataPointActualValueEvent(
                original_record=existing_record,
                updated_record=updated_data_point,
            ),
        )

        return updated_data_point

    # -----------------------------------------------------------------------------

    def set_expected_pending(self, data_point: DataPointRecord, timestamp: float) -> DataPointRecord:
        """Set data point expected value transmit timestamp"""
        data_point.expected_pending = timestamp

        self.__update(data_point=data_point)

        updated_data_point = self.get_by_id(data_point.id)

        if updated_data_point is None:
            raise InvalidStateException("Data point record could not be re-fetched from registry after update")

        return updated_data_point

    # -----------------------------------------------------------------------------

    def set_valid_state(self, data_point: DataPointRecord, state: bool) -> DataPointRecord:
        """Set data point actual value reading state"""
        existing_record = self.get_by_id(dp_id=data_point.id)

        data_point.actual_value_valid = state

        self.__update(data_point=data_point)

        updated_data_point = self.get_by_id(data_point.id)

        if updated_data_point is None:
            raise InvalidStateException("Data point record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=DataPointActualValueEvent.EVENT_NAME,
            event=DataPointActualValueEvent(
                original_record=existing_record,
                updated_record=updated_data_point,
            ),
        )

        return updated_data_point

    # -----------------------------------------------------------------------------

    def __update(self, data_point: DataPointRecord) -> bool:
        items = self.__items.copy()

        for record in items.values():
            if record.id == data_point.id:
                self.__items[data_point.id.__str__()] = data_point

                return True

        return False

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "DataPointsRegistry":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.__items.values())

    # -----------------------------------------------------------------------------

    def __next__(self) -> DataPointRecord:
        if self.__iterator_index < len(self.__items.values()):
            items: List[DataPointRecord] = list(self.__items.values())

            result: DataPointRecord = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration


class PropertiesRegistry:
    """
    Properties registry

    @package        FastyBird:TuyaConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, PropertyRecord] = {}

    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.__items = {}

        self.__event_dispatcher = event_dispatcher

    # -----------------------------------------------------------------------------

    def get_by_id(self, property_id: uuid.UUID) -> Optional[PropertyRecord]:
        """Find property in registry by given unique identifier"""
        items = self.__items.copy()

        return next(
            iter([record for record in items.values() if property_id.__eq__(record.id)]),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_by_property(self, device_id: uuid.UUID, property_type: DeviceProperty) -> Optional[PropertyRecord]:
        """Find device property in registry by given unique type in given device"""
        items = self.__items.copy()

        return next(
            iter(
                [
                    record
                    for record in items.values()
                    if device_id.__eq__(record.device_id) and record.type == property_type
                ]
            ),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_all_by_device(self, device_id: uuid.UUID) -> List[PropertyRecord]:
        """Get all device properties"""
        items = self.__items.copy()

        return list(iter([record for record in items.values() if device_id.__eq__(record.device_id)]))

    # -----------------------------------------------------------------------------

    def get_all_by_type(self, property_type: DeviceProperty) -> List[PropertyRecord]:
        """Get all properties by given type"""
        items = self.__items.copy()

        return list(iter([record for record in items.values() if record.type == property_type]))

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        property_id: uuid.UUID,
        property_type: DeviceProperty,
        property_value: Union[str, int, bool, None],
    ) -> PropertyRecord:
        """Append new device record"""
        property_record = PropertyRecord(
            device_id=device_id,
            property_id=property_id,
            property_type=property_type,
            property_value=property_value,
        )

        self.__items[property_record.id.__str__()] = property_record

        return property_record

    # -----------------------------------------------------------------------------

    def create_or_update(
        self,
        device_id: uuid.UUID,
        property_type: DeviceProperty,
        property_value: Union[str, int, bool, None],
    ) -> PropertyRecord:
        """Create or update device property record"""
        existing_record = self.get_by_property(device_id=device_id, property_type=property_type)

        property_record = self.append(
            device_id=device_id,
            property_id=existing_record.id if existing_record is not None else uuid.uuid4(),
            property_type=property_type,
            property_value=property_value,
        )

        self.__event_dispatcher.dispatch(
            event_id=DevicePropertyRecordCreatedOrUpdatedEvent.EVENT_NAME,
            event=DevicePropertyRecordCreatedOrUpdatedEvent(record=property_record),
        )

        return property_record

    # -----------------------------------------------------------------------------

    def remove(self, property_id: uuid.UUID) -> None:
        """Remove device property from registry"""
        items = self.__items.copy()

        for record in items.values():
            if property_id.__eq__(record.id):
                try:
                    del self.__items[record.id.__str__()]

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self, device_id: Optional[uuid.UUID] = None) -> None:
        """Reset devices properties registry to initial state"""
        items = self.__items.copy()

        if device_id is not None:
            for record in items.values():
                if device_id.__eq__(record.device_id):
                    try:
                        self.remove(property_id=record.id)

                    except KeyError:
                        pass

        else:
            self.__items = {}

    # -----------------------------------------------------------------------------

    def set_value(
        self,
        device_property: PropertyRecord,
        value: Union[str, bool, None],
    ) -> PropertyRecord:
        """Set property value"""
        existing_record = self.get_by_id(property_id=device_property.id)

        device_property.actual_value = value

        self.__update(device_property=device_property)

        updated_property = self.get_by_id(property_id=device_property.id)

        if updated_property is None:
            raise InvalidStateException("Property record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=PropertyActualValueEvent.EVENT_NAME,
            event=PropertyActualValueEvent(
                original_record=existing_record,
                updated_record=updated_property,
            ),
        )

        return updated_property

    # -----------------------------------------------------------------------------

    def __update(self, device_property: PropertyRecord) -> bool:
        items = self.__items.copy()

        for record in items.values():
            if record.id == device_property.id:
                self.__items[device_property.id.__str__()] = device_property

                return True

        return False


class AttributesRegistry:
    """
    Attributes registry

    @package        FastyBird:TuyaConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, AttributeRecord] = {}

    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.__items = {}

        self.__event_dispatcher = event_dispatcher

    # -----------------------------------------------------------------------------

    def get_by_id(self, attribute_id: uuid.UUID) -> Optional[AttributeRecord]:
        """Find attribute in registry by given unique identifier"""
        items = self.__items.copy()

        return next(
            iter([record for record in items.values() if attribute_id.__eq__(record.id)]),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_by_attribute(self, device_id: uuid.UUID, attribute_type: DeviceAttribute) -> Optional[AttributeRecord]:
        """Find device attribute in registry by given unique type in given device"""
        items = self.__items.copy()

        return next(
            iter(
                [
                    record
                    for record in items.values()
                    if device_id.__eq__(record.device_id) and record.type == attribute_type
                ]
            ),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_all_by_device(self, device_id: uuid.UUID) -> List[AttributeRecord]:
        """Get all device attributes"""
        items = self.__items.copy()

        return list(iter([record for record in items.values() if device_id.__eq__(record.device_id)]))

    # -----------------------------------------------------------------------------

    def get_all_by_type(self, attribute_type: DeviceAttribute) -> List[AttributeRecord]:
        """Get all attributes by given type"""
        items = self.__items.copy()

        return list(iter([record for record in items.values() if record.type == attribute_type]))

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        attribute_id: uuid.UUID,
        attribute_type: DeviceAttribute,
        attribute_value: Union[int, str, None],
    ) -> AttributeRecord:
        """Append new device record"""
        attribute_record = AttributeRecord(
            device_id=device_id,
            attribute_id=attribute_id,
            attribute_type=attribute_type,
            attribute_value=attribute_value,
        )

        self.__items[attribute_record.id.__str__()] = attribute_record

        return attribute_record

    # -----------------------------------------------------------------------------

    def create_or_update(
        self,
        device_id: uuid.UUID,
        attribute_type: DeviceAttribute,
        attribute_value: Union[int, str, None],
    ) -> AttributeRecord:
        """Create or update device attribute record"""
        existing_record = self.get_by_attribute(device_id=device_id, attribute_type=attribute_type)

        attribute_record = self.append(
            device_id=device_id,
            attribute_id=existing_record.id if existing_record is not None else uuid.uuid4(),
            attribute_type=attribute_type,
            attribute_value=attribute_value,
        )

        self.__event_dispatcher.dispatch(
            event_id=DeviceAttributeRecordCreatedOrUpdatedEvent.EVENT_NAME,
            event=DeviceAttributeRecordCreatedOrUpdatedEvent(record=attribute_record),
        )

        return attribute_record

    # -----------------------------------------------------------------------------

    def remove(self, attribute_id: uuid.UUID) -> None:
        """Remove device attribute from registry"""
        items = self.__items.copy()

        for record in items.values():
            if attribute_id.__eq__(record.id):
                try:
                    del self.__items[record.id.__str__()]

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self, device_id: Optional[uuid.UUID] = None) -> None:
        """Reset devices attributes registry to initial state"""
        items = self.__items.copy()

        if device_id is not None:
            for record in items.values():
                if device_id.__eq__(record.device_id):
                    try:
                        self.remove(attribute_id=record.id)

                    except KeyError:
                        pass

        else:
            self.__items = {}

    # -----------------------------------------------------------------------------

    def set_value(
        self,
        attribute: AttributeRecord,
        value: Union[str, bool, None],
    ) -> AttributeRecord:
        """Set attribute value"""
        existing_record = self.get_by_id(attribute_id=attribute.id)

        attribute.value = value

        self.__update(attribute=attribute)

        updated_attribute = self.get_by_id(attribute_id=attribute.id)

        if updated_attribute is None:
            raise InvalidStateException("Attribute record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=AttributeActualValueEvent.EVENT_NAME,
            event=AttributeActualValueEvent(
                original_record=existing_record,
                updated_record=updated_attribute,
            ),
        )

        return updated_attribute

    # -----------------------------------------------------------------------------

    def __update(self, attribute: AttributeRecord) -> bool:
        items = self.__items.copy()

        for record in items.values():
            if record.id == attribute.id:
                self.__items[attribute.id.__str__()] = attribute

                return True

        return False


class DiscoveredDevicesRegistry:
    """
    Discovered devices registry

    @package        FastyBird:TuyaConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, DiscoveredDevice] = {}

    __iterator_index = 0

    __data_points_registry: "DiscoveredDataPointsRegistry"

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        data_points_registry: "DiscoveredDataPointsRegistry",
    ) -> None:
        self.__data_points_registry = data_points_registry

        self.__items = {}

    # -----------------------------------------------------------------------------

    def get_by_id(self, device_id: str) -> Optional[DiscoveredDevice]:
        """Find device in registry by given unique identifier"""
        items = self.__items.copy()

        return next(
            iter([record for record in items.values() if device_id == record.id]),
            None,
        )

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: str,
        device_ip_address: str,
        device_product_key: str,
        device_encrypted: bool,
        device_version: str,
    ) -> DiscoveredDevice:
        """Append device record into registry"""
        device_record = DiscoveredDevice(
            device_id=device_id,
            device_ip_address=device_ip_address,
            device_product_key=device_product_key,
            device_encrypted=device_encrypted,
            device_version=device_version,
        )

        self.__items[device_record.id] = device_record

        return device_record

    # -----------------------------------------------------------------------------

    def remove(self, device_id: str) -> None:
        """Remove device from registry"""
        items = self.__items.copy()

        for record in items.values():
            if device_id.__eq__(record.id):
                try:
                    del self.__items[record.id.__str__()]

                    self.__data_points_registry.reset(device_id=record.id)

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self) -> None:
        """Reset devices registry to initial state"""
        items = self.__items.copy()

        for record in items.values():
            self.__data_points_registry.reset(device_id=record.id)

        self.__items = {}

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "DiscoveredDevicesRegistry":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.__items.values())

    # -----------------------------------------------------------------------------

    def __next__(self) -> DiscoveredDevice:
        if self.__iterator_index < len(self.__items.values()):
            items: List[DiscoveredDevice] = list(self.__items.values())

            result: DiscoveredDevice = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration

    # -----------------------------------------------------------------------------

    def __getitem__(self, index: int) -> DiscoveredDevice:
        if index < len(self.__items.values()):
            items: List[DiscoveredDevice] = list(self.__items.values())

            return items[index]

        raise ValueError("Provided unknown index")


class DiscoveredDataPointsRegistry:
    """
    Discovered devices DPS registry

    @package        FastyBird:TuyaConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Set[DiscoveredDataPoint] = set()

    __iterator_index = 0

    # -----------------------------------------------------------------------------

    def __init__(self) -> None:
        self.__items = set()

    # -----------------------------------------------------------------------------

    def get_by_index(self, device_id: str, dp_index: int) -> Optional[DiscoveredDataPoint]:
        """Find DP in registry by given unique index"""
        items = self.__items.copy()

        return next(
            iter([record for record in items if device_id == record.device_id and dp_index == record.index]),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_all_by_device(self, device_id: str) -> List[DiscoveredDataPoint]:
        """Get all device data points"""
        items = self.__items.copy()

        return list(iter([record for record in items if device_id == record.device_id]))

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: str,
        dp_index: int,
        dp_type: DataPointType,
        dp_data_type: DataType,
    ) -> DiscoveredDataPoint:
        """Append device record into registry"""
        dp_record = DiscoveredDataPoint(
            device_id=device_id,
            dp_index=dp_index,
            dp_type=dp_type,
            dp_data_type=dp_data_type,
        )

        self.__items.add(dp_record)

        return dp_record

    # -----------------------------------------------------------------------------

    def create_or_update(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: str,
        dp_index: int,
        dp_type: DataPointType,
        dp_data_type: DataType,
    ) -> DiscoveredDataPoint:
        """Create or update data point record"""
        dp_record = self.append(
            device_id=device_id,
            dp_index=dp_index,
            dp_type=dp_type,
            dp_data_type=dp_data_type,
        )

        return dp_record

    # -----------------------------------------------------------------------------

    def reset(self, device_id: Optional[str] = None) -> None:
        """Reset devices commands registry to initial state"""
        items = self.__items.copy()

        if device_id is not None:
            for record in items:
                if device_id == record.device_id:
                    self.__items.remove(record)

        else:
            self.__items = set()

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "DiscoveredDataPointsRegistry":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.__items)

    # -----------------------------------------------------------------------------

    def __next__(self) -> DiscoveredDataPoint:
        if self.__iterator_index < len(self.__items):
            items: List[DiscoveredDataPoint] = list(self.__items)

            result: DiscoveredDataPoint = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration


class TuyaCloudDevicesRegistry:
    """
    Tuya cloud devices registry

    @package        FastyBird:TuyaConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, TuyaCloudDevice] = {}

    __iterator_index = 0

    __data_points_registry: "TuyaCloudDataPointsRegistry"

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        data_points_registry: "TuyaCloudDataPointsRegistry",
    ) -> None:
        self.__items = {}

        self.__data_points_registry = data_points_registry

    # -----------------------------------------------------------------------------

    def get_by_id(self, device_id: str) -> Optional[TuyaCloudDevice]:
        """Find device in registry by given unique identifier"""
        items = self.__items.copy()

        return next(
            iter([record for record in items.values() if device_id == record.id]),
            None,
        )

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: str,
        device_local_key: str,
        device_name: str,
        device_uid: str,
        device_model: str,
        device_serial_number: Optional[str] = None,
        device_mac_address: Optional[str] = None,
    ) -> TuyaCloudDevice:
        """Append device record into registry"""
        device_record = TuyaCloudDevice(
            device_id=device_id,
            device_local_key=device_local_key,
            device_name=device_name,
            device_uid=device_uid,
            device_model=device_model,
            device_serial_number=device_serial_number,
            device_mac_address=device_mac_address,
        )

        self.__items[device_record.id] = device_record

        return device_record

    # -----------------------------------------------------------------------------

    def create_or_update(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: str,
        device_local_key: str,
        device_name: str,
        device_uid: str,
        device_model: str,
        device_serial_number: Optional[str] = None,
        device_mac_address: Optional[str] = None,
    ) -> TuyaCloudDevice:
        """Create or update device record"""
        device_record = self.append(
            device_id=device_id,
            device_local_key=device_local_key,
            device_name=device_name,
            device_uid=device_uid,
            device_model=device_model,
            device_serial_number=device_serial_number,
            device_mac_address=device_mac_address,
        )

        return device_record

    # -----------------------------------------------------------------------------

    def remove(self, device_id: str) -> None:
        """Remove device from registry"""
        items = self.__items.copy()

        for record in items.values():
            if device_id.__eq__(record.id):
                try:
                    del self.__items[record.id.__str__()]

                    self.__data_points_registry.reset(device_id=record.id)

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self) -> None:
        """Reset devices registry to initial state"""
        items = self.__items.copy()

        for record in items.values():
            self.__data_points_registry.reset(device_id=record.id)

        self.__items = {}

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "TuyaCloudDevicesRegistry":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.__items.values())

    # -----------------------------------------------------------------------------

    def __next__(self) -> TuyaCloudDevice:
        if self.__iterator_index < len(self.__items.values()):
            items: List[TuyaCloudDevice] = list(self.__items.values())

            result: TuyaCloudDevice = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration


class TuyaCloudDataPointsRegistry:
    """
    Tuya cloud devices DPS registry

    @package        FastyBird:TuyaConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Set[TuyaCloudDataPoint] = set()

    __iterator_index = 0

    # -----------------------------------------------------------------------------

    def __init__(self) -> None:
        self.__items = set()

    # -----------------------------------------------------------------------------

    def get_by_code(self, device_id: str, dp_code: str) -> Optional[TuyaCloudDataPoint]:
        """Find DP in registry by given unique code"""
        items = self.__items.copy()

        return next(
            iter([record for record in items if device_id == record.device_id and dp_code == record.code]),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_all_by_device(self, device_id: str) -> List[TuyaCloudDataPoint]:
        """Get all device data points"""
        items = self.__items.copy()

        return list(iter([record for record in items if device_id == record.device_id]))

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: str,
        dp_code: str,
        dp_type: DataPointType,
        dp_name: str,
        dp_data_type: DataType,
        dp_value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ] = None,
        dp_unit: Optional[str] = None,
        dp_min_value: Optional[int] = None,
        dp_max_value: Optional[int] = None,
        dp_step_value: Optional[int] = None,
        dp_queryable: bool = False,
        dp_settable: bool = False,
    ) -> TuyaCloudDataPoint:
        """Append device record into registry"""
        dp_record = TuyaCloudDataPoint(
            device_id=device_id,
            dp_code=dp_code,
            dp_type=dp_type,
            dp_name=dp_name,
            dp_data_type=dp_data_type,
            dp_value_format=dp_value_format,
            dp_unit=dp_unit,
            dp_min_value=dp_min_value,
            dp_max_value=dp_max_value,
            dp_step_value=dp_step_value,
            dp_queryable=dp_queryable,
            dp_settable=dp_settable,
        )

        self.__items.add(dp_record)

        return dp_record

    # -----------------------------------------------------------------------------

    def create_or_update(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: str,
        dp_code: str,
        dp_type: DataPointType,
        dp_name: str,
        dp_data_type: DataType,
        dp_value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ] = None,
        dp_unit: Optional[str] = None,
        dp_min_value: Optional[int] = None,
        dp_max_value: Optional[int] = None,
        dp_step_value: Optional[int] = None,
        dp_queryable: bool = False,
        dp_settable: bool = False,
    ) -> TuyaCloudDataPoint:
        """Create or update data point record"""
        dp_record = self.append(
            device_id=device_id,
            dp_code=dp_code,
            dp_type=dp_type,
            dp_name=dp_name,
            dp_data_type=dp_data_type,
            dp_value_format=dp_value_format,
            dp_unit=dp_unit,
            dp_min_value=dp_min_value,
            dp_max_value=dp_max_value,
            dp_step_value=dp_step_value,
            dp_queryable=dp_queryable,
            dp_settable=dp_settable,
        )

        return dp_record

    # -----------------------------------------------------------------------------

    def reset(self, device_id: Optional[str] = None) -> None:
        """Reset devices commands registry to initial state"""
        items = self.__items.copy()

        if device_id is not None:
            for record in items:
                if device_id == record.device_id:
                    self.__items.remove(record)

        else:
            self.__items = set()

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "TuyaCloudDataPointsRegistry":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.__items)

    # -----------------------------------------------------------------------------

    def __next__(self) -> TuyaCloudDataPoint:
        if self.__iterator_index < len(self.__items):
            items: List[TuyaCloudDataPoint] = list(self.__items)

            result: TuyaCloudDataPoint = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration

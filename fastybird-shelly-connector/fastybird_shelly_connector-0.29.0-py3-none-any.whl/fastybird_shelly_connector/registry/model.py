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
Shelly connector registry module models
"""

# Python base dependencies
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

# Library dependencies
from fastybird_devices_module.repositories.state import (
    ChannelPropertiesStatesRepository,
)
from fastybird_metadata.types import ButtonPayload, DataType, SwitchPayload
from kink import inject
from whistle import EventDispatcher

# Library libs
from fastybird_shelly_connector.events.events import (
    BlockRecordCreatedOrUpdatedEvent,
    DeviceRecordCreatedOrUpdatedEvent,
    PropertyActualValueEvent,
    PropertyRecordCreatedOrUpdatedEvent,
    SensorActualValueEvent,
    SensorRecordCreatedOrUpdatedEvent,
)
from fastybird_shelly_connector.exceptions import InvalidStateException
from fastybird_shelly_connector.registry.records import (
    BlockRecord,
    CommandRecord,
    DeviceRecord,
    PropertyRecord,
    SensorRecord,
)
from fastybird_shelly_connector.types import (
    ClientType,
    DeviceCommandType,
    DeviceDescriptionSource,
    DeviceProperty,
    SensorType,
    SensorUnit,
)


class DevicesRegistry:  # pylint: disable=too-many-instance-attributes
    """
    Devices registry

    @package        FastyBird:ShellyConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, DeviceRecord] = {}

    __iterator_index = 0

    __commands_registry: "CommandsRegistry"
    __properties_registry: "PropertiesRegistry"
    __blocks_registry: "BlocksRegistry"

    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        commands_registry: "CommandsRegistry",
        properties_registry: "PropertiesRegistry",
        blocks_registry: "BlocksRegistry",
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.__items = {}

        self.__commands_registry = commands_registry
        self.__properties_registry = properties_registry
        self.__blocks_registry = blocks_registry

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
        """Find device in registry by given unique shelly identifier"""
        items = self.__items.copy()

        return next(iter([record for record in items.values() if record.identifier == device_identifier]), None)

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        description_source: DeviceDescriptionSource,
        device_id: uuid.UUID,
        device_identifier: str,
        device_type: Optional[str] = None,
        device_mac_address: Optional[str] = None,
        device_firmware_version: Optional[str] = None,
        device_name: Optional[str] = None,
    ) -> DeviceRecord:
        """Append device record into registry"""
        device_record = DeviceRecord(
            device_id=device_id,
            device_identifier=device_identifier,
            device_type=device_type,
            device_mac_address=device_mac_address,
            device_firmware_version=device_firmware_version,
            device_name=device_name,
        )

        device_record.add_description_source(description_source=description_source)

        existing_record = self.get_by_id(device_id=device_id)

        if existing_record is not None:
            for previous_description_source in existing_record.description_source:
                device_record.add_description_source(description_source=previous_description_source)

            device_record.last_communication_timestamp = existing_record.last_communication_timestamp

        self.__items[device_record.id.__str__()] = device_record

        return device_record

    # -----------------------------------------------------------------------------

    def create_or_update(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        description_source: DeviceDescriptionSource,
        device_id: uuid.UUID,
        device_identifier: str,
        device_type: Optional[str] = None,
        device_mac_address: Optional[str] = None,
        device_firmware_version: Optional[str] = None,
        device_name: Optional[str] = None,
    ) -> DeviceRecord:
        """Create or update device record"""
        device_record = self.append(
            device_id=device_id,
            device_identifier=device_identifier,
            device_type=device_type,
            device_mac_address=device_mac_address,
            device_firmware_version=device_firmware_version,
            description_source=description_source,
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
                property_value=None,
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

                    self.__commands_registry.reset(device_id=record.id)
                    self.__properties_registry.reset(device_id=record.id)
                    self.__blocks_registry.reset(device_id=record.id)

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self) -> None:
        """Reset devices registry to initial state"""
        items = self.__items.copy()

        for record in items.values():
            self.__commands_registry.reset(device_id=record.id)
            self.__properties_registry.reset(device_id=record.id)
            self.__blocks_registry.reset(device_id=record.id)

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


class BlocksRegistry:
    """
    Blocks registry

    @package        FastyBird:ShellyConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, BlockRecord] = {}

    __sensors_registry: "SensorsRegistry"

    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        sensors_registry: "SensorsRegistry",
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.__items = {}

        self.__sensors_registry = sensors_registry

        self.__event_dispatcher = event_dispatcher

    # -----------------------------------------------------------------------------

    def get_by_id(self, block_id: uuid.UUID) -> Optional[BlockRecord]:
        """Find block in registry by given unique identifier"""
        items = self.__items.copy()

        return next(
            iter([record for record in items.values() if block_id.__eq__(record.id)]),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_by_identifier(self, device_id: uuid.UUID, block_identifier: int) -> Optional[BlockRecord]:
        """Find block in registry by given unique shelly identifier and device unique identifier"""
        items = self.__items.copy()

        return next(
            iter(
                [
                    record
                    for record in items.values()
                    if device_id.__eq__(record.device_id) and record.identifier == block_identifier
                ]
            ),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_all_by_device(self, device_id: uuid.UUID) -> List[BlockRecord]:
        """Find blocks in registry by device unique identifier"""
        items = self.__items.copy()

        return list(iter([record for record in items.values() if device_id.__eq__(record.device_id)]))

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: uuid.UUID,
        block_id: uuid.UUID,
        block_identifier: int,
        block_description: str,
    ) -> BlockRecord:
        """Append block record into registry"""
        block_record: BlockRecord = BlockRecord(
            device_id=device_id,
            block_id=block_id,
            block_identifier=block_identifier,
            block_description=block_description,
        )

        self.__items[block_record.id.__str__()] = block_record

        return block_record

    # -----------------------------------------------------------------------------

    def create_or_update(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: uuid.UUID,
        block_id: uuid.UUID,
        block_identifier: int,
        block_description: str,
    ) -> BlockRecord:
        """Create or update block record"""
        block_record = self.append(
            device_id=device_id,
            block_id=block_id,
            block_identifier=block_identifier,
            block_description=block_description,
        )

        self.__event_dispatcher.dispatch(
            event_id=BlockRecordCreatedOrUpdatedEvent.EVENT_NAME,
            event=BlockRecordCreatedOrUpdatedEvent(record=block_record),
        )

        return block_record

    # -----------------------------------------------------------------------------

    def remove(self, block_id: uuid.UUID) -> None:
        """Remove block from registry"""
        items = self.__items.copy()

        for record in items.values():
            if block_id.__eq__(record.id):
                try:
                    del self.__items[record.id.__str__()]

                    self.__sensors_registry.reset(block_id=record.id)

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self, device_id: Optional[uuid.UUID] = None) -> None:
        """Reset blocks registry to initial state"""
        items = self.__items.copy()

        if device_id is not None:
            for record in items.values():
                if device_id.__eq__(record.device_id):
                    self.remove(block_id=record.id)

        else:
            for record in items.values():
                self.__sensors_registry.reset(block_id=record.id)

            self.__items = {}


@inject
class SensorsRegistry:
    """
    Sensors&States registry

    @package        FastyBird:ShellyConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, SensorRecord] = {}

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

    def get_by_id(self, sensor_id: uuid.UUID) -> Optional[SensorRecord]:
        """Find sensor&state in registry by given unique identifier"""
        items = self.__items.copy()

        return next(
            iter([record for record in items.values() if sensor_id.__eq__(record.id)]),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_by_identifier(self, block_id: uuid.UUID, sensor_identifier: int) -> Optional[SensorRecord]:
        """Find sensor&state in registry by given unique shelly identifier and block unique identifier"""
        items = self.__items.copy()

        return next(
            iter(
                [
                    record
                    for record in items.values()
                    if block_id.__eq__(record.block_id) and record.identifier == sensor_identifier
                ]
            ),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_all_for_block(self, block_id: uuid.UUID) -> List[SensorRecord]:
        """Find sensor&state in registry by block unique identifier"""
        items = self.__items.copy()

        return [record for record in items.values() if block_id.__eq__(record.block_id)]

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        block_id: uuid.UUID,
        sensor_id: uuid.UUID,
        sensor_identifier: int,
        sensor_type: SensorType,
        sensor_description: str,
        sensor_data_type: DataType,
        sensor_unit: Optional[SensorUnit] = None,
        sensor_value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ] = None,
        sensor_value_invalid: Union[str, int, float, bool, None] = None,
        sensor_queryable: bool = False,
        sensor_settable: bool = False,
    ) -> SensorRecord:
        """Append sensor&state record into registry"""
        existing_sensor = self.get_by_id(sensor_id=sensor_id)

        sensor_record: SensorRecord = SensorRecord(
            block_id=block_id,
            sensor_id=sensor_id,
            sensor_identifier=sensor_identifier,
            sensor_type=sensor_type,
            sensor_description=sensor_description,
            sensor_unit=sensor_unit,
            sensor_data_type=sensor_data_type,
            sensor_value_format=sensor_value_format,
            sensor_value_invalid=sensor_value_invalid,
            sensor_queryable=sensor_queryable,
            sensor_settable=sensor_settable,
        )

        if existing_sensor is None:
            try:
                stored_state = self.__channel_property_state_repository.get_by_id(property_id=sensor_id)

                if stored_state is not None:
                    sensor_record.actual_value = stored_state.actual_value
                    sensor_record.expected_value = stored_state.expected_value
                    sensor_record.expected_pending = None

            except (NotImplementedError, AttributeError):
                pass

        self.__items[sensor_record.id.__str__()] = sensor_record

        return sensor_record

    # -----------------------------------------------------------------------------

    def create_or_update(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        block_id: uuid.UUID,
        sensor_id: uuid.UUID,
        sensor_identifier: int,
        sensor_type: SensorType,
        sensor_description: str,
        sensor_data_type: DataType,
        sensor_unit: Optional[SensorUnit] = None,
        sensor_value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ] = None,
        sensor_value_invalid: Union[str, int, float, bool, None] = None,
        sensor_queryable: bool = False,
        sensor_settable: bool = False,
    ) -> SensorRecord:
        """Create or update sensor&state record"""
        sensor_record = self.append(
            block_id=block_id,
            sensor_id=sensor_id,
            sensor_identifier=sensor_identifier,
            sensor_type=sensor_type,
            sensor_description=sensor_description,
            sensor_unit=sensor_unit,
            sensor_data_type=sensor_data_type,
            sensor_value_format=sensor_value_format,
            sensor_value_invalid=sensor_value_invalid,
            sensor_queryable=sensor_queryable,
            sensor_settable=sensor_settable,
        )

        self.__event_dispatcher.dispatch(
            event_id=SensorRecordCreatedOrUpdatedEvent.EVENT_NAME,
            event=SensorRecordCreatedOrUpdatedEvent(record=sensor_record),
        )

        return sensor_record

    # -----------------------------------------------------------------------------

    def remove(self, sensor_id: uuid.UUID) -> None:
        """Remove sensor&state from registry"""
        items = self.__items.copy()

        for record in items.values():
            if sensor_id.__eq__(record.id):
                try:
                    del self.__items[record.id.__str__()]

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self, block_id: Optional[uuid.UUID] = None) -> None:
        """Reset sensors&states registry to initial state"""
        items = self.__items.copy()

        if block_id is not None:
            for record in items.values():
                if block_id.__eq__(record.block_id):
                    self.remove(sensor_id=record.id)

        else:
            self.__items = {}

    # -----------------------------------------------------------------------------

    def set_actual_value(
        self,
        sensor: SensorRecord,
        value: Union[str, int, float, bool, SwitchPayload, None],
    ) -> SensorRecord:
        """Set sensor&state actual value"""
        existing_record = self.get_by_id(sensor_id=sensor.id)

        sensor.actual_value = value
        sensor.actual_value_valid = True

        self.__update(sensor=sensor)

        updated_sensor = self.get_by_id(sensor_id=sensor.id)

        if updated_sensor is None:
            raise InvalidStateException("Sensor&State record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=SensorActualValueEvent.EVENT_NAME,
            event=SensorActualValueEvent(
                original_record=existing_record,
                updated_record=updated_sensor,
            ),
        )

        return updated_sensor

    # -----------------------------------------------------------------------------

    def set_expected_value(
        self,
        sensor: SensorRecord,
        value: Union[str, int, float, bool, ButtonPayload, SwitchPayload, None],
    ) -> SensorRecord:
        """Set sensor&state expected value"""
        existing_record = self.get_by_id(sensor_id=sensor.id)

        sensor.expected_value = value

        self.__update(sensor=sensor)

        updated_sensor = self.get_by_id(sensor.id)

        if updated_sensor is None:
            raise InvalidStateException("Sensor&State record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=SensorActualValueEvent.EVENT_NAME,
            event=SensorActualValueEvent(
                original_record=existing_record,
                updated_record=updated_sensor,
            ),
        )

        return updated_sensor

    # -----------------------------------------------------------------------------

    def set_expected_pending(self, sensor: SensorRecord, timestamp: float) -> SensorRecord:
        """Set sensor&state expected value transmit timestamp"""
        sensor.expected_pending = timestamp

        self.__update(sensor=sensor)

        updated_sensor = self.get_by_id(sensor.id)

        if updated_sensor is None:
            raise InvalidStateException("Sensor&State record could not be re-fetched from registry after update")

        return updated_sensor

    # -----------------------------------------------------------------------------

    def set_valid_state(self, sensor: SensorRecord, state: bool) -> SensorRecord:
        """Set sensor&state actual value reading state"""
        existing_record = self.get_by_id(sensor_id=sensor.id)

        sensor.actual_value_valid = state

        self.__update(sensor=sensor)

        updated_sensor = self.get_by_id(sensor.id)

        if updated_sensor is None:
            raise InvalidStateException("Sensor&State record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=SensorActualValueEvent.EVENT_NAME,
            event=SensorActualValueEvent(
                original_record=existing_record,
                updated_record=updated_sensor,
            ),
        )

        return updated_sensor

    # -----------------------------------------------------------------------------

    def __update(self, sensor: SensorRecord) -> bool:
        items = self.__items.copy()

        for record in items.values():
            if record.id == sensor.id:
                self.__items[sensor.id.__str__()] = sensor

                return True

        return False

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "SensorsRegistry":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.__items.values())

    # -----------------------------------------------------------------------------

    def __next__(self) -> SensorRecord:
        if self.__iterator_index < len(self.__items.values()):
            items: List[SensorRecord] = list(self.__items.values())

            result: SensorRecord = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration


class PropertiesRegistry:
    """
    Properties registry

    @package        FastyBird:ShellyConnector!
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
        property_value: Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None],
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
        property_value: Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None],
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
            event_id=PropertyRecordCreatedOrUpdatedEvent.EVENT_NAME,
            event=PropertyRecordCreatedOrUpdatedEvent(record=property_record),
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
        item: PropertyRecord,
        value: Union[str, bool, None],
    ) -> PropertyRecord:
        """Set property value"""
        existing_record = self.get_by_id(property_id=item.id)

        item.actual_value = value

        self.__update(item=item)

        updated_property = self.get_by_id(property_id=item.id)

        if updated_property is None:
            raise InvalidStateException("Attribute record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=PropertyActualValueEvent.EVENT_NAME,
            event=PropertyActualValueEvent(
                original_record=existing_record,
                updated_record=updated_property,
            ),
        )

        return updated_property

    # -----------------------------------------------------------------------------

    def __update(self, item: PropertyRecord) -> bool:
        items = self.__items.copy()

        for record in items.values():
            if record.id == item.id:
                self.__items[item.id.__str__()] = item

                return True

        return False


class CommandsRegistry:
    """
    Commands registry

    @package        FastyBird:ShellyConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, CommandRecord] = {}

    # -----------------------------------------------------------------------------

    def __init__(self) -> None:
        self.__items = {}

    # -----------------------------------------------------------------------------

    def get_by_command(
        self, device_id: uuid.UUID, client_type: ClientType, command_type: DeviceCommandType
    ) -> Optional[CommandRecord]:
        """Find device command in registry by given unique identifier in given device"""
        items = self.__items.copy()

        return next(
            iter(
                [
                    record
                    for record in items.values()
                    if device_id.__eq__(record.device_id)
                    and record.client_type == client_type
                    and record.command_type == command_type
                ]
            ),
            None,
        )

    # -----------------------------------------------------------------------------

    def create_or_update(
        self, device_id: uuid.UUID, client_type: ClientType, command_type: DeviceCommandType, command_status: bool
    ) -> CommandRecord:
        """Create or update processed command"""
        command_record = CommandRecord(
            device_id=device_id,
            client_type=client_type,
            command_type=command_type,
            command_timestamp=time.time(),
            command_status=command_status,
        )

        self.__items[command_record.__str__()] = command_record

        return command_record

    # -----------------------------------------------------------------------------

    def reset(self, device_id: Optional[uuid.UUID] = None) -> None:
        """Reset devices commands registry to initial state"""
        items = self.__items.copy()

        if device_id is not None:
            for record in items.values():
                if device_id.__eq__(record.device_id):
                    try:
                        del self.__items[record.__str__()]

                    except KeyError:
                        pass

        else:
            self.__items = {}

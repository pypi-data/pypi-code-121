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
FastyBird BUS connector registry module models
"""

# pylint: disable=too-many-lines

# Python base dependencies
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set, Union

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
from fastybird_fb_bus_connector.events.events import (
    AttributeRegisterRecordCreatedOrUpdatedEvent,
    DeviceAttributeRecordCreatedOrUpdatedEvent,
    DeviceAttributeRecordDeletedEvent,
    DeviceRecordCreatedOrUpdatedEvent,
    InputOutputRegisterRecordCreatedOrUpdatedEvent,
    RegisterActualValueEvent,
)
from fastybird_fb_bus_connector.exceptions import InvalidStateException
from fastybird_fb_bus_connector.registry.records import (
    AttributeRegisterRecord,
    DeviceAttributeRecord,
    DeviceRecord,
    DiscoveredAttributeRegisterRecord,
    DiscoveredDeviceRecord,
    DiscoveredInputRegisterRecord,
    DiscoveredOutputRegisterRecord,
    DiscoveredRegisterRecord,
    InputRegisterRecord,
    OutputRegisterRecord,
    RegisterRecord,
)
from fastybird_fb_bus_connector.types import (
    UNASSIGNED_ADDRESS,
    DeviceProperty,
    Packet,
    RegisterType,
)


class DevicesRegistry:  # pylint: disable=too-many-public-methods
    """
    Devices registry

    @package        FastyBird:FbBusConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, DeviceRecord] = {}

    __iterator_index = 0

    __registers_registry: "RegistersRegistry"
    __attributes_registry: "DevicesAttributesRegistry"

    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        registers_registry: "RegistersRegistry",
        attributes_registry: "DevicesAttributesRegistry",
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.__items = {}

        self.__registers_registry = registers_registry
        self.__attributes_registry = attributes_registry

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

    def get_by_address(self, address: int) -> Optional[DeviceRecord]:
        """Find device in registry by given unique address"""
        addresses_attributes = self.__registers_registry.get_all_by_name(name=DeviceProperty.ADDRESS.value)

        for address_attribute in addresses_attributes:
            if address_attribute.actual_value == address:
                return self.get_by_id(device_id=address_attribute.device_id)

        return None

    # -----------------------------------------------------------------------------

    def get_by_serial_number(self, serial_number: str) -> Optional[DeviceRecord]:
        """Find device in registry by given unique serial number"""
        items = self.__items.copy()

        return next(iter([record for record in items.values() if record.serial_number == serial_number]), None)

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        device_id: uuid.UUID,
        device_serial_number: str,
        device_enabled: bool,
    ) -> DeviceRecord:
        """Append new device or update existing device in registry"""
        device: DeviceRecord = DeviceRecord(
            device_id=device_id,
            serial_number=device_serial_number,
            enabled=device_enabled,
        )

        self.__items[device.id.__str__()] = device

        return device

    # -----------------------------------------------------------------------------

    def create_or_update(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: uuid.UUID,
        device_serial_number: str,
        device_enabled: bool,
    ) -> DeviceRecord:
        """Create new device or update existing device in registry"""
        device_record = self.append(
            device_id=device_id,
            device_serial_number=device_serial_number,
            device_enabled=device_enabled,
        )

        self.__event_dispatcher.dispatch(
            event_id=DeviceRecordCreatedOrUpdatedEvent.EVENT_NAME,
            event=DeviceRecordCreatedOrUpdatedEvent(record=device_record),
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

                    self.__registers_registry.reset(device_id=record.id)
                    self.__attributes_registry.reset(device_id=record.id)

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self) -> None:
        """Reset registry to initial state"""
        self.__items = {}

        self.__registers_registry.reset()
        self.__attributes_registry.reset()

    # -----------------------------------------------------------------------------

    def enable(self, device: DeviceRecord) -> DeviceRecord:
        """Enable device for communication"""
        device.enabled = True

        self.__update(updated_device=device)

        updated_device = self.get_by_id(device.id)

        if updated_device is None:
            raise InvalidStateException("Device record could not be re-fetched from registry after update")

        return updated_device

    # -----------------------------------------------------------------------------

    def disable(self, device: DeviceRecord) -> DeviceRecord:
        """Disable device for communication"""
        device.enabled = False

        self.__update(updated_device=device)

        updated_device = self.get_by_id(device.id)

        if updated_device is None:
            raise InvalidStateException("Device record could not be re-fetched from registry after update")

        return updated_device

    # -----------------------------------------------------------------------------

    def set_state(self, device: DeviceRecord, state: ConnectionState) -> DeviceRecord:
        """Set device actual state"""
        actual_state = self.__registers_registry.get_by_name(
            device_id=device.id,
            name=DeviceProperty.STATE.value,
        )

        if actual_state is None:
            raise InvalidStateException(
                "Device state could not be updated. Attribute register was not found in registry",
            )

        if state in (ConnectionState.RUNNING, ConnectionState.UNKNOWN) and actual_state.actual_value != state.value:
            # Reset pointers & counters
            device.lost_timestamp = 0
            device.transmit_attempts = 0
            device.last_writing_packet_timestamp = 0
            device.last_reading_packet_timestamp = 0

        if state == ConnectionState.LOST:
            if actual_state.actual_value != state.value:
                device.lost_timestamp = time.time()

            device.transmit_attempts = 0
            device.last_writing_packet_timestamp = 0
            device.last_reading_packet_timestamp = 0

        self.__registers_registry.set_actual_value(register=actual_state, value=state.value)

        self.__update(updated_device=device)

        updated_device = self.get_by_id(device.id)

        if updated_device is None:
            raise InvalidStateException("Device record could not be re-fetched from registry after update")

        return updated_device

    # -----------------------------------------------------------------------------

    def get_state(self, device: DeviceRecord) -> ConnectionState:
        """Get device actual state"""
        actual_state = self.__registers_registry.get_by_name(
            device_id=device.id,
            name=DeviceProperty.STATE.value,
        )

        if (
            actual_state is None
            or actual_state.actual_value is None
            or not isinstance(actual_state.actual_value, str)
            or not ConnectionState.has_value(actual_state.actual_value)
        ):
            return ConnectionState.UNKNOWN

        return ConnectionState(actual_state.actual_value)

    # -----------------------------------------------------------------------------

    def is_device_running(self, device: DeviceRecord) -> bool:
        """Is device in running state?"""
        return self.get_state(device=device) == ConnectionState.RUNNING

    # -----------------------------------------------------------------------------

    def is_device_unknown(self, device: DeviceRecord) -> bool:
        """Is device in unknown state?"""
        return self.get_state(device=device) == ConnectionState.UNKNOWN

    # -----------------------------------------------------------------------------

    def set_write_packet_timestamp(self, device: DeviceRecord, success: bool = True) -> DeviceRecord:
        """Set packet timestamp for registers writing"""
        device.last_writing_packet_timestamp = time.time()
        device.transmit_attempts = 0 if success else device.transmit_attempts + 1

        self.__update(updated_device=device)

        updated_device = self.get_by_id(device.id)

        if updated_device is None:
            raise InvalidStateException("Device record could not be re-fetched from registry after update")

        return updated_device

    # -----------------------------------------------------------------------------

    def set_read_packet_timestamp(self, device: DeviceRecord, success: bool = True) -> DeviceRecord:
        """Set packet timestamp for registers reading"""
        device.last_reading_packet_timestamp = time.time()
        device.transmit_attempts = 0 if success else device.transmit_attempts + 1

        self.__update(updated_device=device)

        updated_device = self.get_by_id(device.id)

        if updated_device is None:
            raise InvalidStateException("Device record could not be re-fetched from registry after update")

        return updated_device

    # -----------------------------------------------------------------------------

    def set_misc_packet_timestamp(self, device: DeviceRecord, success: bool = True) -> DeviceRecord:
        """Set packet timestamp for misc communication"""
        device.last_misc_packet_timestamp = time.time()
        device.transmit_attempts = 0 if success else device.transmit_attempts + 1

        self.__update(updated_device=device)

        updated_device = self.get_by_id(device.id)

        if updated_device is None:
            raise InvalidStateException("Device record could not be re-fetched from registry after update")

        return updated_device

    # -----------------------------------------------------------------------------

    def get_address(self, device: DeviceRecord) -> Optional[int]:
        """Get device address from registry"""
        actual_address = self.__registers_registry.get_by_name(
            device_id=device.id,
            name=DeviceProperty.ADDRESS.value,
        )

        if actual_address is None or not isinstance(actual_address.actual_value, int):
            return None

        return actual_address.actual_value

    # -----------------------------------------------------------------------------

    def get_max_packet_length_for_device(self, device: DeviceRecord) -> int:
        """Get device max packet length from registry"""
        max_packet_length_attribute = self.__registers_registry.get_by_name(
            device_id=device.id,
            name=DeviceProperty.MAX_PACKET_LENGTH.value,
        )

        if max_packet_length_attribute is None or not isinstance(max_packet_length_attribute.actual_value, int):
            return 80

        return max_packet_length_attribute.actual_value

    # -----------------------------------------------------------------------------

    def find_free_address(self) -> Optional[int]:
        """Find free address for new device"""
        addresses_attributes = self.__registers_registry.get_all_by_name(DeviceProperty.ADDRESS.value)

        reserved_addresses: List[int] = []

        for address_attribute in addresses_attributes:
            if isinstance(address_attribute.actual_value, int):
                reserved_addresses.append(address_attribute.actual_value)

        for address in range(1, 251):
            if address not in reserved_addresses:
                return address

        return None

    # -----------------------------------------------------------------------------

    def __update(self, updated_device: DeviceRecord) -> bool:
        """Update device record"""
        self.__items[updated_device.id.__str__()] = updated_device

        return True

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
class RegistersRegistry:
    """
    Registers registry

    @package        FastyBird:FbBusConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, RegisterRecord] = {}

    __event_dispatcher: EventDispatcher

    __device_property_state_repository: DevicePropertiesStatesRepository
    __channel_property_state_repository: ChannelPropertiesStatesRepository

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        event_dispatcher: EventDispatcher,
        device_property_state_repository: DevicePropertiesStatesRepository,
        channel_property_state_repository: ChannelPropertiesStatesRepository,
    ) -> None:
        self.__items = {}

        self.__event_dispatcher = event_dispatcher

        self.__device_property_state_repository = device_property_state_repository
        self.__channel_property_state_repository = channel_property_state_repository

    # -----------------------------------------------------------------------------

    def get_by_id(self, register_id: uuid.UUID) -> Optional[RegisterRecord]:
        """Get register by identifier"""
        items = self.__items.copy()

        return next(iter([record for record in items.values() if register_id.__eq__(record.id)]), None)

    # -----------------------------------------------------------------------------

    def get_by_address(
        self,
        device_id: uuid.UUID,
        register_type: RegisterType,
        register_address: int,
    ) -> Optional[RegisterRecord]:
        """Get register by its address"""
        items = self.__items.copy()

        return next(
            iter(
                [
                    record
                    for record in items.values()
                    if device_id.__eq__(record.device_id)
                    and record.address == register_address
                    and record.type == register_type
                ]
            ),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_by_name(
        self,
        device_id: uuid.UUID,
        name: str,
    ) -> Optional[AttributeRegisterRecord]:
        """Get device attribute register by name"""
        items = self.__items.copy()

        return next(
            iter(
                [
                    record
                    for record in items.values()
                    if isinstance(record, AttributeRegisterRecord)
                    and record.name == name
                    and device_id.__eq__(record.device_id)
                ]
            ),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_all_by_name(
        self,
        name: str,
    ) -> List[AttributeRegisterRecord]:
        """Get all attributes registers by name"""
        items = self.__items.copy()

        return [
            record for record in items.values() if isinstance(record, AttributeRegisterRecord) and record.name == name
        ]

    # -----------------------------------------------------------------------------

    def get_all_for_device(
        self,
        device_id: uuid.UUID,
        register_type: Union[RegisterType, List[RegisterType], None] = None,
    ) -> List[RegisterRecord]:
        """Get all registers for device by type"""
        items = self.__items.copy()

        return [
            record
            for record in items.values()
            if device_id.__eq__(record.device_id)
            and (
                register_type is None
                or (isinstance(register_type, RegisterType) and record.type == register_type)
                or (isinstance(register_type, list) and record.type in register_type)
            )
        ]

    # -----------------------------------------------------------------------------

    def append_input_register(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
        register_invalid: Union[int, float, str, None] = None,
        channel_id: Optional[uuid.UUID] = None,
    ) -> InputRegisterRecord:
        """Append new register or replace existing register in registry"""
        existing_register = self.get_by_id(register_id=register_id)

        register = InputRegisterRecord(
            device_id=device_id,
            register_id=register_id,
            register_address=register_address,
            register_data_type=register_data_type,
            register_invalid=register_invalid,
            channel_id=channel_id,
        )

        if existing_register is None:
            try:
                stored_state = self.__channel_property_state_repository.get_by_id(property_id=register_id)

                if stored_state is not None:
                    register.actual_value = stored_state.actual_value
                    register.expected_value = stored_state.expected_value
                    register.expected_pending = stored_state.pending

                else:
                    register.actual_value = None
                    register.expected_value = None
                    register.expected_pending = None

            except (NotImplementedError, AttributeError):
                pass

        else:
            register.actual_value = existing_register.actual_value
            register.expected_value = existing_register.expected_value
            register.expected_pending = existing_register.expected_pending

        self.__items[register.id.__str__()] = register

        return register

    # -----------------------------------------------------------------------------

    def append_output_register(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
        register_invalid: Union[int, float, str, None] = None,
        channel_id: Optional[uuid.UUID] = None,
    ) -> OutputRegisterRecord:
        """Append new register or replace existing register in registry"""
        existing_register = self.get_by_id(register_id=register_id)

        register = OutputRegisterRecord(
            device_id=device_id,
            register_id=register_id,
            register_address=register_address,
            register_data_type=register_data_type,
            register_invalid=register_invalid,
            channel_id=channel_id,
        )

        if existing_register is None:
            try:
                stored_state = self.__channel_property_state_repository.get_by_id(property_id=register_id)

                if stored_state is not None:
                    register.actual_value = stored_state.actual_value
                    register.expected_value = stored_state.expected_value
                    register.expected_pending = stored_state.pending

                else:
                    register.actual_value = None
                    register.expected_value = None
                    register.expected_pending = None

            except (NotImplementedError, AttributeError):
                pass

        else:
            register.actual_value = existing_register.actual_value
            register.expected_value = existing_register.expected_value
            register.expected_pending = existing_register.expected_pending

        self.__items[register.id.__str__()] = register

        return register

    # -----------------------------------------------------------------------------

    def append_attribute_register(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
        register_name: Optional[str] = None,
        register_invalid: Union[int, float, str, None] = None,
        register_settable: bool = False,
        register_queryable: bool = False,
        register_value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None] = None,
    ) -> AttributeRegisterRecord:
        """Append new attribute register or replace existing register in registry"""
        existing_register = self.get_by_id(register_id=register_id)

        register = AttributeRegisterRecord(
            device_id=device_id,
            register_id=register_id,
            register_address=register_address,
            register_data_type=register_data_type,
            register_invalid=register_invalid,
            register_name=register_name,
            register_settable=register_settable,
            register_queryable=register_queryable,
        )

        if existing_register is None:
            if register_value is None:
                try:
                    stored_state = self.__device_property_state_repository.get_by_id(property_id=register_id)

                    if stored_state is not None:
                        register.actual_value = stored_state.actual_value
                        register.expected_value = stored_state.expected_value
                        register.expected_pending = stored_state.pending

                    else:
                        register.actual_value = None
                        register.expected_value = None
                        register.expected_pending = None

                except (NotImplementedError, AttributeError):
                    pass

            else:
                register.actual_value = register_value
                register.expected_value = None
                register.expected_pending = None

        else:
            if register_value is None:
                register.actual_value = existing_register.actual_value
                register.expected_value = existing_register.expected_value
                register.expected_pending = existing_register.expected_pending

            else:
                register.actual_value = register_value
                register.expected_value = None
                register.expected_pending = None

        self.__items[register.id.__str__()] = register

        return register

    # -----------------------------------------------------------------------------

    def create_or_update(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_type: RegisterType,
        register_data_type: DataType,
        register_invalid: Union[int, float, str, None] = None,
        register_name: Optional[str] = None,
        register_settable: bool = False,
        register_queryable: bool = False,
        channel_id: Optional[uuid.UUID] = None,
    ) -> RegisterRecord:
        """Create new register or replace existing register in registry"""
        if register_type == RegisterType.INPUT:
            input_register = self.append_input_register(
                device_id=device_id,
                register_id=register_id,
                register_address=register_address,
                register_data_type=register_data_type,
                register_invalid=register_invalid,
                channel_id=channel_id,
            )

            self.__event_dispatcher.dispatch(
                event_id=InputOutputRegisterRecordCreatedOrUpdatedEvent.EVENT_NAME,
                event=InputOutputRegisterRecordCreatedOrUpdatedEvent(record=input_register),
            )

            return input_register

        if register_type == RegisterType.OUTPUT:
            output_register = self.append_output_register(
                device_id=device_id,
                register_id=register_id,
                register_address=register_address,
                register_data_type=register_data_type,
                register_invalid=register_invalid,
                channel_id=channel_id,
            )

            self.__event_dispatcher.dispatch(
                event_id=InputOutputRegisterRecordCreatedOrUpdatedEvent.EVENT_NAME,
                event=InputOutputRegisterRecordCreatedOrUpdatedEvent(record=output_register),
            )

            return output_register

        if register_type == RegisterType.ATTRIBUTE:
            attribute_register = self.append_attribute_register(
                device_id=device_id,
                register_id=register_id,
                register_address=register_address,
                register_data_type=register_data_type,
                register_invalid=register_invalid,
                register_name=register_name,
                register_settable=register_settable,
                register_queryable=register_queryable,
            )

            self.__event_dispatcher.dispatch(
                event_id=AttributeRegisterRecordCreatedOrUpdatedEvent.EVENT_NAME,
                event=AttributeRegisterRecordCreatedOrUpdatedEvent(record=attribute_register),
            )

            return attribute_register

        raise ValueError("Provided register type is not supported")

    # -----------------------------------------------------------------------------

    def remove(self, register_id: uuid.UUID) -> None:
        """Remove register from registry"""
        items = self.__items.copy()

        for record in items.values():
            if register_id.__eq__(record.id):
                try:
                    del self.__items[record.id.__str__()]

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self, device_id: Optional[uuid.UUID] = None, registers_type: Optional[RegisterType] = None) -> None:
        """Reset registry to initial state"""
        items = self.__items.copy()

        if device_id is not None or registers_type is not None:
            for record in items.values():
                if (device_id is None or device_id.__eq__(record.device_id)) and (
                    registers_type is None or record.type == registers_type
                ):
                    self.remove(register_id=record.id)

        else:
            self.__items = {}

    # -----------------------------------------------------------------------------

    def set_actual_value(
        self,
        register: RegisterRecord,
        value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None],
    ) -> RegisterRecord:
        """Set actual value to register"""
        existing_record = self.get_by_id(register_id=register.id)

        register.actual_value = value
        register.actual_value_valid = True

        self.__update(register=register)

        updated_register = self.get_by_id(register.id)

        if updated_register is None:
            raise InvalidStateException("Register record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=RegisterActualValueEvent.EVENT_NAME,
            event=RegisterActualValueEvent(
                original_record=existing_record,
                updated_record=updated_register,
            ),
        )

        return updated_register

    # -----------------------------------------------------------------------------

    def set_expected_value(
        self,
        register: RegisterRecord,
        value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None],
    ) -> RegisterRecord:
        """Set expected value to register"""
        existing_record = self.get_by_id(register_id=register.id)

        register.expected_value = value

        self.__update(register=register)

        updated_register = self.get_by_id(register.id)

        if updated_register is None:
            raise InvalidStateException("Register record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=RegisterActualValueEvent.EVENT_NAME,
            event=RegisterActualValueEvent(
                original_record=existing_record,
                updated_record=updated_register,
            ),
        )

        return updated_register

    # -----------------------------------------------------------------------------

    def set_expected_pending(self, register: RegisterRecord, timestamp: float) -> RegisterRecord:
        """Set expected value transmit timestamp"""
        existing_record = self.get_by_id(register_id=register.id)

        register.expected_pending = timestamp

        self.__update(register=register)

        updated_register = self.get_by_id(register.id)

        if updated_register is None:
            raise InvalidStateException("Register record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=RegisterActualValueEvent.EVENT_NAME,
            event=RegisterActualValueEvent(
                original_record=existing_record,
                updated_record=updated_register,
            ),
        )

        return updated_register

    # -----------------------------------------------------------------------------

    def set_valid_state(self, register: RegisterRecord, state: bool) -> RegisterRecord:
        """Set register actual value reading state"""
        existing_record = self.get_by_id(register_id=register.id)

        register.actual_value_valid = state

        self.__update(register=register)

        updated_register = self.get_by_id(register.id)

        if updated_register is None:
            raise InvalidStateException("Register record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=RegisterActualValueEvent.EVENT_NAME,
            event=RegisterActualValueEvent(
                original_record=existing_record,
                updated_record=updated_register,
            ),
        )

        return updated_register

    # -----------------------------------------------------------------------------

    def __update(self, register: RegisterRecord) -> bool:
        items = self.__items.copy()

        for record in items.values():
            if record.id == register.id:
                self.__items[register.id.__str__()] = register

                return True

        return False


@inject
class DevicesAttributesRegistry:
    """
    Devices attributes registry

    @package        FastyBird:FbBusConnector!
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


class DiscoveredDevicesRegistry:
    """
    Discovered devices registry

    @package        FastyBird:FbBusConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Set[DiscoveredDeviceRecord]

    __registers_registry: "DiscoveredRegistersRegistry"
    __devices_registry: DevicesRegistry

    __logger: Union[logging.Logger, logging.Logger]

    __iterator_index = 0

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        registers_registry: "DiscoveredRegistersRegistry",
        devices_registry: DevicesRegistry,
        logger: Union[logging.Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__items = set()

        self.__registers_registry = registers_registry
        self.__devices_registry = devices_registry

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def get_by_address(self, address: int) -> Optional[DiscoveredDeviceRecord]:
        """Find device in registry by given unique address"""
        items = self.__items.copy()

        return next(
            iter([record for record in items if record.address == address]),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_by_serial_number(self, serial_number: str) -> Optional[DiscoveredDeviceRecord]:
        """Find device in registry by given unique serial_number"""
        items = self.__items.copy()

        return next(
            iter([record for record in items if record.serial_number == serial_number]),
            None,
        )

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_address: int,
        device_max_packet_length: int,
        device_serial_number: str,
        device_state: ConnectionState,
        device_hardware_version: str,
        device_hardware_model: str,
        device_hardware_manufacturer: str,
        device_firmware_version: str,
        device_firmware_manufacturer: str,
        input_registers_size: int,
        output_registers_size: int,
        attributes_registers_size: int,
    ) -> None:
        """Append discovered device data"""
        discovered_device = DiscoveredDeviceRecord(
            device_address=device_address,
            device_max_packet_length=device_max_packet_length,
            device_serial_number=device_serial_number,
            device_state=device_state,
            device_hardware_version=device_hardware_version,
            device_hardware_model=device_hardware_model,
            device_hardware_manufacturer=device_hardware_manufacturer,
            device_firmware_version=device_firmware_version,
            device_firmware_manufacturer=device_firmware_manufacturer,
            input_registers_size=input_registers_size,
            output_registers_size=output_registers_size,
            attributes_registers_size=attributes_registers_size,
        )

        if discovered_device in self.__items:
            return

        self.__items.add(discovered_device)

        self.__logger.info(
            "Discovered device %s[%d] %s[%s]:%s",
            device_serial_number,
            device_address,
            device_hardware_version,
            device_hardware_model,
            device_firmware_version,
        )

    # -----------------------------------------------------------------------------

    def reset(self) -> None:
        """Reset registry to initial state"""
        self.__items = set()

        self.__registers_registry.reset()

    # -----------------------------------------------------------------------------

    def remove(self, serial_number: str) -> None:
        """Remove device from registry"""
        items = self.__items.copy()

        for record in items:
            if record.serial_number == serial_number:
                try:
                    self.__items.remove(record)

                    self.__registers_registry.reset(device_serial_number=record.serial_number)

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def set_waiting_for_packet(
        self,
        device: DiscoveredDeviceRecord,
        packet_type: Optional[Packet],
    ) -> DiscoveredDeviceRecord:
        """Mark that gateway is waiting for reply from device"""
        device.waiting_for_packet = packet_type

        self.__update(updated_device=device)

        updated_device = self.get_by_serial_number(device.serial_number)

        if updated_device is None:
            raise InvalidStateException("Device record could not be re-fetched from registry after update")

        return updated_device

    # -----------------------------------------------------------------------------

    def prepare_devices(self) -> None:
        """Prepare discovered devices"""
        for discovered_device in self.__items:
            # Try to find device in registry
            existing_device = self.__devices_registry.get_by_serial_number(
                serial_number=discovered_device.serial_number,
            )

            # Discovering new device...
            if existing_device is None:
                # Check if device has address or not
                if discovered_device.address != UNASSIGNED_ADDRESS:
                    # Check if other device with same address is present in registry
                    device_by_address = self.__devices_registry.get_by_address(address=discovered_device.address)

                    if device_by_address is not None:
                        self.__logger.warning(
                            "Address used by discovered device is assigned to other registered device",
                            extra={
                                "device": {
                                    "serial_number": discovered_device.serial_number,
                                    "address": discovered_device.address,
                                },
                            },
                        )

                        return

                self.__logger.info(
                    "New device: %s with address: %d was successfully prepared for registering",
                    discovered_device.serial_number,
                    discovered_device.address,
                    extra={
                        "device": {
                            "serial_number": discovered_device.serial_number,
                            "address": discovered_device.address,
                        },
                    },
                )

            # Discovering existing device...
            else:
                # Check if other device with same address is present in registry
                device_by_address = self.__devices_registry.get_by_address(address=discovered_device.address)

                if device_by_address is not None and device_by_address.serial_number != discovered_device.serial_number:
                    self.__logger.warning(
                        "Address used by discovered device is assigned to other registered device",
                        extra={
                            "device": {
                                "serial_number": discovered_device.serial_number,
                                "address": discovered_device.address,
                            },
                        },
                    )

                    return

                self.__logger.info(
                    "Existing device: %s with address: %d was successfully prepared for updating",
                    discovered_device.serial_number,
                    discovered_device.address,
                    extra={
                        "device": {
                            "serial_number": discovered_device.serial_number,
                            "address": discovered_device.address,
                        },
                    },
                )

                # Update device state
                self.__devices_registry.set_state(device=existing_device, state=ConnectionState.INIT)

            # Input registers
            self.__configure_device_registers(
                discovered_device=discovered_device,
                registers_type=RegisterType.INPUT,
            )

            # Output registers
            self.__configure_device_registers(
                discovered_device=discovered_device,
                registers_type=RegisterType.OUTPUT,
            )

            # Attribute registers
            self.__configure_device_registers(
                discovered_device=discovered_device,
                registers_type=RegisterType.ATTRIBUTE,
            )

            self.__logger.info(
                "Configured registers: (Input: %d, Output: %d, Attribute: %d) for device: %s",
                discovered_device.input_registers_size,
                discovered_device.output_registers_size,
                discovered_device.attributes_registers_size,
                discovered_device.serial_number,
                extra={
                    "device": {
                        "serial_number": discovered_device.serial_number,
                        "address": discovered_device.address,
                    },
                },
            )

    # -----------------------------------------------------------------------------

    def __update(self, updated_device: DiscoveredDeviceRecord) -> bool:
        """Update device record"""
        self.__items.remove(updated_device)
        self.__items.add(updated_device)

        return True

    # -----------------------------------------------------------------------------

    def __configure_device_registers(
        self,
        discovered_device: DiscoveredDeviceRecord,
        registers_type: RegisterType,
    ) -> None:
        """Prepare discovered device registers"""
        if registers_type == RegisterType.INPUT:
            registers_size = discovered_device.input_registers_size

        elif registers_type == RegisterType.OUTPUT:
            registers_size = discovered_device.output_registers_size

        elif registers_type == RegisterType.ATTRIBUTE:
            registers_size = discovered_device.attributes_registers_size

        else:
            return

        # Register data type will be reset to unknown
        register_data_type = DataType.UNKNOWN

        for i in range(registers_size):
            if registers_type == RegisterType.INPUT:
                # Create register record in registry
                self.__registers_registry.create_input_register(
                    device_serial_number=discovered_device.serial_number,
                    device_address=discovered_device.address,
                    register_address=i,
                    register_data_type=register_data_type,
                )

            elif registers_type == RegisterType.OUTPUT:
                # Create register record in registry
                self.__registers_registry.create_output_register(
                    device_serial_number=discovered_device.serial_number,
                    device_address=discovered_device.address,
                    register_address=i,
                    register_data_type=register_data_type,
                )

            elif registers_type == RegisterType.ATTRIBUTE:
                # Create register record in registry
                self.__registers_registry.create_attribute_register(
                    device_serial_number=discovered_device.serial_number,
                    device_address=discovered_device.address,
                    register_address=i,
                    register_data_type=register_data_type,
                    register_name=None,
                    register_settable=False,
                    register_queryable=False,
                )

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "DiscoveredDevicesRegistry":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.__items)

    # -----------------------------------------------------------------------------

    def __next__(self) -> DiscoveredDeviceRecord:
        if self.__iterator_index < len(self.__items):
            items: List[DiscoveredDeviceRecord] = list(self.__items)

            result: DiscoveredDeviceRecord = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration


class DiscoveredRegistersRegistry:
    """
    Discovered devices registers registry

    @package        FastyBird:FbBusConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Set[DiscoveredRegisterRecord]

    __logger: Union[logging.Logger, logging.Logger]

    # -----------------------------------------------------------------------------

    def __init__(self, logger: Union[logging.Logger, logging.Logger] = logging.getLogger("dummy")) -> None:
        self.__items = set()

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def get_all_by_device(
        self,
        device_serial_number: str,
    ) -> List[DiscoveredRegisterRecord]:
        """Get all registers by device serial number"""
        items = self.__items.copy()

        return [record for record in items if record.device_serial_number == device_serial_number]

    # -----------------------------------------------------------------------------

    def append_input_register(
        self,
        device_serial_number: str,
        device_address: int,
        register_address: int,
        register_data_type: DataType,
    ) -> None:
        """Append discovered device register"""
        configured_register = DiscoveredInputRegisterRecord(
            device_serial_number=device_serial_number,
            device_address=device_address,
            register_address=register_address,
            register_data_type=register_data_type,
        )

        if configured_register not in self.__items:
            self.__logger.warning(
                "Register: %d[%d] for device: %s could not be found in registry",
                register_address,
                RegisterType.INPUT.value,
                device_serial_number,
                extra={
                    "device": {
                        "serial_number": device_serial_number,
                        "address": device_address,
                    },
                },
            )

            return

        self.__items.remove(configured_register)
        self.__items.add(configured_register)

        self.__logger.info(
            "Configured register: %d[%d] for device: %s",
            register_address,
            RegisterType.INPUT.value,
            device_serial_number,
            extra={
                "device": {
                    "serial_number": device_serial_number,
                    "address": device_address,
                },
            },
        )

    # -----------------------------------------------------------------------------

    def append_output_register(
        self,
        device_serial_number: str,
        device_address: int,
        register_address: int,
        register_data_type: DataType,
    ) -> None:
        """Append discovered device output register"""
        configured_register = DiscoveredOutputRegisterRecord(
            device_serial_number=device_serial_number,
            device_address=device_address,
            register_address=register_address,
            register_data_type=register_data_type,
        )

        if configured_register not in self.__items:
            self.__logger.warning(
                "Register: %d[%d] for device: %s could not be found in registry",
                register_address,
                RegisterType.OUTPUT.value,
                device_serial_number,
                extra={
                    "device": {
                        "serial_number": device_serial_number,
                        "address": device_address,
                    },
                },
            )

            return

        self.__items.remove(configured_register)
        self.__items.add(configured_register)

        self.__logger.info(
            "Configured register: %d[%d] for device: %s",
            register_address,
            RegisterType.OUTPUT.value,
            device_serial_number,
            extra={
                "device": {
                    "serial_number": device_serial_number,
                    "address": device_address,
                },
            },
        )

    # -----------------------------------------------------------------------------

    def append_attribute_register(  # pylint: disable=too-many-arguments
        self,
        device_serial_number: str,
        device_address: int,
        register_address: int,
        register_name: Optional[str],
        register_data_type: DataType,
        register_settable: bool,
        register_queryable: bool,
    ) -> None:
        """Append discovered device attribute"""
        configured_register = DiscoveredAttributeRegisterRecord(
            device_serial_number=device_serial_number,
            device_address=device_address,
            register_address=register_address,
            register_name=register_name,
            register_data_type=register_data_type,
            register_settable=register_settable,
            register_queryable=register_queryable,
        )

        if configured_register not in self.__items:
            self.__logger.warning(
                "Register: %d[%d] for device: %s could not be found in registry",
                register_address,
                RegisterType.ATTRIBUTE.value,
                device_serial_number,
                extra={
                    "device": {
                        "serial_number": device_serial_number,
                        "address": device_address,
                    },
                },
            )

            return

        self.__items.remove(configured_register)
        self.__items.add(configured_register)

        self.__logger.info(
            "Configured register: %d[%d] for device: %s",
            register_address,
            RegisterType.ATTRIBUTE.value,
            device_serial_number,
            extra={
                "device": {
                    "serial_number": device_serial_number,
                    "address": device_address,
                },
            },
        )

    # -----------------------------------------------------------------------------

    def create_input_register(  # pylint: disable=too-many-arguments
        self,
        device_serial_number: str,
        device_address: int,
        register_address: int,
        register_data_type: DataType,
    ) -> None:
        """Create discovered device register"""
        self.__items.add(
            DiscoveredInputRegisterRecord(
                device_address=device_address,
                device_serial_number=device_serial_number,
                register_address=register_address,
                register_data_type=register_data_type,
            )
        )

    # -----------------------------------------------------------------------------

    def create_output_register(  # pylint: disable=too-many-arguments
        self,
        device_serial_number: str,
        device_address: int,
        register_address: int,
        register_data_type: DataType,
    ) -> None:
        """Create discovered device register"""
        self.__items.add(
            DiscoveredOutputRegisterRecord(
                device_address=device_address,
                device_serial_number=device_serial_number,
                register_address=register_address,
                register_data_type=register_data_type,
            )
        )

    # -----------------------------------------------------------------------------

    def create_attribute_register(  # pylint: disable=too-many-arguments
        self,
        device_serial_number: str,
        device_address: int,
        register_address: int,
        register_name: Optional[str],
        register_data_type: DataType,
        register_settable: bool,
        register_queryable: bool,
    ) -> None:
        """Create discovered device register"""
        self.__items.add(
            DiscoveredAttributeRegisterRecord(
                device_address=device_address,
                device_serial_number=device_serial_number,
                register_address=register_address,
                register_name=register_name,
                register_data_type=register_data_type,
                register_settable=register_settable,
                register_queryable=register_queryable,
            )
        )

    # -----------------------------------------------------------------------------

    def reset(self, device_serial_number: Optional[str] = None) -> None:
        """Reset registry to initial state"""
        items = self.__items.copy()

        if device_serial_number is not None:
            for register in items:
                if register.device_serial_number == device_serial_number:
                    self.__items.remove(register)

        else:
            self.__items = set()

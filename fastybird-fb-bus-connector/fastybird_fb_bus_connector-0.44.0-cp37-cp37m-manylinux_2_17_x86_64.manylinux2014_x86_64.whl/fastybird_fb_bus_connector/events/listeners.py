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
FastyBird BUS connector events module listeners
"""

# Python base dependencies
import logging
import uuid
from datetime import datetime
from typing import Dict, Union

# Library dependencies
from fastybird_devices_module.entities.channel import ChannelDynamicPropertyEntity
from fastybird_devices_module.entities.device import (
    DeviceDynamicPropertyEntity,
    DeviceStaticPropertyEntity,
)
from fastybird_devices_module.managers.channel import (
    ChannelPropertiesManager,
    ChannelsManager,
)
from fastybird_devices_module.managers.device import (
    DeviceAttributesManager,
    DevicePropertiesManager,
    DevicesManager,
)
from fastybird_devices_module.managers.state import (
    ChannelPropertiesStatesManager,
    DevicePropertiesStatesManager,
)
from fastybird_devices_module.repositories.channel import (
    ChannelPropertiesRepository,
    ChannelsRepository,
)
from fastybird_devices_module.repositories.device import (
    DeviceAttributesRepository,
    DevicePropertiesRepository,
    DevicesRepository,
)
from fastybird_devices_module.repositories.state import (
    ChannelPropertiesStatesRepository,
    DevicePropertiesStatesRepository,
)
from fastybird_devices_module.utils import normalize_value
from fastybird_metadata.types import ButtonPayload, SwitchPayload
from kink import inject
from whistle import Event, EventDispatcher

# Library libs
from fastybird_fb_bus_connector.entities import FbBusDeviceEntity
from fastybird_fb_bus_connector.events.events import (
    AttributeRegisterRecordCreatedOrUpdatedEvent,
    DeviceAttributeRecordCreatedOrUpdatedEvent,
    DeviceAttributeRecordDeletedEvent,
    DeviceRecordCreatedOrUpdatedEvent,
    InputOutputRegisterRecordCreatedOrUpdatedEvent,
    RegisterActualValueEvent,
)
from fastybird_fb_bus_connector.logger import Logger
from fastybird_fb_bus_connector.registry.model import RegistersRegistry
from fastybird_fb_bus_connector.registry.records import (
    AttributeRegisterRecord,
    InputRegisterRecord,
    OutputRegisterRecord,
)
from fastybird_fb_bus_connector.types import DeviceProperty, RegisterName, RegisterType


@inject
class EventsListener:  # pylint: disable=too-many-instance-attributes
    """
    Events listener

    @package        FastyBird:FbBusConnector!
    @module         events/listeners

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __connector_id: uuid.UUID

    __registers_registry: RegistersRegistry

    __devices_repository: DevicesRepository
    __devices_manager: DevicesManager

    __devices_properties_repository: DevicePropertiesRepository
    __devices_properties_manager: DevicePropertiesManager
    __devices_properties_states_repository: DevicePropertiesStatesRepository
    __devices_properties_states_manager: DevicePropertiesStatesManager

    __devices_attributes_repository: DeviceAttributesRepository
    __devices_attributes_manager: DeviceAttributesManager

    __channels_repository: ChannelsRepository
    __channels_manager: ChannelsManager

    __channels_properties_repository: ChannelPropertiesRepository
    __channels_properties_manager: ChannelPropertiesManager
    __channels_properties_states_repository: ChannelPropertiesStatesRepository
    __channels_properties_states_manager: ChannelPropertiesStatesManager

    __event_dispatcher: EventDispatcher

    __logger: Union[Logger, logging.Logger]

    __UPDATE_ALL_EVENTS: bool = True

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        connector_id: uuid.UUID,
        registers_registry: RegistersRegistry,
        devices_repository: DevicesRepository,
        devices_manager: DevicesManager,
        devices_properties_repository: DevicePropertiesRepository,
        devices_properties_manager: DevicePropertiesManager,
        devices_properties_states_repository: DevicePropertiesStatesRepository,
        devices_properties_states_manager: DevicePropertiesStatesManager,
        devices_attributes_repository: DeviceAttributesRepository,
        devices_attributes_manager: DeviceAttributesManager,
        channels_repository: ChannelsRepository,
        channels_manager: ChannelsManager,
        channels_properties_repository: ChannelPropertiesRepository,
        channels_properties_manager: ChannelPropertiesManager,
        event_dispatcher: EventDispatcher,
        channels_properties_states_manager: ChannelPropertiesStatesManager,
        channels_properties_states_repository: ChannelPropertiesStatesRepository,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__connector_id = connector_id

        self.__registers_registry = registers_registry

        self.__devices_repository = devices_repository
        self.__devices_manager = devices_manager

        self.__devices_properties_repository = devices_properties_repository
        self.__devices_properties_manager = devices_properties_manager
        self.__devices_properties_states_repository = devices_properties_states_repository
        self.__devices_properties_states_manager = devices_properties_states_manager

        self.__devices_attributes_repository = devices_attributes_repository
        self.__devices_attributes_manager = devices_attributes_manager

        self.__channels_repository = channels_repository
        self.__channels_manager = channels_manager

        self.__channels_properties_repository = channels_properties_repository
        self.__channels_properties_manager = channels_properties_manager
        self.__channels_properties_states_repository = channels_properties_states_repository
        self.__channels_properties_states_manager = channels_properties_states_manager

        self.__event_dispatcher = event_dispatcher

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def open(self) -> None:
        """Open all listeners callbacks"""
        self.__event_dispatcher.add_listener(
            event_id=DeviceRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_device,
        )

        self.__event_dispatcher.add_listener(
            event_id=InputOutputRegisterRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_io_register,
        )

        self.__event_dispatcher.add_listener(
            event_id=AttributeRegisterRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_attribute_register,
        )

        self.__event_dispatcher.add_listener(
            event_id=DeviceAttributeRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_device_attribute,
        )

        self.__event_dispatcher.add_listener(
            event_id=DeviceAttributeRecordDeletedEvent.EVENT_NAME,
            listener=self.__handle_delete_device_attribute,
        )

        self.__event_dispatcher.add_listener(
            event_id=RegisterActualValueEvent.EVENT_NAME,
            listener=self.__handle_write_register_actual_value,
        )

    # -----------------------------------------------------------------------------

    def close(self) -> None:
        """Close all listeners registrations"""
        self.__event_dispatcher.remove_listener(
            event_id=DeviceRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_device,
        )

        self.__event_dispatcher.remove_listener(
            event_id=InputOutputRegisterRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_io_register,
        )

        self.__event_dispatcher.remove_listener(
            event_id=AttributeRegisterRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_attribute_register,
        )

        self.__event_dispatcher.remove_listener(
            event_id=DeviceAttributeRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_device_attribute,
        )

        self.__event_dispatcher.remove_listener(
            event_id=DeviceAttributeRecordDeletedEvent.EVENT_NAME,
            listener=self.__handle_delete_device_attribute,
        )

        self.__event_dispatcher.remove_listener(
            event_id=RegisterActualValueEvent.EVENT_NAME,
            listener=self.__handle_write_register_actual_value,
        )

    # -----------------------------------------------------------------------------

    def __handle_create_or_update_device(self, event: Event) -> None:
        if not isinstance(event, DeviceRecordCreatedOrUpdatedEvent):
            return

        device_data = {
            "id": event.record.id,
            "identifier": event.record.serial_number,
        }

        device = self.__devices_repository.get_by_id(device_id=event.record.id)

        if device is None:
            # Define relation between device and it's connector
            device_data["connector_id"] = self.__connector_id

            device = self.__devices_manager.create(
                data=device_data,
                device_type=FbBusDeviceEntity,  # type: ignore[misc]
            )

            self.__logger.debug(
                "Creating new device",
                extra={
                    "device": {
                        "id": device.id.__str__(),
                    },
                },
            )

        else:
            device = self.__devices_manager.update(data=device_data, device=device)

            self.__logger.debug(
                "Updating existing device",
                extra={
                    "device": {
                        "id": device.id.__str__(),
                    },
                },
            )

    # -----------------------------------------------------------------------------

    def __handle_create_or_update_io_register(self, event: Event) -> None:
        if not isinstance(event, InputOutputRegisterRecordCreatedOrUpdatedEvent):
            return

        if isinstance(event.record, InputRegisterRecord):
            channel_identifier = f"{RegisterName.INPUT.value}_{(event.record.address + 1):02}"

        elif isinstance(event.record, OutputRegisterRecord):
            channel_identifier = f"{RegisterName.OUTPUT.value}_{(event.record.address + 1):02}"

        else:
            return

        channel = self.__channels_repository.get_by_identifier(
            device_id=event.record.device_id,
            channel_identifier=channel_identifier,
        )

        if channel is None:
            channel_data = {
                "device_id": event.record.device_id,
                "identifier": channel_identifier,
            }

            channel = self.__channels_manager.create(data=channel_data)

            self.__logger.debug(
                "Creating new IO channel",
                extra={
                    "device": {
                        "id": channel.device.id.__str__(),
                    },
                    "channel": {
                        "id": channel.id.__str__(),
                    },
                },
            )

        property_data = {
            "id": event.record.id,
            "identifier": f"register_{event.record.address:02}",
            "data_type": event.record.data_type,
            "format": event.record.format,
            "unit": None,
            "invalid": None,
            "queryable": event.record.queryable,
            "settable": event.record.settable,
        }

        channel_property = self.__channels_properties_repository.get_by_identifier(
            channel_id=channel.id,
            property_identifier=str(property_data["identifier"]),
        )

        if channel_property is None:
            # Define relation between channel & property
            property_data["channel_id"] = channel.id

            channel_property = self.__channels_properties_manager.create(
                data=property_data,
                property_type=ChannelDynamicPropertyEntity,
            )

            self.__logger.debug(
                "Creating new channel property with state info",
                extra={
                    "device": {
                        "id": channel_property.channel.device.id.__str__(),
                    },
                    "channel": {
                        "id": channel_property.channel.id.__str__(),
                    },
                    "property": {
                        "id": channel_property.id.__str__(),
                    },
                },
            )

        else:
            channel_property = self.__channels_properties_manager.update(
                data=property_data,
                channel_property=channel_property,
            )

            self.__logger.debug(
                "Updating existing channel property with state info",
                extra={
                    "device": {
                        "id": channel_property.channel.device.id.__str__(),
                    },
                    "channel": {
                        "id": channel_property.channel.id.__str__(),
                    },
                    "property": {
                        "id": channel_property.id.__str__(),
                    },
                },
            )

        # Add newly created channel identifier to register
        if event.record.type.__eq__(RegisterType.OUTPUT):
            self.__registers_registry.append_output_register(
                device_id=event.record.device_id,
                register_id=event.record.id,
                register_address=event.record.address,
                register_data_type=event.record.data_type,
                channel_id=channel.id,
            )

        if event.record.type.__eq__(RegisterType.INPUT):
            self.__registers_registry.append_input_register(
                device_id=event.record.device_id,
                register_id=event.record.id,
                register_address=event.record.address,
                register_data_type=event.record.data_type,
                channel_id=channel.id,
            )

        # Store value for dynamic registers
        self.__write_channel_property_actual_value(register=event.record)

    # -----------------------------------------------------------------------------

    def __handle_create_or_update_attribute_register(self, event: Event) -> None:
        if not isinstance(event, AttributeRegisterRecordCreatedOrUpdatedEvent) or event.record.name is None:
            return

        if event.record.name is not None and event.record.name in [
            DeviceProperty.ADDRESS.value,
            DeviceProperty.MAX_PACKET_LENGTH.value,
        ]:
            property_data = {
                "id": event.record.id,
                "identifier": f"{event.record.name}_{event.record.address:02}",
                "name": event.record.name,
                "data_type": event.record.data_type,
                "format": event.record.format,
                "unit": None,
                "invalid": None,
                "queryable": False,
                "settable": False,
                "value": event.record.actual_value,
            }

        else:
            property_data = {
                "id": event.record.id,
                "identifier": f"{event.record.name}_{event.record.address:02}",
                "name": event.record.name,
                "data_type": event.record.data_type,
                "format": event.record.format,
                "unit": None,
                "invalid": None,
                "queryable": event.record.queryable,
                "settable": event.record.settable,
            }

        device_property = self.__devices_properties_repository.get_by_id(property_id=event.record.id)

        if device_property is None:
            # Define relation between channel & property
            property_data["device_id"] = event.record.device_id

            # Special mapping for known attributes
            if event.record.name is not None and event.record.name in [
                DeviceProperty.ADDRESS.value,
                DeviceProperty.MAX_PACKET_LENGTH.value,
            ]:
                device_property = self.__devices_properties_manager.create(
                    data=property_data,
                    property_type=DeviceStaticPropertyEntity,
                )

            else:
                device_property = self.__devices_properties_manager.create(
                    data=property_data,
                    property_type=DeviceDynamicPropertyEntity,
                )

            self.__logger.debug(
                "Creating new device property",
                extra={
                    "device": {
                        "id": device_property.device.id.__str__(),
                    },
                    "property": {
                        "id": device_property.id.__str__(),
                    },
                },
            )

        else:
            device_property = self.__devices_properties_manager.update(
                data=property_data,
                device_property=device_property,
            )

            self.__logger.debug(
                "Updating existing device property",
                extra={
                    "device": {
                        "id": device_property.device.id.__str__(),
                    },
                    "property": {
                        "id": device_property.id.__str__(),
                    },
                },
            )

        if isinstance(device_property, DeviceDynamicPropertyEntity):
            # Store value for dynamic registers
            self.__write_device_property_value(register=event.record)

    # -----------------------------------------------------------------------------

    def __handle_create_or_update_device_attribute(self, event: Event) -> None:
        if not isinstance(event, DeviceAttributeRecordCreatedOrUpdatedEvent):
            return

        attribute_data = {
            "id": event.record.id,
            "identifier": event.record.identifier,
            "name": event.record.name,
            "content": event.record.value,
        }

        device_attribute = self.__devices_attributes_repository.get_by_id(attribute_id=event.record.id)

        if device_attribute is None:
            # Define relation between channel and it's device
            attribute_data["device_id"] = event.record.device_id

            device_attribute = self.__devices_attributes_manager.create(data=attribute_data)

            self.__logger.debug(
                "Creating new device attribute",
                extra={
                    "device": {
                        "id": device_attribute.device.id.__str__(),
                    },
                    "attribute": {
                        "id": device_attribute.id.__str__(),
                    },
                },
            )

        else:
            device_attribute = self.__devices_attributes_manager.update(
                data=attribute_data,
                device_attribute=device_attribute,
            )

            self.__logger.debug(
                "Updating existing device attribute",
                extra={
                    "device": {
                        "id": device_attribute.device.id.__str__(),
                    },
                    "attribute": {
                        "id": device_attribute.id.__str__(),
                    },
                },
            )

    # -----------------------------------------------------------------------------

    def __handle_delete_device_attribute(self, event: Event) -> None:
        if not isinstance(event, DeviceAttributeRecordDeletedEvent):
            return

        device_attribute = self.__devices_attributes_repository.get_by_id(attribute_id=event.record.id)

        if device_attribute is not None:
            self.__devices_attributes_manager.delete(device_attribute=device_attribute)

            self.__logger.debug(
                "Removing existing device attribute",
                extra={
                    "device": {
                        "id": device_attribute.device.id.__str__(),
                    },
                    "attribute": {
                        "id": device_attribute.id.__str__(),
                    },
                },
            )

    # -----------------------------------------------------------------------------

    def __handle_write_register_actual_value(self, event: Event) -> None:
        if not isinstance(event, RegisterActualValueEvent):
            return

        register = event.updated_record

        if isinstance(register, (InputRegisterRecord, OutputRegisterRecord)):
            self.__write_channel_property_actual_value(register=register)

        if isinstance(register, AttributeRegisterRecord):
            self.__write_device_property_value(register=register)

    # -----------------------------------------------------------------------------

    def __write_channel_property_actual_value(
        self,
        register: Union[InputRegisterRecord, OutputRegisterRecord],
    ) -> None:
        channel_property = self.__channels_properties_repository.get_by_id(property_id=register.id)

        if channel_property is not None:
            actual_value = (
                register.actual_value
                if isinstance(register.actual_value, (str, int, float, bool)) or register.actual_value is None
                else str(register.actual_value)
            )
            expected_value = (
                register.expected_value
                if isinstance(register.expected_value, (str, int, float, bool)) or register.expected_value is None
                else str(register.expected_value)
            )

            state_data = {
                "actual_value": register.actual_value,
                "expected_value": register.expected_value,
                "pending": actual_value != expected_value and expected_value is not None,
                "valid": register.actual_value_valid,
            }

            try:
                property_state = self.__channels_properties_states_repository.get_by_id(property_id=channel_property.id)

            except (NotImplementedError, AttributeError):
                self.__logger.warning("States repository is not configured. State could not be fetched")

                return

            if property_state is None:
                try:
                    property_state = self.__channels_properties_states_manager.create(
                        channel_property=channel_property,
                        data=state_data,
                    )

                except NotImplementedError:
                    self.__logger.warning("States manager is not configured. State could not be saved")

                    return

                self.__logger.debug(
                    "Creating new channel property state",
                    extra={
                        "device": {
                            "id": channel_property.channel.device.id.__str__(),
                        },
                        "channel": {
                            "id": channel_property.channel.id.__str__(),
                        },
                        "property": {
                            "id": channel_property.id.__str__(),
                        },
                        "state": {
                            "id": property_state.id.__str__(),
                            "actual_value": property_state.actual_value,
                            "expected_value": property_state.expected_value,
                            "pending": property_state.pending,
                            "valid": property_state.valid,
                        },
                    },
                )

            else:
                stored_value = normalize_value(
                    data_type=channel_property.data_type,
                    value=property_state.actual_value,
                    value_format=channel_property.format,
                    value_invalid=channel_property.invalid,
                )

                if self.__UPDATE_ALL_EVENTS or stored_value != register.actual_value:
                    try:
                        property_state = self.__channels_properties_states_manager.update(
                            channel_property=channel_property,
                            state=property_state,
                            data=state_data,
                        )

                    except NotImplementedError:
                        self.__logger.warning("States manager is not configured. State could not be saved")

                        return

                    self.__logger.debug(
                        "Updating existing channel property state",
                        extra={
                            "device": {
                                "id": channel_property.channel.device.id.__str__(),
                            },
                            "channel": {
                                "id": channel_property.channel.id.__str__(),
                            },
                            "property": {
                                "id": channel_property.id.__str__(),
                            },
                            "state": {
                                "id": property_state.id.__str__(),
                                "actual_value": property_state.actual_value,
                                "expected_value": property_state.expected_value,
                                "pending": property_state.pending,
                                "valid": property_state.valid,
                            },
                        },
                    )

    # -----------------------------------------------------------------------------

    def __write_device_property_value(self, register: AttributeRegisterRecord) -> None:
        device_property = self.__devices_properties_repository.get_by_id(property_id=register.id)

        if device_property is None:
            self.__logger.warning(
                "Device property couldn't be found in database",
                extra={
                    "device": {"id": register.device_id.__str__()},
                    "property": {"id": register.id.__str__()},
                },
            )
            return

        if isinstance(device_property, DeviceDynamicPropertyEntity):
            try:
                property_state = self.__devices_properties_states_repository.get_by_id(property_id=device_property.id)

            except (NotImplementedError, AttributeError):
                self.__logger.warning("States repository is not configured. State could not be fetched")

                return

            actual_value = (
                register.actual_value
                if isinstance(register.actual_value, (str, int, float, bool)) or register.actual_value is None
                else str(register.actual_value)
            )
            expected_value = (
                register.expected_value
                if isinstance(register.expected_value, (str, int, float, bool)) or register.expected_value is None
                else str(register.expected_value)
            )

            state_data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]] = {
                "actual_value": register.actual_value,
                "expected_value": register.expected_value,
                "pending": actual_value != expected_value and expected_value is not None,
                "valid": register.actual_value_valid,
            }

            if property_state is None:
                try:
                    property_state = self.__devices_properties_states_manager.create(
                        device_property=device_property,
                        data=state_data,
                    )

                except NotImplementedError:
                    self.__logger.warning("States manager is not configured. State could not be saved")

                    return

                self.__logger.debug(
                    "Creating new device property state",
                    extra={
                        "device": {
                            "id": device_property.device.id.__str__(),
                        },
                        "property": {
                            "id": device_property.id.__str__(),
                        },
                        "state": {
                            "id": property_state.id.__str__(),
                            "actual_value": property_state.actual_value,
                            "expected_value": property_state.expected_value,
                            "pending": property_state.pending,
                            "valid": property_state.valid,
                        },
                    },
                )

            else:
                stored_value = normalize_value(
                    data_type=device_property.data_type,
                    value=property_state.actual_value,
                    value_format=device_property.format,
                    value_invalid=device_property.invalid,
                )

                if self.__UPDATE_ALL_EVENTS or stored_value != register.actual_value:
                    try:
                        property_state = self.__devices_properties_states_manager.update(
                            device_property=device_property,
                            state=property_state,
                            data=state_data,
                        )

                    except NotImplementedError:
                        self.__logger.warning("States manager is not configured. State could not be saved")

                        return

                    self.__logger.debug(
                        "Updating existing device property state",
                        extra={
                            "device": {
                                "id": device_property.device.id.__str__(),
                            },
                            "property": {
                                "id": device_property.id.__str__(),
                            },
                            "state": {
                                "id": property_state.id.__str__(),
                                "actual_value": property_state.actual_value,
                                "expected_value": property_state.expected_value,
                                "pending": property_state.pending,
                                "valid": property_state.valid,
                            },
                        },
                    )

        elif isinstance(device_property, DeviceStaticPropertyEntity):
            actual_value_normalized = str(device_property.value) if device_property.value is not None else None
            updated_value_normalized = str(register.actual_value) if register.actual_value is not None else None

            if actual_value_normalized != updated_value_normalized:
                self.__devices_properties_manager.update(
                    data={
                        "value": register.actual_value,
                    },
                    device_property=device_property,
                )

                self.__logger.debug(
                    "Updating existing device property",
                    extra={
                        "device": {
                            "id": device_property.device.id.__str__(),
                        },
                        "property": {
                            "id": device_property.id.__str__(),
                        },
                    },
                )

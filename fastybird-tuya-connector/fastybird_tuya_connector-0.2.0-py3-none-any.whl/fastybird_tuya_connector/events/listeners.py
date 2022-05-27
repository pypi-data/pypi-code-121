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
Tuya connector events module listeners
"""

# Python base dependencies
import logging
import uuid
from datetime import datetime
from typing import Dict, Union

# Library dependencies
import inflection
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
from fastybird_metadata.types import ButtonPayload, SwitchPayload
from kink import inject
from whistle import Event, EventDispatcher

# Library libs
from fastybird_tuya_connector.entities import TuyaDeviceEntity
from fastybird_tuya_connector.events.events import (
    AttributeActualValueEvent,
    DataPointActualValueEvent,
    DataPointRecordCreatedOrUpdatedEvent,
    DeviceAttributeRecordCreatedOrUpdatedEvent,
    DevicePropertyRecordCreatedOrUpdatedEvent,
    DeviceRecordCreatedOrUpdatedEvent,
    PropertyActualValueEvent,
)
from fastybird_tuya_connector.logger import Logger
from fastybird_tuya_connector.types import DataPointType, DeviceProperty


@inject
class EventsListener:  # pylint: disable=too-many-instance-attributes
    """
    Events listener

    @package        FastyBird:TuyaConnector!
    @module         events/listeners

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __connector_id: uuid.UUID

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

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        connector_id: uuid.UUID,
        # Connector services
        event_dispatcher: EventDispatcher,
        # Devices module services
        devices_repository: DevicesRepository,
        devices_manager: DevicesManager,
        devices_properties_repository: DevicePropertiesRepository,
        devices_properties_manager: DevicePropertiesManager,
        devices_attributes_repository: DeviceAttributesRepository,
        devices_attributes_manager: DeviceAttributesManager,
        devices_properties_states_repository: DevicePropertiesStatesRepository,
        devices_properties_states_manager: DevicePropertiesStatesManager,
        channels_repository: ChannelsRepository,
        channels_manager: ChannelsManager,
        channels_properties_repository: ChannelPropertiesRepository,
        channels_properties_manager: ChannelPropertiesManager,
        channels_properties_states_repository: ChannelPropertiesStatesRepository,
        channels_properties_states_manager: ChannelPropertiesStatesManager,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__connector_id = connector_id

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
            event_id=DataPointRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_data_point,
        )

        self.__event_dispatcher.add_listener(
            event_id=DevicePropertyRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_property,
        )

        self.__event_dispatcher.add_listener(
            event_id=DeviceAttributeRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_attribute,
        )

        self.__event_dispatcher.add_listener(
            event_id=DataPointActualValueEvent.EVENT_NAME,
            listener=self.__handle_write_data_point_actual_value,
        )

        self.__event_dispatcher.add_listener(
            event_id=PropertyActualValueEvent.EVENT_NAME,
            listener=self.__handle_write_property_actual_value,
        )

        self.__event_dispatcher.add_listener(
            event_id=AttributeActualValueEvent.EVENT_NAME,
            listener=self.__handle_write_attribute_actual_value,
        )

    # -----------------------------------------------------------------------------

    def close(self) -> None:
        """Close all listeners registrations"""
        self.__event_dispatcher.remove_listener(
            event_id=DeviceRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_device,
        )

        self.__event_dispatcher.remove_listener(
            event_id=DataPointRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_data_point,
        )

        self.__event_dispatcher.remove_listener(
            event_id=DevicePropertyRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_property,
        )

        self.__event_dispatcher.remove_listener(
            event_id=DeviceAttributeRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_attribute,
        )

        self.__event_dispatcher.remove_listener(
            event_id=DataPointActualValueEvent.EVENT_NAME,
            listener=self.__handle_write_data_point_actual_value,
        )

        self.__event_dispatcher.remove_listener(
            event_id=PropertyActualValueEvent.EVENT_NAME,
            listener=self.__handle_write_property_actual_value,
        )

        self.__event_dispatcher.remove_listener(
            event_id=AttributeActualValueEvent.EVENT_NAME,
            listener=self.__handle_write_attribute_actual_value,
        )

    # -----------------------------------------------------------------------------

    def __handle_create_or_update_device(self, event: Event) -> None:  # pylint: disable=too-many-branches
        if not isinstance(event, DeviceRecordCreatedOrUpdatedEvent):
            return

        device_data = {
            "id": event.record.id,
            "identifier": event.record.identifier,
            "name": event.record.name,
        }

        device = self.__devices_repository.get_by_id(device_id=event.record.id)

        if device is None:
            # Define relation between device and it's connector
            device_data["connector_id"] = self.__connector_id

            device = self.__devices_manager.create(
                data=device_data,
                device_type=TuyaDeviceEntity,  # type: ignore[misc]
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

    def __handle_create_or_update_attribute(self, event: Event) -> None:
        if not isinstance(event, DeviceAttributeRecordCreatedOrUpdatedEvent):
            return

        attribute_data = {
            "id": event.record.id,
            "identifier": event.record.type.value,
            "name": None,
            "content": event.record.value,
        }

        device_attribute = self.__devices_attributes_repository.get_by_id(attribute_id=event.record.id)

        if device_attribute is None:
            # Define relation between device & channel
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

    def __handle_create_or_update_property(self, event: Event) -> None:
        if not isinstance(event, DevicePropertyRecordCreatedOrUpdatedEvent):
            return

        property_data = {
            "id": event.record.id,
            "identifier": event.record.type.value,
            "name": inflection.underscore(event.record.type.value),
            "settable": False,
            "queryable": False,
            "data_type": event.record.data_type,
            "format": event.record.format,
            "unit": None,
            "value": event.record.value,
        }

        device_property = self.__devices_properties_repository.get_by_id(property_id=event.record.id)

        if device_property is None:
            # Define relation between device & property
            property_data["device_id"] = event.record.device_id

            if event.record.type.__eq__(DeviceProperty.STATE):
                del property_data["value"]

                device_property = self.__devices_properties_manager.create(
                    data=property_data,
                    property_type=DeviceDynamicPropertyEntity,
                )

            else:
                device_property = self.__devices_properties_manager.create(
                    data=property_data,
                    property_type=DeviceStaticPropertyEntity,
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
            if device_property.name is not None:
                property_data["name"] = device_property.name

            if event.record.type.__eq__(DeviceProperty.STATE):
                del property_data["value"]

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

    # -----------------------------------------------------------------------------

    def __handle_create_or_update_data_point(self, event: Event) -> None:
        if not isinstance(event, DataPointRecordCreatedOrUpdatedEvent):
            return

        channel_identifier = (
            DataPointType.CLOUD.value if event.record.type == DataPointType.CLOUD else DataPointType.LOCAL.value
        )

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

        property_identifier = event.record.identifier

        if event.record.type == DataPointType.LOCAL:
            property_identifier = f"dp_{event.record.index}"

        property_data = {
            "id": event.record.id,
            "identifier": property_identifier,
            "name": None,
            "unit": None,
            "data_type": event.record.data_type,
            "format": event.record.format,
            "invalid": None,
            "queryable": event.record.queryable,
            "settable": event.record.settable,
        }

        channel_property = self.__channels_properties_repository.get_by_id(property_id=event.record.id)

        if channel_property is None:
            # Define relation between channel & property
            property_data["channel_id"] = channel.id

            channel_property = self.__channels_properties_manager.create(
                data=property_data,
                property_type=ChannelDynamicPropertyEntity,
            )

            self.__logger.debug(
                "Creating new channel property",
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
            if channel_property.name is not None:
                property_data["name"] = channel_property.name

            channel_property = self.__channels_properties_manager.update(
                data=property_data,
                channel_property=channel_property,
            )

            self.__logger.debug(
                "Updating existing channel property",
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

    # -----------------------------------------------------------------------------

    def __handle_write_attribute_actual_value(self, event: Event) -> None:
        if not isinstance(event, AttributeActualValueEvent):
            return

        device_attribute = self.__devices_attributes_repository.get_by_id(attribute_id=event.updated_record.id)

        if device_attribute is None:
            self.__logger.warning(
                "Device attribute couldn't be found in database",
                extra={
                    "device": {"id": event.updated_record.device_id.__str__()},
                    "attribute": {"id": event.updated_record.id.__str__()},
                },
            )
            return

        self.__devices_attributes_manager.update(
            data={
                "content": event.updated_record.value,
            },
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

    def __handle_write_property_actual_value(self, event: Event) -> None:
        if not isinstance(event, PropertyActualValueEvent):
            return

        device_property = self.__devices_properties_repository.get_by_id(property_id=event.updated_record.id)

        if device_property is None:
            self.__logger.warning(
                "Device property couldn't be found in database",
                extra={
                    "device": {"id": event.updated_record.device_id.__str__()},
                    "property": {"id": event.updated_record.id.__str__()},
                },
            )
            return

        if isinstance(device_property, DeviceDynamicPropertyEntity):
            try:
                property_state = self.__devices_properties_states_repository.get_by_id(
                    property_id=device_property.id,
                )

            except NotImplementedError:
                self.__logger.warning("States repository is not configured. State could not be fetched")

                return

            state_data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]] = {
                "actual_value": event.updated_record.actual_value,
                "expected_value": None,
                "pending": False,
                "valid": True,
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
            updated_value_normalized = (
                str(event.updated_record.actual_value) if event.updated_record.actual_value is not None else None
            )

            if actual_value_normalized != updated_value_normalized:
                self.__devices_properties_manager.update(
                    data={
                        "value": event.updated_record.actual_value,
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

    # -----------------------------------------------------------------------------

    def __handle_write_data_point_actual_value(self, event: Event) -> None:
        if not isinstance(event, DataPointActualValueEvent):
            return

        channel_property = self.__channels_properties_repository.get_by_id(property_id=event.updated_record.id)

        if channel_property is None:
            self.__logger.warning(
                "Channel property couldn't be found in database",
                extra={
                    "property": {"id": event.updated_record.id.__str__()},
                },
            )
            return

        if isinstance(channel_property, ChannelDynamicPropertyEntity):
            try:
                property_state = self.__channels_properties_states_repository.get_by_id(property_id=channel_property.id)

            except NotImplementedError:
                self.__logger.warning("States repository is not configured. State could not be fetched")

                return

            actual_value = (
                event.updated_record.actual_value
                if isinstance(event.updated_record.actual_value, (str, int, float, bool))
                or event.updated_record.actual_value is None
                else str(event.updated_record.actual_value)
            )
            expected_value = (
                event.updated_record.expected_value
                if isinstance(event.updated_record.expected_value, (str, int, float, bool))
                or event.updated_record.expected_value is None
                else str(event.updated_record.expected_value)
            )

            state_data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]] = {
                "actual_value": event.updated_record.actual_value,
                "expected_value": event.updated_record.expected_value,
                "pending": actual_value != expected_value and expected_value is not None,
                "valid": event.updated_record.actual_value_valid,
            }

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

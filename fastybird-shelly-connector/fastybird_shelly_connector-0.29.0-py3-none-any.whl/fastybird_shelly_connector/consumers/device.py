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
Shelly connector consumers module consumer for device messages
"""

# Python base dependencies
import uuid
from typing import Optional, Set

# Library dependencies
from fastybird_metadata.devices_module import ConnectionState

# Library libs
from fastybird_shelly_connector.consumers.consumer import IConsumer
from fastybird_shelly_connector.consumers.entities import (
    BaseEntity,
    DeviceDescriptionEntity,
    DeviceDescriptionFromCoapEntity,
    DeviceDescriptionFromHttpEntity,
    DeviceExtendedStatusEntity,
    DeviceFoundEntity,
    DeviceInfoEntity,
    DeviceSettingsFromHttpEntity,
    DeviceStatusEntity,
)
from fastybird_shelly_connector.registry.model import (
    BlocksRegistry,
    DevicesRegistry,
    PropertiesRegistry,
    SensorsRegistry,
)
from fastybird_shelly_connector.registry.records import DeviceRecord, SensorRecord
from fastybird_shelly_connector.types import DeviceDescriptionSource, DeviceProperty


class DeviceDescriptionConsumer(IConsumer):  # pylint: disable=too-few-public-methods
    """
    Device description message consumer

    @package        FastyBird:ShellyConnector!
    @module         consumers/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry
    __properties_registry: PropertiesRegistry
    __blocks_registry: BlocksRegistry
    __sensors_registry: SensorsRegistry

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        devices_registry: DevicesRegistry,
        properties_registry: PropertiesRegistry,
        blocks_registry: BlocksRegistry,
        sensors_registry: SensorsRegistry,
    ) -> None:
        self.__devices_registry = devices_registry
        self.__properties_registry = properties_registry
        self.__blocks_registry = blocks_registry
        self.__sensors_registry = sensors_registry

    # -----------------------------------------------------------------------------

    def consume(self, entity: BaseEntity) -> None:
        """Handle received message"""
        if not isinstance(entity, (DeviceDescriptionEntity, DeviceInfoEntity, DeviceExtendedStatusEntity)):
            return

        if isinstance(entity, DeviceDescriptionEntity):
            device_record = self.__receive_basic_description(entity=entity)

        elif isinstance(entity, DeviceInfoEntity):
            device_record = self.__receive_info(entity=entity)

        elif isinstance(entity, DeviceExtendedStatusEntity):
            device_record = self.__receive_extended_description(entity=entity)

        else:
            return

        if device_record is None:
            return

        # Set device connection state
        state_property_record = self.__properties_registry.get_by_property(
            device_id=device_record.id,
            property_type=DeviceProperty.STATE,
        )

        if state_property_record is not None and state_property_record.actual_value != ConnectionState.CONNECTED.value:
            self.__properties_registry.set_value(
                item=state_property_record,
                value=ConnectionState.CONNECTED.value,
            )

    # -----------------------------------------------------------------------------

    def __receive_basic_description(  # pylint: disable=too-many-branches
        self,
        entity: DeviceDescriptionEntity,
    ) -> Optional[DeviceRecord]:
        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=entity.identifier,
        )

        if isinstance(entity, DeviceDescriptionFromCoapEntity):
            if device_record is not None:
                device_record = self.__devices_registry.create_or_update(
                    description_source=DeviceDescriptionSource.COAP_DESCRIPTION,
                    device_id=device_record.id,
                    device_identifier=entity.identifier,
                    device_type=entity.type,
                    device_mac_address=device_record.mac_address,
                    device_firmware_version=device_record.firmware_version,
                    device_name=device_record.name,
                )

            else:
                device_record = self.__devices_registry.create_or_update(
                    description_source=DeviceDescriptionSource.COAP_DESCRIPTION,
                    device_id=uuid.uuid4(),
                    device_identifier=entity.identifier,
                    device_type=entity.type,
                )

        elif isinstance(entity, DeviceDescriptionFromHttpEntity):
            if device_record is None:
                return None

            device_record = self.__devices_registry.create_or_update(
                description_source=DeviceDescriptionSource.HTTP_DESCRIPTION,
                device_id=device_record.id,
                device_identifier=entity.identifier,
                device_type=device_record.type,
                device_mac_address=device_record.mac_address,
                device_firmware_version=device_record.firmware_version,
                device_name=device_record.name,
            )

        else:
            raise AttributeError("Provided entity is not supported")

        self.__properties_registry.create_or_update(
            device_id=device_record.id,
            property_type=DeviceProperty.IP_ADDRESS,
            property_value=entity.ip_address,
        )

        for block_description in entity.blocks:
            block_record = self.__blocks_registry.get_by_identifier(
                device_id=device_record.id,
                block_identifier=block_description.identifier,
            )

            if block_record is not None:
                block_record = self.__blocks_registry.create_or_update(
                    device_id=device_record.id,
                    block_id=block_record.id,
                    block_identifier=block_description.identifier,
                    block_description=block_description.description,
                )

            else:
                block_record = self.__blocks_registry.create_or_update(
                    device_id=device_record.id,
                    block_id=uuid.uuid4(),
                    block_identifier=block_description.identifier,
                    block_description=block_description.description,
                )

            for sensor_state_description in block_description.sensors_states:
                sensor_state_record = self.__sensors_registry.get_by_identifier(
                    block_id=block_record.id,
                    sensor_identifier=sensor_state_description.identifier,
                )

                if sensor_state_record is not None:
                    self.__sensors_registry.create_or_update(
                        block_id=block_record.id,
                        sensor_id=sensor_state_record.id,
                        sensor_identifier=sensor_state_description.identifier,
                        sensor_description=sensor_state_description.description,
                        sensor_type=sensor_state_description.type,
                        sensor_unit=sensor_state_description.unit,
                        sensor_data_type=sensor_state_description.data_type,
                        sensor_value_format=sensor_state_description.format,
                        sensor_value_invalid=sensor_state_description.invalid,
                        sensor_queryable=sensor_state_description.queryable,
                        sensor_settable=sensor_state_description.settable,
                    )

                else:
                    self.__sensors_registry.create_or_update(
                        block_id=block_record.id,
                        sensor_id=uuid.uuid4(),
                        sensor_identifier=sensor_state_description.identifier,
                        sensor_description=sensor_state_description.description,
                        sensor_type=sensor_state_description.type,
                        sensor_unit=sensor_state_description.unit,
                        sensor_data_type=sensor_state_description.data_type,
                        sensor_value_format=sensor_state_description.format,
                        sensor_value_invalid=sensor_state_description.invalid,
                        sensor_queryable=sensor_state_description.queryable,
                        sensor_settable=sensor_state_description.settable,
                    )

        return device_record

    # -----------------------------------------------------------------------------

    def __receive_info(self, entity: DeviceInfoEntity) -> Optional[DeviceRecord]:
        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=entity.identifier,
        )

        if device_record is None:
            return None

        device_record = self.__devices_registry.create_or_update(
            description_source=DeviceDescriptionSource.HTTP_SHELLY,
            device_id=device_record.id,
            device_identifier=entity.identifier,
            device_type=entity.type,
            device_mac_address=entity.mac_address,
            device_firmware_version=entity.firmware_version,
            device_name=device_record.name,
        )

        self.__properties_registry.create_or_update(
            device_id=device_record.id,
            property_type=DeviceProperty.IP_ADDRESS,
            property_value=entity.ip_address,
        )

        self.__properties_registry.create_or_update(
            device_id=device_record.id,
            property_type=DeviceProperty.AUTH_ENABLED,
            property_value=entity.auth_enabled,
        )

        return device_record

    # -----------------------------------------------------------------------------

    def __receive_extended_description(self, entity: DeviceExtendedStatusEntity) -> Optional[DeviceRecord]:
        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=entity.identifier,
        )

        if device_record is None:
            return None

        device_record = self.__devices_registry.create_or_update(
            description_source=DeviceDescriptionSource.HTTP_STATUS,
            device_id=device_record.id,
            device_identifier=entity.identifier,
            device_type=device_record.type,
            device_mac_address=device_record.mac_address,
            device_firmware_version=device_record.firmware_version,
            device_name=device_record.name,
        )

        self.__properties_registry.create_or_update(
            device_id=device_record.id,
            property_type=DeviceProperty.IP_ADDRESS,
            property_value=entity.ip_address,
        )

        return device_record


class DeviceFoundConsumer(IConsumer):  # pylint: disable=too-few-public-methods
    """
    Device state message consumer

    @package        FastyBird:ShellyConnector!
    @module         consumers/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry
    __properties_registry: PropertiesRegistry

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        devices_registry: DevicesRegistry,
        properties_registry: PropertiesRegistry,
    ) -> None:
        self.__devices_registry = devices_registry
        self.__properties_registry = properties_registry

    # -----------------------------------------------------------------------------

    def consume(self, entity: BaseEntity) -> None:
        """Handle received message"""
        if not isinstance(entity, DeviceFoundEntity):
            return

        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=entity.identifier,
        )

        if device_record is not None:
            device_record = self.__devices_registry.create_or_update(
                description_source=DeviceDescriptionSource.MDNS_DISCOVERY,
                device_id=device_record.id,
                device_identifier=entity.identifier,
                device_type=device_record.type,
                device_mac_address=device_record.mac_address,
                device_firmware_version=device_record.firmware_version,
                device_name=device_record.name,
            )

        else:
            device_record = self.__devices_registry.create_or_update(
                description_source=DeviceDescriptionSource.MDNS_DISCOVERY,
                device_id=uuid.uuid4(),
                device_identifier=entity.identifier,
            )

        self.__properties_registry.create_or_update(
            device_id=device_record.id,
            property_type=DeviceProperty.IP_ADDRESS,
            property_value=entity.ip_address,
        )

        # Set device connection state
        state_property_record = self.__properties_registry.get_by_property(
            device_id=device_record.id,
            property_type=DeviceProperty.STATE,
        )

        if state_property_record is not None and state_property_record.actual_value != ConnectionState.RUNNING.value:
            self.__properties_registry.set_value(
                item=state_property_record,
                value=ConnectionState.CONNECTED.value,
            )


class DeviceStateConsumer(IConsumer):  # pylint: disable=too-few-public-methods
    """
    Device state message consumer

    @package        FastyBird:ShellyConnector!
    @module         consumers/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry
    __properties_registry: PropertiesRegistry
    __blocks_registry: BlocksRegistry
    __sensors_registry: SensorsRegistry

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        devices_registry: DevicesRegistry,
        properties_registry: PropertiesRegistry,
        blocks_registry: BlocksRegistry,
        sensors_registry: SensorsRegistry,
    ) -> None:
        self.__devices_registry = devices_registry
        self.__properties_registry = properties_registry
        self.__blocks_registry = blocks_registry
        self.__sensors_registry = sensors_registry

    # -----------------------------------------------------------------------------

    def consume(self, entity: BaseEntity) -> None:
        """Handle received message"""
        if not isinstance(entity, DeviceStatusEntity):
            return

        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=entity.identifier,
        )

        if device_record is None:
            return

        self.__properties_registry.create_or_update(
            device_id=device_record.id,
            property_type=DeviceProperty.IP_ADDRESS,
            property_value=entity.ip_address,
        )

        device_sensors: Set[SensorRecord] = set()

        for block_record in self.__blocks_registry.get_all_by_device(device_id=device_record.id):
            for block_sensor_record in self.__sensors_registry.get_all_for_block(block_id=block_record.id):
                device_sensors.add(block_sensor_record)

        for sensor_state in entity.sensors_states:
            sensor_record = next(
                iter([record for record in device_sensors if record.identifier == sensor_state.identifier]),
                None,
            )

            if sensor_record is not None:
                self.__sensors_registry.set_actual_value(
                    sensor=sensor_record,
                    value=sensor_state.value,
                )

        # Set device connection state
        state_property_record = self.__properties_registry.get_by_property(
            device_id=device_record.id,
            property_type=DeviceProperty.STATE,
        )

        if state_property_record is not None and state_property_record.value != ConnectionState.CONNECTED.value:
            self.__properties_registry.set_value(
                item=state_property_record,
                value=ConnectionState.CONNECTED.value,
            )


class DeviceSettingsConsumer(IConsumer):  # pylint: disable=too-few-public-methods
    """
    Device settings message consumer

    @package        FastyBird:ShellyConnector!
    @module         consumers/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        devices_registry: DevicesRegistry,
    ) -> None:
        self.__devices_registry = devices_registry

    # -----------------------------------------------------------------------------

    def consume(self, entity: BaseEntity) -> None:
        """Handle received message"""
        if not isinstance(entity, DeviceSettingsFromHttpEntity):
            return

        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=entity.identifier,
        )

        if device_record is None:
            return

        self.__devices_registry.create_or_update(
            description_source=DeviceDescriptionSource.HTTP_SETTINGS,
            device_id=device_record.id,
            device_identifier=device_record.identifier,
            device_type=device_record.type,
            device_mac_address=device_record.mac_address,
            device_firmware_version=device_record.firmware_version,
            device_name=entity.name,
        )

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
Tuya connector consumers module consumer for device messages
"""

# Python base dependencies
import uuid
from typing import Optional

# Library dependencies
from fastybird_metadata.devices_module import ConnectionState

# Library libs
from fastybird_tuya_connector.consumers.consumer import IConsumer
from fastybird_tuya_connector.consumers.entities import (
    BaseEntity,
    CloudDeviceFoundEntity,
    DeviceFoundEntity,
    DeviceStatusEntity,
    LocalDeviceFoundEntity,
)
from fastybird_tuya_connector.registry.model import (
    AttributesRegistry,
    DataPointsRegistry,
    DevicesRegistry,
    DiscoveredDataPointsRegistry,
    DiscoveredDevicesRegistry,
    PropertiesRegistry,
    TuyaCloudDataPointsRegistry,
    TuyaCloudDevicesRegistry,
)
from fastybird_tuya_connector.registry.records import DataPointRecord
from fastybird_tuya_connector.types import (
    DataPointType,
    DeviceAttribute,
    DeviceProperty,
)


class DeviceFoundConsumer(IConsumer):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """
    Device state message consumer

    @package        FastyBird:TuyaConnector!
    @module         consumers/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry
    __data_points_registry: DataPointsRegistry
    __properties_registry: PropertiesRegistry
    __attributes_registry: AttributesRegistry
    __discovered_devices_registry: DiscoveredDevicesRegistry
    __discovered_data_points_registry: DiscoveredDataPointsRegistry
    __tuya_cloud_devices_registry: TuyaCloudDevicesRegistry
    __tuya_cloud_data_points_registry: TuyaCloudDataPointsRegistry

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        devices_registry: DevicesRegistry,
        data_points_registry: DataPointsRegistry,
        properties_registry: PropertiesRegistry,
        attributes_registry: AttributesRegistry,
        discovered_devices_registry: DiscoveredDevicesRegistry,
        discovered_data_points_registry: DiscoveredDataPointsRegistry,
        tuya_cloud_devices_registry: TuyaCloudDevicesRegistry,
        tuya_cloud_data_points_registry: TuyaCloudDataPointsRegistry,
    ) -> None:
        self.__devices_registry = devices_registry
        self.__data_points_registry = data_points_registry
        self.__properties_registry = properties_registry
        self.__attributes_registry = attributes_registry
        self.__discovered_devices_registry = discovered_devices_registry
        self.__discovered_data_points_registry = discovered_data_points_registry
        self.__tuya_cloud_devices_registry = tuya_cloud_devices_registry
        self.__tuya_cloud_data_points_registry = tuya_cloud_data_points_registry

    # -----------------------------------------------------------------------------

    def consume(self, entity: BaseEntity) -> None:  # pylint: disable=too-many-branches
        """Handle received message"""
        if not isinstance(entity, DeviceFoundEntity):
            return

        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=entity.identifier,
        )

        if isinstance(entity, CloudDeviceFoundEntity):
            cloud_device_record = self.__tuya_cloud_devices_registry.get_by_id(device_id=entity.identifier)

            if cloud_device_record is None:
                return

            if device_record is not None:
                device_record = self.__devices_registry.create_or_update(
                    device_id=device_record.id,
                    device_identifier=cloud_device_record.id,
                    device_name=cloud_device_record.name,
                )

            else:
                device_record = self.__devices_registry.create_or_update(
                    device_id=uuid.uuid4(),
                    device_identifier=cloud_device_record.id,
                    device_name=cloud_device_record.name,
                )

            self.__properties_registry.create_or_update(
                device_id=device_record.id,
                property_type=DeviceProperty.LOCAL_KEY,
                property_value=cloud_device_record.local_key,
            )

            self.__properties_registry.create_or_update(
                device_id=device_record.id,
                property_type=DeviceProperty.USER_IDENTIFIER,
                property_value=cloud_device_record.uid,
            )

            self.__properties_registry.create_or_update(
                device_id=device_record.id,
                property_type=DeviceProperty.IP_ADDRESS,
                property_value=None,
            )

            self.__attributes_registry.create_or_update(
                device_id=device_record.id,
                attribute_type=DeviceAttribute.MODEL,
                attribute_value=cloud_device_record.model,
            )

            self.__attributes_registry.create_or_update(
                device_id=device_record.id,
                attribute_type=DeviceAttribute.MAC_ADDRESS,
                attribute_value=cloud_device_record.mac_address,
            )

            self.__attributes_registry.create_or_update(
                device_id=device_record.id,
                attribute_type=DeviceAttribute.SERIAL_NUMBER,
                attribute_value=cloud_device_record.serial_number,
            )

            for cloud_data_point in self.__tuya_cloud_data_points_registry.get_all_by_device(
                device_id=cloud_device_record.id
            ):
                data_point_record = self.__data_points_registry.get_by_identifier(
                    device_id=device_record.id,
                    dp_identifier=cloud_data_point.code,
                )

                if data_point_record is not None:
                    self.__data_points_registry.create_or_update(
                        device_id=device_record.id,
                        dp_id=data_point_record.id,
                        dp_identifier=data_point_record.identifier,
                        dp_type=DataPointType.CLOUD,
                        dp_name=cloud_data_point.name,
                        dp_data_type=cloud_data_point.data_type,
                        dp_unit=cloud_data_point.unit,
                        dp_value_format=cloud_data_point.value_format,
                        dp_queryable=cloud_data_point.queryable,
                        dp_settable=cloud_data_point.settable,
                    )

                else:
                    self.__data_points_registry.create_or_update(
                        device_id=device_record.id,
                        dp_id=uuid.uuid4(),
                        dp_identifier=cloud_data_point.code,
                        dp_type=DataPointType.CLOUD,
                        dp_name=cloud_data_point.name,
                        dp_data_type=cloud_data_point.data_type,
                        dp_unit=cloud_data_point.unit,
                        dp_value_format=cloud_data_point.value_format,
                        dp_queryable=cloud_data_point.queryable,
                        dp_settable=cloud_data_point.settable,
                    )

        elif isinstance(entity, LocalDeviceFoundEntity):
            local_device_record = self.__discovered_devices_registry.get_by_id(device_id=entity.identifier)

            if local_device_record is None:
                return

            if device_record is not None:
                device_record = self.__devices_registry.create_or_update(
                    device_id=device_record.id,
                    device_identifier=local_device_record.id,
                    device_name=device_record.name,
                )

            else:
                device_record = self.__devices_registry.create_or_update(
                    device_id=uuid.uuid4(),
                    device_identifier=local_device_record.id,
                )

            self.__properties_registry.create_or_update(
                device_id=device_record.id,
                property_type=DeviceProperty.IP_ADDRESS,
                property_value=local_device_record.ip_address,
            )

            self.__attributes_registry.create_or_update(
                device_id=device_record.id,
                attribute_type=DeviceAttribute.ENCRYPTED,
                attribute_value=local_device_record.encrypted,
            )

            self.__attributes_registry.create_or_update(
                device_id=device_record.id,
                attribute_type=DeviceAttribute.PROTOCOL_VERSION,
                attribute_value=local_device_record.version.value,
            )

            for local_data_point in self.__discovered_data_points_registry.get_all_by_device(
                device_id=local_device_record.id
            ):
                data_point_record = self.__data_points_registry.get_by_index(
                    device_id=device_record.id,
                    dp_index=local_data_point.index,
                )

                if data_point_record is not None:
                    self.__data_points_registry.create_or_update(
                        device_id=device_record.id,
                        dp_id=data_point_record.id,
                        dp_index=data_point_record.index,
                        dp_type=DataPointType.LOCAL,
                        dp_name=None,
                        dp_data_type=local_data_point.data_type,
                        dp_unit=None,
                        dp_value_format=None,
                        dp_queryable=True,
                        dp_settable=True,
                    )

                else:
                    self.__data_points_registry.create_or_update(
                        device_id=device_record.id,
                        dp_id=uuid.uuid4(),
                        dp_index=local_data_point.index,
                        dp_type=DataPointType.LOCAL,
                        dp_name=None,
                        dp_data_type=local_data_point.data_type,
                        dp_unit=None,
                        dp_value_format=None,
                        dp_queryable=True,
                        dp_settable=True,
                    )


class DeviceStateConsumer(IConsumer):  # pylint: disable=too-few-public-methods
    """
    Device state message consumer

    @package        FastyBird:TuyaConnector!
    @module         consumers/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry
    __data_points_registry: DataPointsRegistry
    __properties_registry: PropertiesRegistry

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        devices_registry: DevicesRegistry,
        data_points_registry: DataPointsRegistry,
        properties_registry: PropertiesRegistry,
    ) -> None:
        self.__devices_registry = devices_registry
        self.__data_points_registry = data_points_registry
        self.__properties_registry = properties_registry

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

        for dp_state in entity.dps_states:
            device_dp: Optional[DataPointRecord] = None
            if dp_state.identifier is not None:
                device_dp = self.__data_points_registry.get_by_identifier(
                    device_id=device_record.id,
                    dp_identifier=dp_state.identifier,
                )

            elif dp_state.index is not None:
                device_dp = self.__data_points_registry.get_by_index(
                    device_id=device_record.id,
                    dp_index=dp_state.index,
                )

            if device_dp is not None:
                self.__data_points_registry.set_actual_value(
                    data_point=device_dp,
                    value=dp_state.value,
                )

        # Set device connection state
        state_property = self.__properties_registry.get_by_property(
            device_id=device_record.id,
            property_type=DeviceProperty.STATE,
        )

        if state_property is not None and state_property.value != ConnectionState.CONNECTED.value:
            self.__properties_registry.set_value(
                device_property=state_property,
                value=ConnectionState.CONNECTED.value,
            )

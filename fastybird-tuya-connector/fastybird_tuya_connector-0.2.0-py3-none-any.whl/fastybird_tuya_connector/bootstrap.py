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
Tuya connector DI container
"""

# pylint: disable=no-value-for-parameter

# Python base dependencies
import logging

# Library dependencies
from fastybird_devices_module.exceptions import TerminateConnectorException
from kink import di
from whistle import EventDispatcher

# Library libs
from fastybird_tuya_connector.api.openapi import TuyaOpenAPI
from fastybird_tuya_connector.clients.cloud import TuyaCloudClient
from fastybird_tuya_connector.clients.local import LocalDeviceClient
from fastybird_tuya_connector.connector import TuyaConnector
from fastybird_tuya_connector.consumers.consumer import Consumer
from fastybird_tuya_connector.consumers.device import (
    DeviceFoundConsumer,
    DeviceStateConsumer,
)
from fastybird_tuya_connector.discovery import DevicesDiscovery
from fastybird_tuya_connector.entities import (  # pylint: disable=unused-import
    TuyaConnectorEntity,
    TuyaDeviceEntity,
)
from fastybird_tuya_connector.events.listeners import EventsListener
from fastybird_tuya_connector.logger import Logger
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


def create_connector(
    connector: TuyaConnectorEntity,
    logger: logging.Logger = logging.getLogger("dummy"),
) -> TuyaConnector:
    """Create Tuya connector services"""
    if isinstance(logger, logging.Logger):
        connector_logger = Logger(connector_id=connector.id, logger=logger)

        di[Logger] = connector_logger
        di["tuya-connector_logger"] = di[Logger]

    else:
        connector_logger = logger

    if connector.access_id is None or connector.access_secret is None:
        raise TerminateConnectorException("Missing connector configuration")

    di[EventDispatcher] = EventDispatcher()
    di["tuya-connector_events-dispatcher"] = di[EventDispatcher]

    # Registers
    di[DataPointsRegistry] = DataPointsRegistry(event_dispatcher=di[EventDispatcher])  # type: ignore[call-arg]
    di["tuya-connector_data-points-registry"] = di[DataPointsRegistry]
    di[PropertiesRegistry] = PropertiesRegistry(event_dispatcher=di[EventDispatcher])
    di["tuya-connector_data-properties-registry"] = di[PropertiesRegistry]
    di[AttributesRegistry] = AttributesRegistry(event_dispatcher=di[EventDispatcher])
    di["tuya-connector_data-attributes-registry"] = di[AttributesRegistry]
    di[DevicesRegistry] = DevicesRegistry(
        data_points_registry=di[DataPointsRegistry],
        attributes_registry=di[AttributesRegistry],
        properties_registry=di[PropertiesRegistry],
        event_dispatcher=di[EventDispatcher],
    )
    di["tuya-connector_data-devices-registry"] = di[DevicesRegistry]
    di[DiscoveredDataPointsRegistry] = DiscoveredDataPointsRegistry()
    di["tuya-connector_data-discovered-data-points-registry"] = di[DiscoveredDataPointsRegistry]
    di[DiscoveredDevicesRegistry] = DiscoveredDevicesRegistry(data_points_registry=di[DiscoveredDataPointsRegistry])
    di["tuya-connector_data-discovered-devices-registry"] = di[DiscoveredDevicesRegistry]
    di[TuyaCloudDataPointsRegistry] = TuyaCloudDataPointsRegistry()
    di["tuya-connector_data-tuya-cloud-data-points-registry"] = di[TuyaCloudDataPointsRegistry]
    di[TuyaCloudDevicesRegistry] = TuyaCloudDevicesRegistry(data_points_registry=di[TuyaCloudDataPointsRegistry])
    di["tuya-connector_data-tuya-cloud-devices-registry"] = di[TuyaCloudDevicesRegistry]

    # API
    di[TuyaOpenAPI] = TuyaOpenAPI(
        endpoint=connector.openapi_endpoint,
        access_id=connector.access_id,
        access_secret=connector.access_secret,
        logger=connector_logger,
    )
    di["tuya-connector_api-openapi"] = di[TuyaOpenAPI]

    # Connector messages consumers
    di[DeviceFoundConsumer] = DeviceFoundConsumer(
        devices_registry=di[DevicesRegistry],
        data_points_registry=di[DataPointsRegistry],
        properties_registry=di[PropertiesRegistry],
        attributes_registry=di[AttributesRegistry],
        discovered_devices_registry=di[DiscoveredDevicesRegistry],
        discovered_data_points_registry=di[DiscoveredDataPointsRegistry],
        tuya_cloud_devices_registry=di[TuyaCloudDevicesRegistry],
        tuya_cloud_data_points_registry=di[TuyaCloudDataPointsRegistry],
    )
    di["tuya-connector_device-found-consumer"] = di[DeviceFoundConsumer]

    di[DeviceStateConsumer] = DeviceStateConsumer(
        devices_registry=di[DevicesRegistry],
        data_points_registry=di[DataPointsRegistry],
        properties_registry=di[PropertiesRegistry],
    )
    di["tuya-connector_device-state-consumer"] = di[DeviceStateConsumer]

    di[Consumer] = Consumer(
        consumers=[
            di[DeviceStateConsumer],
            di[DeviceFoundConsumer],
        ],
        logger=connector_logger,
    )
    di["tuya-connector_consumers-proxy"] = di[Consumer]

    # Clients
    di[TuyaCloudClient] = TuyaCloudClient(
        endpoint=connector.openpulsar_endpoint,
        access_id=connector.access_id,
        access_secret=connector.access_secret,
        consumer=di[Consumer],
        devices_registry=di[DevicesRegistry],
        properties_registry=di[PropertiesRegistry],
        data_points_registry=di[DataPointsRegistry],
        openapi=di[TuyaOpenAPI],
        logger=connector_logger,
    )
    di["tuya-connector_cloud-device-client"] = di[TuyaCloudClient]
    di[LocalDeviceClient] = LocalDeviceClient(
        consumer=di[Consumer],
        devices_registry=di[DevicesRegistry],
        properties_registry=di[PropertiesRegistry],
        data_points_registry=di[DataPointsRegistry],
        logger=connector_logger,
    )
    di["tuya-connector_local-device-client"] = di[LocalDeviceClient]

    # Devices discovery
    di[DevicesDiscovery] = DevicesDiscovery(
        discovered_devices_registry=di[DiscoveredDevicesRegistry],
        discovered_data_points_registry=di[DiscoveredDataPointsRegistry],
        tuya_cloud_devices_registry=di[TuyaCloudDevicesRegistry],
        tuya_cloud_data_points_registry=di[TuyaCloudDataPointsRegistry],
        openapi=di[TuyaOpenAPI],
        consumer=di[Consumer],
        logger=logger,
    )
    di["tuya-connector_discovery-client"] = di[DevicesDiscovery]

    # Inner events system
    di[EventsListener] = EventsListener(  # type: ignore[call-arg]
        connector_id=connector.id,
        event_dispatcher=di[EventDispatcher],
        logger=connector_logger,
    )
    di["tuya-connector_events-listener"] = di[EventsListener]

    # Main connector service
    connector_service = TuyaConnector(
        mode=connector.communication_mode,
        connector_id=connector.id,
        devices_registry=di[DevicesRegistry],
        properties_registry=di[PropertiesRegistry],
        attributes_registry=di[AttributesRegistry],
        data_points_registry=di[DataPointsRegistry],
        devices_discovery=di[DevicesDiscovery],
        local_device_client=di[LocalDeviceClient],
        cloud_device_client=di[TuyaCloudClient],
        consumer=di[Consumer],
        events_listener=di[EventsListener],
        logger=connector_logger,
    )
    di[TuyaConnector] = connector_service
    di["tuya-connector_connector"] = connector_service

    return connector_service

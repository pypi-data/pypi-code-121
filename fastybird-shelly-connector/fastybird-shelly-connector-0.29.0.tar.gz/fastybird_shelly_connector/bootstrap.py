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
Shelly connector DI container module
"""

# pylint: disable=no-value-for-parameter

# Python base dependencies
import logging

# Library dependencies
from kink import di
from whistle import EventDispatcher

# Library libs
from fastybird_shelly_connector.api.gen1parser import Gen1Parser
from fastybird_shelly_connector.api.gen1validator import Gen1Validator
from fastybird_shelly_connector.clients.client import Client
from fastybird_shelly_connector.clients.coap import CoapClient
from fastybird_shelly_connector.clients.http import HttpClient
from fastybird_shelly_connector.clients.mdns import MdnsClient
from fastybird_shelly_connector.connector import ShellyConnector
from fastybird_shelly_connector.consumers.consumer import Consumer
from fastybird_shelly_connector.consumers.device import (
    DeviceDescriptionConsumer,
    DeviceFoundConsumer,
    DeviceSettingsConsumer,
    DeviceStateConsumer,
)
from fastybird_shelly_connector.entities import (  # pylint: disable=unused-import
    ShellyConnectorEntity,
    ShellyDeviceEntity,
)
from fastybird_shelly_connector.events.listeners import EventsListener
from fastybird_shelly_connector.logger import Logger
from fastybird_shelly_connector.registry.model import (
    BlocksRegistry,
    CommandsRegistry,
    DevicesRegistry,
    PropertiesRegistry,
    SensorsRegistry,
)


def create_connector(
    connector: ShellyConnectorEntity,
    logger: logging.Logger = logging.getLogger("dummy"),
) -> ShellyConnector:
    """Create Shelly connector services"""
    if isinstance(logger, logging.Logger):
        connector_logger = Logger(connector_id=connector.id, logger=logger)

        di[Logger] = connector_logger
        di["shelly-connector_logger"] = di[Logger]

    else:
        connector_logger = logger

    di[EventDispatcher] = EventDispatcher()
    di["shelly-connector_events-dispatcher"] = di[EventDispatcher]

    # Registers
    di[SensorsRegistry] = SensorsRegistry(event_dispatcher=di[EventDispatcher])  # type: ignore[call-arg]
    di["shelly-connector_sensors-registry"] = di[SensorsRegistry]
    di[BlocksRegistry] = BlocksRegistry(sensors_registry=di[SensorsRegistry], event_dispatcher=di[EventDispatcher])
    di["shelly-connector_blocks-registry"] = di[BlocksRegistry]
    di[CommandsRegistry] = CommandsRegistry()
    di["shelly-connector_devices-commands-registry"] = di[CommandsRegistry]
    di[PropertiesRegistry] = PropertiesRegistry(event_dispatcher=di[EventDispatcher])
    di["shelly-connector_devices-attributes-registry"] = di[PropertiesRegistry]
    di[DevicesRegistry] = DevicesRegistry(
        commands_registry=di[CommandsRegistry],
        properties_registry=di[PropertiesRegistry],
        blocks_registry=di[BlocksRegistry],
        event_dispatcher=di[EventDispatcher],
    )
    di["shelly-connector_devices-registry"] = di[DevicesRegistry]

    # API utils
    di[Gen1Validator] = Gen1Validator()
    di["shelly-connector_api-gen-1-parser"] = di[Gen1Validator]

    di[Gen1Parser] = Gen1Parser(
        validator=di[Gen1Validator],
        devices_registry=di[DevicesRegistry],
        blocks_registry=di[BlocksRegistry],
        sensors_registry=di[SensorsRegistry],
    )
    di["shelly-connector_api-gen-1-parser"] = di[Gen1Parser]

    # Connector messages consumers
    di[DeviceDescriptionConsumer] = DeviceDescriptionConsumer(
        devices_registry=di[DevicesRegistry],
        properties_registry=di[PropertiesRegistry],
        blocks_registry=di[BlocksRegistry],
        sensors_registry=di[SensorsRegistry],
    )
    di["shelly-connector_device-description-consumer"] = di[DeviceDescriptionConsumer]

    di[DeviceFoundConsumer] = DeviceFoundConsumer(
        devices_registry=di[DevicesRegistry],
        properties_registry=di[PropertiesRegistry],
    )
    di["shelly-connector_device-found-consumer"] = di[DeviceFoundConsumer]

    di[DeviceStateConsumer] = DeviceStateConsumer(
        devices_registry=di[DevicesRegistry],
        properties_registry=di[PropertiesRegistry],
        blocks_registry=di[BlocksRegistry],
        sensors_registry=di[SensorsRegistry],
    )
    di["shelly-connector_device-state-consumer"] = di[DeviceStateConsumer]

    di[DeviceSettingsConsumer] = DeviceSettingsConsumer(
        devices_registry=di[DevicesRegistry],
    )
    di["shelly-connector_device-settings-consumer"] = di[DeviceSettingsConsumer]

    di[Consumer] = Consumer(
        consumers=[
            di[DeviceDescriptionConsumer],
            di[DeviceFoundConsumer],
            di[DeviceStateConsumer],
            di[DeviceSettingsConsumer],
        ],
        logger=connector_logger,
    )
    di["shelly-connector_consumers-proxy"] = di[Consumer]

    # Connector clients
    di[CoapClient] = CoapClient(
        validator=di[Gen1Validator],
        parser=di[Gen1Parser],
        consumer=di[Consumer],
        devices_registry=di[DevicesRegistry],
        logger=logger,
    )
    di["shelly-connector_coap-client"] = di[CoapClient]

    di[MdnsClient] = MdnsClient(consumer=di[Consumer], devices_registry=di[DevicesRegistry], logger=logger)
    di["shelly-connector_mdns-client"] = di[MdnsClient]

    di[HttpClient] = HttpClient(
        validator=di[Gen1Validator],
        parser=di[Gen1Parser],
        consumer=di[Consumer],
        devices_registry=di[DevicesRegistry],
        properties_registry=di[PropertiesRegistry],
        commands_registry=di[CommandsRegistry],
        blocks_registry=di[BlocksRegistry],
        sensors_registry=di[SensorsRegistry],
        logger=logger,
    )
    di["shelly-connector_http-client"] = di[HttpClient]

    di[Client] = Client(
        clients=[
            di[CoapClient],
            di[MdnsClient],
            di[HttpClient],
        ],
    )
    di["shelly-connector_clients-proxy"] = di[Client]

    # Inner events system
    di[EventsListener] = EventsListener(  # type: ignore[call-arg]
        connector_id=connector.id,
        event_dispatcher=di[EventDispatcher],
        logger=connector_logger,
    )
    di["shelly-connector_events-listener"] = di[EventsListener]

    # Main connector service
    connector_service = ShellyConnector(
        connector_id=connector.id,
        consumer=di[Consumer],
        devices_registry=di[DevicesRegistry],
        properties_registry=di[PropertiesRegistry],
        blocks_registry=di[BlocksRegistry],
        sensors_registry=di[SensorsRegistry],
        client=di[Client],
        events_listener=di[EventsListener],
        logger=connector_logger,
    )
    di[ShellyConnector] = connector_service
    di["shelly-connector_connector"] = connector_service

    return connector_service

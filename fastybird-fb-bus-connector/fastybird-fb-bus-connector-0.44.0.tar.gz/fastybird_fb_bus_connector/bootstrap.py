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
FastyBird BUS connector DI container
"""

# pylint: disable=no-value-for-parameter

# Python base dependencies
import logging

# Library dependencies
from kink import di
from whistle import EventDispatcher

# Library libs
from fastybird_fb_bus_connector.api.v1parser import V1Parser
from fastybird_fb_bus_connector.clients.apiv1 import ApiV1Client
from fastybird_fb_bus_connector.clients.client import Client
from fastybird_fb_bus_connector.connector import FbBusConnector
from fastybird_fb_bus_connector.consumers.consumer import Consumer
from fastybird_fb_bus_connector.consumers.device import (
    DeviceItemConsumer,
    DiscoveryConsumer,
    RegisterItemConsumer,
)
from fastybird_fb_bus_connector.entities import FbBusConnectorEntity
from fastybird_fb_bus_connector.events.listeners import EventsListener
from fastybird_fb_bus_connector.logger import Logger
from fastybird_fb_bus_connector.receivers.apiv1 import ApiV1Receiver
from fastybird_fb_bus_connector.receivers.receiver import Receiver
from fastybird_fb_bus_connector.registry.model import (
    DevicesAttributesRegistry,
    DevicesRegistry,
    DiscoveredDevicesRegistry,
    DiscoveredRegistersRegistry,
    RegistersRegistry,
)
from fastybird_fb_bus_connector.transporters.pjon import PjonTransporter
from fastybird_fb_bus_connector.types import ProtocolVersion


def create_connector(  # pylint: disable=too-many-statements
    connector: FbBusConnectorEntity,
    logger: logging.Logger = logging.getLogger("dummy"),
) -> FbBusConnector:
    """Create FB BUS connector services"""
    if isinstance(logger, logging.Logger):
        connector_logger = Logger(connector_id=connector.id, logger=logger)

        di[Logger] = connector_logger
        di["fb-bus-connector_logger"] = di[Logger]

    else:
        connector_logger = logger

    di[EventDispatcher] = EventDispatcher()
    di["fb-bus-connector_events-dispatcher"] = di[EventDispatcher]

    # Registers
    di[RegistersRegistry] = RegistersRegistry(event_dispatcher=di[EventDispatcher])  # type: ignore[call-arg]
    di["fb-bus-connector_registers-registry"] = di[RegistersRegistry]

    di[DevicesAttributesRegistry] = DevicesAttributesRegistry(event_dispatcher=di[EventDispatcher])
    di["fb-bus-connector_attributes-registry"] = di[DevicesAttributesRegistry]

    di[DevicesRegistry] = DevicesRegistry(
        registers_registry=di[RegistersRegistry],
        attributes_registry=di[DevicesAttributesRegistry],
        event_dispatcher=di[EventDispatcher],
    )
    di["fb-bus-connector_devices-registry"] = di[DevicesRegistry]

    di[DiscoveredRegistersRegistry] = DiscoveredRegistersRegistry(logger=logger)
    di["fb-bus-connector_registers-registry"] = di[DiscoveredRegistersRegistry]

    di[DiscoveredDevicesRegistry] = DiscoveredDevicesRegistry(
        registers_registry=di[DiscoveredRegistersRegistry],
        devices_registry=di[DevicesRegistry],
        logger=logger,
    )
    di["fb-bus-connector_registers-registry"] = di[DiscoveredDevicesRegistry]

    # API utils
    if connector.protocol == ProtocolVersion.V1:
        di[V1Parser] = V1Parser(
            devices_registry=di[DevicesRegistry],
            registers_registry=di[RegistersRegistry],
        )
        di["fb-bus-connector_api-v1-parser"] = di[V1Parser]

    # Messages consumers
    di[DeviceItemConsumer] = DeviceItemConsumer(devices_registry=di[DevicesRegistry], logger=connector_logger)
    di["fb-bus-connector_device-receiver"] = di[DeviceItemConsumer]

    di[RegisterItemConsumer] = RegisterItemConsumer(
        devices_registry=di[DevicesRegistry],
        registers_registry=di[RegistersRegistry],
        logger=connector_logger,
    )
    di["fb-bus-connector_registers-consumer"] = di[RegisterItemConsumer]

    di[DiscoveryConsumer] = DiscoveryConsumer(
        discovered_devices_registry=di[DiscoveredDevicesRegistry],
        discovered_registers_registry=di[DiscoveredRegistersRegistry],
    )
    di["fb-bus-connector_discovery-consumer"] = di[DiscoveryConsumer]

    di[Consumer] = Consumer(
        consumers=[
            di[RegisterItemConsumer],
            di[DeviceItemConsumer],
            di[DiscoveryConsumer],
        ],
        logger=connector_logger,
    )
    di["fb-bus-connector_consumer-proxy"] = di[Consumer]

    # Communication receivers
    receivers = []

    if connector.protocol == ProtocolVersion.V1:
        di[ApiV1Receiver] = ApiV1Receiver(parser=di[V1Parser])
        di["fb-bus-connector_api-v1-receiver"] = di[ApiV1Receiver]

        receivers.append(di[ApiV1Receiver])

    di[Receiver] = Receiver(
        receivers=receivers,
        consumer=di[Consumer],
        logger=connector_logger,
    )
    di["fb-bus-connector_receiver-proxy"] = di[Receiver]

    # Communication transporter
    di[PjonTransporter] = PjonTransporter(
        receiver=di[Receiver],
        address=connector.address,
        baud_rate=connector.baud_rate,
        interface=connector.interface,
        logger=connector_logger,
    )
    di["fb-bus-connector_data-transporter"] = di[PjonTransporter]

    # Data clients
    clients = []

    if connector.protocol == ProtocolVersion.V1:
        di[ApiV1Client] = ApiV1Client(
            devices_registry=di[DevicesRegistry],
            devices_attributes_registry=di[DevicesAttributesRegistry],
            registers_registry=di[RegistersRegistry],
            discovered_devices_registry=di[DiscoveredDevicesRegistry],
            discovered_registers_registry=di[DiscoveredRegistersRegistry],
            transporter=di[PjonTransporter],
            logger=connector_logger,
        )
        di["fb-bus-connector_api-v1-client"] = di[ApiV1Client]

        clients.append(di[ApiV1Client])

    di[Client] = Client(
        clients=clients,
    )
    di["fb-bus-connector_client-proxy"] = di[Client]

    # Inner events system
    di[EventsListener] = EventsListener(  # type: ignore[call-arg]
        connector_id=connector.id,
        event_dispatcher=di[EventDispatcher],
        logger=connector_logger,
    )
    di["fb-bus-connector_events-listener"] = di[EventsListener]

    # Main connector service
    connector_service = FbBusConnector(
        connector_id=connector.id,
        consumer=di[Consumer],
        client=di[Client],
        devices_registry=di[DevicesRegistry],
        registers_registry=di[RegistersRegistry],
        devices_attributes_registry=di[DevicesAttributesRegistry],
        transporter=di[PjonTransporter],
        events_listener=di[EventsListener],
        logger=connector_logger,
    )
    di[FbBusConnector] = connector_service
    di["fb-bus-connector_connector"] = connector_service

    return connector_service

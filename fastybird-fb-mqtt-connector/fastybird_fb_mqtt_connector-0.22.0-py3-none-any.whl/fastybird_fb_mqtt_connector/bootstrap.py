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
FastyBird MQTT connector DI container
"""

# pylint: disable=no-value-for-parameter

# Python base dependencies
import logging

# Library dependencies
from typing import Optional

from kink import di
from whistle import EventDispatcher

# Library libs
from fastybird_fb_mqtt_connector.clients.apiv1 import ApiV1Client
from fastybird_fb_mqtt_connector.clients.client import IClient
from fastybird_fb_mqtt_connector.connector import FbMqttConnector
from fastybird_fb_mqtt_connector.consumers.channel import ChannelAttributeItemConsumer
from fastybird_fb_mqtt_connector.consumers.consumer import Consumer
from fastybird_fb_mqtt_connector.consumers.device import DeviceAttributeItemConsumer
from fastybird_fb_mqtt_connector.consumers.extension import DeviceExtensionItemConsumer
from fastybird_fb_mqtt_connector.consumers.property import (
    ChannelPropertyItemConsumer,
    DevicePropertyItemConsumer,
)
from fastybird_fb_mqtt_connector.entities import (  # pylint: disable=unused-import
    FbMqttConnectorEntity,
    FbMqttDeviceEntity,
)
from fastybird_fb_mqtt_connector.events.listeners import EventsListener
from fastybird_fb_mqtt_connector.logger import Logger
from fastybird_fb_mqtt_connector.registry.model import (
    ChannelsPropertiesRegistry,
    ChannelsRegistry,
    DevicesAttributesRegistry,
    DevicesPropertiesRegistry,
    DevicesRegistry,
)
from fastybird_fb_mqtt_connector.subscriptions.repository import SubscriptionsRepository
from fastybird_fb_mqtt_connector.types import ProtocolVersion


def create_connector(
    connector: FbMqttConnectorEntity,
    logger: logging.Logger = logging.getLogger("dummy"),
) -> FbMqttConnector:
    """Create FB MQTT connector services"""
    if isinstance(logger, logging.Logger):
        connector_logger = Logger(connector_id=connector.id, logger=logger)

        di[Logger] = connector_logger
        di["fb-mqtt-connector_logger"] = di[Logger]

    else:
        connector_logger = logger

    di[EventDispatcher] = EventDispatcher()
    di["fb-mqtt-connector_events-dispatcher"] = di[EventDispatcher]

    # Registers
    di[DevicesPropertiesRegistry] = DevicesPropertiesRegistry(  # type: ignore[call-arg]
        event_dispatcher=di[EventDispatcher],
    )
    di["fb-mqtt-connector_devices-properties-registry"] = di[DevicesPropertiesRegistry]

    di[DevicesAttributesRegistry] = DevicesAttributesRegistry(
        event_dispatcher=di[EventDispatcher],
    )
    di["fb-mqtt-connector_devices-attributes-registry"] = di[DevicesAttributesRegistry]

    di[ChannelsPropertiesRegistry] = ChannelsPropertiesRegistry(  # type: ignore[call-arg]
        event_dispatcher=di[EventDispatcher],
    )
    di["fb-mqtt-connector_channels-properties-registry"] = di[ChannelsPropertiesRegistry]

    di[ChannelsRegistry] = ChannelsRegistry(
        properties_registry=di[ChannelsPropertiesRegistry],
        event_dispatcher=di[EventDispatcher],
    )
    di["fb-mqtt-connector_channels-registry"] = di[ChannelsRegistry]

    di[DevicesRegistry] = DevicesRegistry(
        properties_registry=di[DevicesPropertiesRegistry],
        attributes_registry=di[DevicesAttributesRegistry],
        channels_registry=di[ChannelsRegistry],
        event_dispatcher=di[EventDispatcher],
    )
    di["fb-mqtt-connector_devices-registry"] = di[DevicesRegistry]

    # MQTT topics
    di[SubscriptionsRepository] = SubscriptionsRepository()
    di["fb-mqtt-connector_subscription-repository"] = di[SubscriptionsRepository]

    # Messages consumers
    di[DeviceAttributeItemConsumer] = DeviceAttributeItemConsumer(
        devices_registry=di[DevicesRegistry],
        attributes_registry=di[DevicesAttributesRegistry],
        properties_registry=di[DevicesPropertiesRegistry],
        channels_registry=di[ChannelsRegistry],
        logger=connector_logger,
    )
    di["fb-bus-connector_device-attribute-consumer"] = di[DeviceAttributeItemConsumer]

    di[DeviceExtensionItemConsumer] = DeviceExtensionItemConsumer(
        devices_registry=di[DevicesRegistry],
        attributes_registry=di[DevicesAttributesRegistry],
        logger=connector_logger,
    )
    di["fb-bus-connector_extension-consumer"] = di[DeviceExtensionItemConsumer]

    di[ChannelAttributeItemConsumer] = ChannelAttributeItemConsumer(
        devices_registry=di[DevicesRegistry],
        channels_registry=di[ChannelsRegistry],
        properties_registry=di[ChannelsPropertiesRegistry],
        logger=connector_logger,
    )
    di["fb-bus-connector_channel-attribute-consumer"] = di[ChannelAttributeItemConsumer]

    di[DevicePropertyItemConsumer] = DevicePropertyItemConsumer(
        devices_registry=di[DevicesRegistry],
        properties_registry=di[DevicesPropertiesRegistry],
        logger=connector_logger,
    )
    di["fb-bus-connector_device-property-consumer"] = di[DevicePropertyItemConsumer]

    di[ChannelPropertyItemConsumer] = ChannelPropertyItemConsumer(
        devices_registry=di[DevicesRegistry],
        channels_registry=di[ChannelsRegistry],
        properties_registry=di[ChannelsPropertiesRegistry],
        logger=connector_logger,
    )
    di["fb-bus-connector_channel-property-consumer"] = di[ChannelPropertyItemConsumer]

    di[Consumer] = Consumer(
        consumers=[
            di[DeviceAttributeItemConsumer],
            di[DeviceExtensionItemConsumer],
            di[ChannelAttributeItemConsumer],
            di[DevicePropertyItemConsumer],
            di[ChannelPropertyItemConsumer],
        ],
        logger=connector_logger,
    )
    di["fb-mqtt-connector_consumer-proxy"] = di[Consumer]

    # Data clients
    client: Optional[IClient] = None

    if connector.protocol == ProtocolVersion.V1:
        di[ApiV1Client] = ApiV1Client(
            connector_id=connector.id,
            server_host=connector.server,
            server_port=connector.port,
            server_username=connector.username,
            server_password=connector.password,
            devices_registry=di[DevicesRegistry],
            devices_properties_registry=di[DevicesPropertiesRegistry],
            channels_registry=di[ChannelsRegistry],
            channels_properties_registry=di[ChannelsPropertiesRegistry],
            subscriptions_repository=di[SubscriptionsRepository],
            consumer=di[Consumer],
            logger=connector_logger,
        )
        di["fb-mqtt-connector_client_api_v1"] = di[ApiV1Client]

        client = di[ApiV1Client]

    # Inner events system
    di[EventsListener] = EventsListener(  # type: ignore[call-arg]
        event_dispatcher=di[EventDispatcher],
        logger=connector_logger,
    )
    di["fb-mqtt-connector_events-listener"] = di[EventsListener]

    # Main connector service
    connector_service = FbMqttConnector(
        connector_id=connector.id,
        consumer=di[Consumer],
        client=client,
        devices_registry=di[DevicesRegistry],
        devices_properties_registry=di[DevicesPropertiesRegistry],
        devices_attributes_registry=di[DevicesAttributesRegistry],
        channels_registry=di[ChannelsRegistry],
        channels_properties_registry=di[ChannelsPropertiesRegistry],
        events_listener=di[EventsListener],
        logger=connector_logger,
    )
    di[FbMqttConnector] = connector_service
    di["fb-mqtt-connector_connector"] = connector_service

    return connector_service

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
FastyBird MQTT connector clients module client for API v1
"""

# Python base dependencies
import logging
import re
import uuid
from typing import List, Optional, Union

# Library dependencies
from fastybird_metadata.devices_module import DevicePropertyName
from paho.mqtt.client import MQTT_ERR_SUCCESS, Client, MQTTMessage

# Library libs
from fastybird_fb_mqtt_connector.api.v1builder import V1Builder
from fastybird_fb_mqtt_connector.api.v1parser import V1Parser
from fastybird_fb_mqtt_connector.api.v1validator import V1Validator
from fastybird_fb_mqtt_connector.clients.client import IClient
from fastybird_fb_mqtt_connector.consumers.consumer import Consumer
from fastybird_fb_mqtt_connector.consumers.entities import DevicePropertyEntity
from fastybird_fb_mqtt_connector.exceptions import ParsePayloadException
from fastybird_fb_mqtt_connector.logger import Logger
from fastybird_fb_mqtt_connector.registry.model import (
    ChannelsPropertiesRegistry,
    ChannelsRegistry,
    DevicesPropertiesRegistry,
    DevicesRegistry,
)
from fastybird_fb_mqtt_connector.registry.records import DeviceRecord
from fastybird_fb_mqtt_connector.subscriptions.repository import SubscriptionsRepository


class ApiV1Client(Client, IClient):  # pylint: disable=too-many-instance-attributes
    """
    FastyBird MQTT API v1 client

    @package        FastyBird:FbMqttConnector!
    @module         clients/apiv1

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __server_host: str = "localhost"
    __server_port: int = 1883
    __server_username: Optional[str] = None
    __server_password: Optional[str] = None

    __devices_registry: DevicesRegistry
    __devices_properties_registry: DevicesPropertiesRegistry
    __channels_registry: ChannelsRegistry
    __channels_properties_registry: ChannelsPropertiesRegistry

    __subscriptions_repository: SubscriptionsRepository
    __consumer: Consumer

    __processed_devices: List[str] = []

    __logger: Union[Logger, logging.Logger]

    __API_TOPICS: List[str] = [
        "/fb/v1/+/+",
        "/fb/v1/+/+/+",
        "/fb/v1/+/+/+/+",
        "/fb/v1/+/+/+/+/+",
        "/fb/v1/+/+/+/+/+/+",
        "/fb/v1/+/+/+/+/+/+/+",
    ]

    __COMMON_TOPICS: List[str] = [
        "$SYS/broker/log/#",
    ]

    __SYS_TOPIC_REGEX = r"^\$SYS\/broker\/log\/([a-zA-Z0-9]+)?"
    __NEW_CLIENT_MESSAGE_PAYLOAD = "New client connected from"

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        connector_id: uuid.UUID,
        server_host: str,
        server_port: int,
        server_username: Optional[str],
        server_password: Optional[str],
        devices_registry: DevicesRegistry,
        devices_properties_registry: DevicesPropertiesRegistry,
        channels_registry: ChannelsRegistry,
        channels_properties_registry: ChannelsPropertiesRegistry,
        subscriptions_repository: SubscriptionsRepository,
        consumer: Consumer,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        super().__init__(client_id=connector_id.__str__())

        # Set up external MQTT broker callbacks
        self.on_connect = lambda client, userdata, flags, response_code: self.__on_connect()
        self.on_disconnect = lambda client, userdata, response_code: self.__on_disconnect()
        self.on_subscribe = lambda client, userdata, message_id, granted_qos: self.__on_subscribe(message_id=message_id)
        self.on_unsubscribe = lambda client, userdata, message_id: self.__on_unsubscribe(message_id=message_id)
        self.on_message = lambda client, userdata, message: self.__on_message(message=message)

        self.__server_host = server_host
        self.__server_port = server_port
        self.__server_username = server_username
        self.__server_password = server_password

        self.__devices_registry = devices_registry
        self.__devices_properties_registry = devices_properties_registry
        self.__channels_registry = channels_registry
        self.__channels_properties_registry = channels_properties_registry

        self.__subscriptions_repository = subscriptions_repository
        self.__consumer = consumer

        self.__processed_devices = []

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def start(self) -> None:
        """Start communication"""
        if self.__server_username is not None:
            self.username_pw_set(username=self.__server_username, password=self.__server_password)

        self.connect(
            host=self.__server_host,
            port=self.__server_port,
        )

        self.loop_start()

    # -----------------------------------------------------------------------------

    def stop(self) -> None:
        """Stop communication"""
        self.loop_stop()

        self.disconnect()

    # -----------------------------------------------------------------------------

    def handle(self) -> None:
        """Handle connector devices"""
        for device in self.__devices_registry:
            if device.id.__str__() not in self.__processed_devices:
                self.__process_device(device=device)

                self.__processed_devices.append(device.id.__str__())

                return

        self.__processed_devices = []

    # -----------------------------------------------------------------------------

    def __on_connect(self) -> None:
        """On connection to broker established event"""
        self.__logger.info("Connected to MQTT broker")

        for topic in self.__COMMON_TOPICS:
            result, message_id = self.subscribe(topic=topic, qos=0)

            if result == MQTT_ERR_SUCCESS and message_id is not None:
                self.__subscriptions_repository.create(topic=topic, qos=0, mid=message_id)

        for topic in self.__API_TOPICS:
            result, message_id = self.subscribe(topic=topic, qos=0)

            if result == MQTT_ERR_SUCCESS and message_id is not None:
                self.__subscriptions_repository.create(topic=topic, qos=0, mid=message_id)

    # -----------------------------------------------------------------------------

    def __on_disconnect(self) -> None:
        """On connection to broker closed event"""
        self.__logger.info("Disconnected from MQTT broker")

    # -----------------------------------------------------------------------------

    def __on_subscribe(self, message_id: int) -> None:
        """On topic subscribed event"""
        subscription = self.__subscriptions_repository.get_by_id(mid=message_id)

        if subscription is not None:
            self.__logger.info("Subscribed to topic: %s", subscription.topic)

        else:
            self.__logger.warning("Subscribed to unknown topic")

    # -----------------------------------------------------------------------------

    def __on_unsubscribe(self, message_id: int) -> None:
        """On topic unsubscribed event"""
        subscription = self.__subscriptions_repository.get_by_id(mid=message_id)

        if subscription is not None:
            self.__subscriptions_repository.delete(subscription=subscription)

            self.__logger.info("Unsubscribed from topic: %s", subscription.topic)

        else:
            self.__logger.warning("Unsubscribed from unknown topic")

    # -----------------------------------------------------------------------------

    def __on_message(self, message: MQTTMessage) -> None:  # pylint: disable=too-many-branches
        """On broker message event"""
        payload = message.payload.decode("utf-8", "ignore")

        if len(re.findall(self.__SYS_TOPIC_REGEX, message.topic)) == 1:
            result: List[tuple] = re.findall(self.__SYS_TOPIC_REGEX, message.topic)
            log_level = str(result.pop()).lower()

            if log_level == "n":
                self.__logger.info(payload)

                if self.__NEW_CLIENT_MESSAGE_PAYLOAD in payload:
                    payload_parts = payload.split(",")

                    try:
                        ip_address: Optional[str] = payload_parts[5]

                    except IndexError:
                        ip_address = None

                    try:
                        device_id: Optional[str] = payload_parts[7]

                    except IndexError:
                        device_id = None

                    try:
                        username: Optional[str] = payload_parts[10]

                    except IndexError:
                        username = None

                    if ip_address and device_id and username:
                        entity = DevicePropertyEntity(
                            device=device_id,
                            name=DevicePropertyName.IP_ADDRESS.value,
                        )
                        entity.value = ip_address

                        self.__consumer.append(entity=entity)

            elif log_level == "e":
                self.__logger.error(payload)

            elif log_level == "i":
                self.__logger.info(payload)

            else:
                self.__logger.debug(payload)

            return

        if (
            V1Validator.validate_convention(message.topic) is False
            or V1Validator.validate_version(message.topic) is False
            or V1Validator.validate_is_command(message.topic) is True
        ):
            return

        if V1Validator.validate(message.topic) is False:
            self.__logger.warning(
                "Received topic is not valid MQTT v1 convention topic: %s",
                message.topic,
            )

            return

        try:
            self.__consumer.append(
                entity=V1Parser.parse_message(
                    topic=message.topic,
                    payload=payload,
                    retained=message.retain,
                ),
            )

        except ParsePayloadException as ex:
            self.__logger.error(
                "Received message could not be successfully parsed to entity",
                extra={
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )

            return

        except AttributeError as ex:
            self.__logger.error(
                "One or more parsed values from message are not valid",
                extra={
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )

            return

    # -----------------------------------------------------------------------------

    def __process_device(self, device: DeviceRecord) -> None:
        if self.__write_device_properties_handler(device=device):
            return

        if self.__write_channel_properties_handler(device=device):
            return

    # -----------------------------------------------------------------------------

    def __write_device_properties_handler(self, device: DeviceRecord) -> bool:
        device_properties = self.__devices_properties_registry.get_all_for_device(device_id=device.id)

        for device_property in device_properties:
            if device_property.expected_value is not None and device_property.expected_pending is None:
                if self.__publish(
                    topic=V1Builder.build_device_property(
                        device=device.identifier,
                        identifier=device_property.identifier,
                    ),
                    payload=str(device_property.expected_value),
                ):
                    return True

        return False

    # -----------------------------------------------------------------------------

    def __write_channel_properties_handler(self, device: DeviceRecord) -> bool:
        channels = self.__channels_registry.get_all_by_device(device_id=device.id)

        for channel in channels:
            channel_properties = self.__channels_properties_registry.get_all_for_channel(channel_id=channel.id)

            for channel_property in channel_properties:
                if channel_property.expected_value is not None and channel_property.expected_pending is None:
                    if self.__publish(
                        topic=V1Builder.build_channel_property(
                            device=device.identifier,
                            channel=channel.identifier,
                            identifier=channel_property.identifier,
                        ),
                        payload=str(channel_property.expected_value),
                    ):
                        return True

        return False

    # -----------------------------------------------------------------------------

    def __publish(self, topic: str, payload: str, qos: int = 0) -> bool:
        """Send message to broker"""
        if not self.is_connected():
            return False

        result = self.publish(topic=topic, payload=payload, qos=qos)

        if result.rc != 0:
            return False

        return True

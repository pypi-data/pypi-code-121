"""MQTT Daemon Base."""
import asyncio
import logging
import os
import signal
import uuid
from types import FrameType
from typing import Any, Optional

import paho.mqtt.client as mqtt

from mqtt_hass_base.error import MQTTHassBaseError


class MqttClientDaemon:
    """Mqtt device base class."""

    mqtt_port: int = -1
    mqtt_client: mqtt.Client
    mqtt_discovery_root_topic: str
    mqtt_data_root_topic: str

    def __init__(
        self,
        name: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        mqtt_discovery_root_topic: Optional[str] = None,
        mqtt_data_root_topic: Optional[str] = None,
        log_level: Optional[str] = None,
        first_connection_timeout: int = 10,
    ):
        """Create new MQTT daemon."""
        if name:
            self.name = name
        else:
            self.name = os.environ.get("MQTT_NAME", "mqtt-device-" + str(uuid.uuid1()))
        self.must_run = False
        self.mqtt_connected = False
        # mqtt
        self.mqtt_host = host
        if port:
            self.mqtt_port = port
        self.mqtt_username = username
        self.mqtt_password = password
        self.log_level = log_level
        self._first_connection_timeout = first_connection_timeout
        # Get logger
        self.logger = self._get_logger()
        self.logger.info("Initializing...")
        self.read_base_config(mqtt_discovery_root_topic, mqtt_data_root_topic)
        self.read_config()

    def _get_logger(self) -> logging.Logger:
        """Build logger."""
        logging_level = logging.DEBUG
        logger = logging.getLogger(name=self.name)
        logger.setLevel(logging_level)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger

    def read_config(self) -> None:
        """Read configuration."""
        raise NotImplementedError

    def read_base_config(
        self,
        mqtt_discovery_root_topic: Optional[str],
        mqtt_data_root_topic: Optional[str],
    ) -> None:
        """Read base configuration from env vars."""
        if self.mqtt_username is None:
            self.mqtt_username = os.environ.get("MQTT_USERNAME", None)
        if self.mqtt_password is None:
            self.mqtt_password = os.environ.get("MQTT_PASSWORD", None)
        if self.mqtt_host is None:
            self.mqtt_host = os.environ.get("MQTT_HOST", "127.0.0.1")
        if self.mqtt_port is None or self.mqtt_port <= 0:
            try:
                self.mqtt_port = int(os.environ.get("MQTT_PORT", 1883))
            except ValueError as exp:
                self.logger.critical("Bad MQTT port")
                raise ValueError from exp
            if self.mqtt_port <= 0:
                self.logger.critical("Bad MQTT port")
                raise ValueError("Bad MQTT port")
        if mqtt_discovery_root_topic is None:
            self.mqtt_discovery_root_topic = os.environ.get(
                "MQTT_DISCOVERY_ROOT_TOPIC",
                os.environ.get("ROOT_TOPIC", "homeassistant"),
            )
        else:
            self.mqtt_discovery_root_topic = mqtt_discovery_root_topic
        if mqtt_data_root_topic is None:
            self.mqtt_data_root_topic = os.environ.get(
                "MQTT_DATA_ROOT_TOPIC", "homeassistant"
            )
        else:
            self.mqtt_data_root_topic = mqtt_data_root_topic
        if self.log_level is None:
            self.log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
        self.logger.setLevel(getattr(logging, self.log_level.upper()))

    async def _mqtt_connect(self) -> mqtt.Client:
        """Connecto to the MQTT server."""
        self.logger.info("Connecting to MQTT server")
        client = mqtt.Client(client_id=self.name)
        if None not in (self.mqtt_username, self.mqtt_password):
            client.username_pw_set(self.mqtt_username, self.mqtt_password)

        client.on_message = self._base_on_message
        client.on_connect = self._base_on_connect
        client.on_disconnect = self._base_on_disconnect
        client.on_publish = self._base_on_publish

        client.connect_async(self.mqtt_host, self.mqtt_port, keepalive=60)
        self.logger.info("Reaching MQTT server")
        client.loop_start()  # type: ignore[no-untyped-call]
        return client

    def _base_on_connect(
        self,
        client: mqtt.Client,
        userdata: Optional[dict[str, Any]],
        flags: dict[str, Any],
        rc: int,  # pylint: disable=invalid-name
    ) -> None:  # pylint: disable=W0613
        """MQTT on_connect callback."""
        self.logger.debug("Connected to MQTT server with result code %s", str(rc))
        self.mqtt_connected = True

        self._on_connect(client, userdata, flags, rc)
        self._mqtt_subscribe(client, userdata, flags, rc)
        self.logger.debug("Subscribing done")

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Optional[dict[str, Any]],
        flags: dict[str, Any],
        rc: int,  # pylint: disable=invalid-name
    ) -> None:
        """On connect callback method."""
        raise NotImplementedError

    def _base_on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Optional[dict[str, Any]],
        rc: int,  # pylint: disable=invalid-name
    ) -> None:  # pylint: disable=W0613
        """MQTT on_disconnect callback."""
        self.logger.debug("Disconnected from MQTT server with result code %s", str(rc))
        self.mqtt_connected = False

        self._on_disconnect(client, userdata, rc)
        self.logger.debug("Disconnection done")

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Optional[dict[str, Any]],
        rc: int,  # pylint: disable=invalid-name
    ) -> None:
        """On disconnect callback method."""
        raise NotImplementedError

    def _mqtt_subscribe(
        self,
        client: mqtt.Client,
        userdata: Optional[dict[str, Any]],
        flags: dict[str, Any],
        rc: int,  # pylint: disable=invalid-name
    ) -> None:
        """Define which topic to subscribes.

        Called after on_connect callback.
        """
        raise NotImplementedError

    def _base_on_message(
        self,
        client: mqtt.Client,
        userdata: Optional[dict[str, Any]],
        msg: mqtt.MQTTMessage,
    ) -> None:
        """MQTT on_message callback."""
        self.logger.info("Message received: %s %s", msg.topic, str(msg.payload))
        self._on_message(client, userdata, msg)

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: Optional[dict[str, Any]],
        msg: mqtt.MQTTMessage,
    ) -> None:
        """On Message callback."""
        raise NotImplementedError

    def _base_on_publish(
        self, client: mqtt.Client, userdata: Optional[dict[str, Any]], mid: int
    ) -> None:
        """On publish base callback."""
        self.logger.debug("PUBLISH")
        self._on_publish(client, userdata, mid)

    def _on_publish(
        self, client: mqtt.Client, userdata: Optional[dict[str, Any]], mid: int
    ) -> None:
        """On publish callback."""
        raise NotImplementedError

    def _base_signal_handler(self, signal_: int, frame: FrameType) -> None:
        """Signal handler."""
        self.logger.info("SIGINT received")
        self.logger.debug("Signal %s in frame %s received", signal_, frame)
        self.must_run = False
        self._signal_handler(signal_, frame)
        self.logger.info("Exiting...")

    async def _set_devices_mqtt_client(self) -> None:
        """Set mqtt_client to all devices.

        Use this method to call the `set_mqtt_client` Device class method on
        all devices objects.
        """
        raise NotImplementedError

    async def async_run(self) -> None:
        """Run main base loop."""
        self.logger.info("Start main process")
        self.must_run = True
        # Add signal handler
        signal.signal(signal.SIGINT, self._base_signal_handler)  # type: ignore[arg-type]
        # Mqtt client
        self.mqtt_client = await self._mqtt_connect()
        await self._set_devices_mqtt_client()

        # Ensure we are connected at the first run of the main loop
        timeout = self._first_connection_timeout
        if timeout is not None:
            while not self.mqtt_client.is_connected():  # type: ignore[no-untyped-call]
                self.logger.info("Waiting for the connection to the mqtt server.")
                await asyncio.sleep(1)
                if timeout == 0:
                    msg = "Mqtt connection timed out. Exiting..."
                    self.logger.error(msg)
                    raise MQTTHassBaseError(msg)
                timeout -= 1

        await self._init_main_loop()

        while self.must_run:
            self.logger.debug("We are in the main loop")
            await self._main_loop()
            if (
                not self.mqtt_client.is_connected()  # type: ignore[no-untyped-call]
                or not self.mqtt_connected
            ):
                self.logger.error("Mqtt not connected, please check you configuration.")

        self.logger.info("Main loop stopped")
        await self._loop_stopped()
        self.logger.info("Closing MQTT client")
        self.mqtt_client.disconnect()
        self.mqtt_client.loop_stop()

    def _signal_handler(self, signal_: int, frame: FrameType) -> None:
        """System signal callback to handle KILLSIG."""
        raise NotImplementedError

    async def _init_main_loop(self) -> None:
        """Init method called just before the start of the main loop."""
        raise NotImplementedError

    async def _main_loop(self) -> None:
        """Run main loop.

        This method is recalled at each iteration.
        """
        raise NotImplementedError

    async def _loop_stopped(self) -> None:
        """Run after main loop is stopped."""
        raise NotImplementedError

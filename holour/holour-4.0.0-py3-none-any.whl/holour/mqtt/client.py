import paho.mqtt.client as mqtt
import logging
import time
import socket

from holour import json_encode
from holour.msg import Status
from holour.mqtt.config import MQTTConfig


class MQTTClient:

    def __init__(self, name: str, mqtt_config: MQTTConfig, log_level=logging.INFO):
        self.log = logging.getLogger(name)
        self.log.setLevel(log_level)

        self.log.info(f"Setting up MQTT client...")
        self.ip = self._get_own_ip()
        self.connected = False
        self.mqtt_config = mqtt_config
        self.mqtt_client = mqtt.Client(client_id=mqtt_config.client_id)
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_disconnect = self._on_disconnect
        self.mqtt_client.on_message = self._on_message
        self.mqtt_client.will_set(self._status_topic(), self._status_payload(online=False), qos=2, retain=True)
        self.log.info("MQTT client setup is completed")

    def _get_own_ip(self) -> str:
        self.log.info("Retrieving own ip...")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip, port = s.getsockname()
        s.close()
        self.log.info(f"Running on: {ip}")
        return ip

    def _status_topic(self) -> str:
        return f'{self.mqtt_config.prefix}/status/{self.mqtt_config.client_id}'

    def _status_payload(self, online: bool) -> str:
        status = 'online' if online else 'offline'
        return json_encode(Status(self.mqtt_config.client_id, self.ip, status))

    def _connect(self):
        self.log.info(f"Connecting to MQTT broker on: {self.mqtt_config.address}:{self.mqtt_config.port}...")
        self.mqtt_client.connect(host=self.mqtt_config.address,
                                 port=self.mqtt_config.port,
                                 keepalive=self.mqtt_config.keep_alive)
        self.mqtt_client.loop_start()

    def _on_connect(self, client: mqtt.Client, userdata, flags, rc: int):
        self.log.info(f"Connected with result code: {rc}")
        self.connected = True
        client.publish(self._status_topic(), self._status_payload(online=True), qos=2, retain=True)

    def _on_disconnect(self, client: mqtt.Client, userdata, rc: int):
        self.log.info(f"Disconnected from MQTT-server")
        self.connected = False
        client.publish(self._status_topic(), self._status_payload(online=False), qos=2, retain=True)

    def _on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        raise NotImplementedError()

    def _wait_for_keyboard_interrupt(self):
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            self.mqtt_client.loop_stop()
            self.log.info("Bye bye")

import threading
from collections import namedtuple
from typing import Dict, List, Optional, Union

from paho.mqtt.client import MQTTMessage

from worker_bunch.mqtt.mqtt_client import MqttClient
from worker_bunch.service_config import ConfigException
from worker_bunch.utils.json_utils import JsonUtils

ProxyMessage = namedtuple("ProxyMessage", ["topic", "payload", "retain"])


class MqttProxy:

    def __init__(self, mqtt_client: Optional[MqttClient]):

        self._mqtt_client = mqtt_client
        self._lock = threading.Lock()

        self._messages: List[ProxyMessage] = []

    def close(self):
        self.publish()
        self._mqtt_client = None

    def connect(self):
        with self._lock:
            if self._mqtt_client:
                self._mqtt_client.connect()

    def is_connected(self):
        with self._lock:
            if self._mqtt_client:
                return self._mqtt_client.is_connected()
            else:
                return True  # hide missing mqtt client

    def ensure_connection(self):
        if self._mqtt_client:
            self._mqtt_client.ensure_connection()

    def set_last_will(self, topic: str, last_will: Union[str, Dict], retain: Optional[bool] = None):
        if not self._mqtt_client:
            raise ConfigException("no mqtt client configured!")

        if isinstance(last_will, dict):
            last_will = JsonUtils.dumps(last_will)

        with self._lock:
            if self._mqtt_client and topic and last_will:
                self._mqtt_client.set_last_will(topic=topic, last_will=last_will, retain=retain)

    def subscribe(self, topics: List[str]):
        if topics:
            if not self._mqtt_client:
                raise ConfigException("no mqtt client configured!")

            with self._lock:
                self._mqtt_client.subscribe(topics)

    def get_messages(self) -> List[MQTTMessage]:
        with self._lock:
            if self._mqtt_client:
                return self._mqtt_client.get_messages()
            else:
                return []

    def queue(self, topic: str, payload: Union[str, Dict], retain: Optional[bool] = None):
        if not self._mqtt_client:
            raise ConfigException("no mqtt client configured!")

        if isinstance(payload, dict):
            payload = JsonUtils.dumps(payload)

        with self._lock:
            self._messages.append(ProxyMessage(topic=topic, payload=payload, retain=retain))

    def publish(self):
        if self._mqtt_client:
            with self._lock:
                if self._mqtt_client:
                    messages = self._messages
                    self._messages = []
                    for m in messages:
                        self._mqtt_client.publish(topic=m.topic, payload=m.payload, retain=m.retain)

from enum import Enum
from typing import Dict, List

from attr import frozen
from paho.mqtt.client import MQTTMessage


class NotificationType(Enum):
    """means MESSAGE*"""

    ASTRAL = "ASTRAL"
    CRON = "CRON"
    JUST_STARTED = "JUST_STARTED"
    MQTT_MESSAGE = "MQTT_MESSAGE"
    SINGLE_STARTED = "SINGLE_STARTED"  # used to signal "DEBUG" to worker
    TIMER = "TIMER"


NT = NotificationType


@frozen
class Notification:

    type: NotificationType

    # contains the MQTT topic or timer key
    topic: str

    # payload is not part of key. it will be skipped if new notification for the same type a topic arrive.
    payload: str = None

    def __key(self):
        return self.type, self.topic

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__key() == other.__key()
        return NotImplemented

    @classmethod
    def ensure_string(cls, value_in) -> str:
        if isinstance(value_in, bytes):
            return value_in.decode("utf-8")

        return value_in

    @classmethod
    def create_from_mqtt(cls, mqtt_message: MQTTMessage):
        return Notification(
            type=NotificationType.MQTT_MESSAGE,
            topic=cls.ensure_string(mqtt_message.topic),
            payload=cls.ensure_string(mqtt_message.payload),
        )

    @classmethod
    def create_mqtt(cls, topic: str, payload: str):
        return Notification(type=NotificationType.MQTT_MESSAGE, topic=topic, payload=cls.ensure_string(payload))

    @classmethod
    def create_astral(cls, topic: str):
        return Notification(type=NotificationType.ASTRAL, topic=topic)

    @classmethod
    def create_timer(cls, topic: str):
        return Notification(type=NotificationType.TIMER, topic=topic)

    @classmethod
    def create_cron(cls, topic: str):
        return Notification(type=NotificationType.CRON, topic=topic)

    @classmethod
    def find(cls, notifications: List[any], ntype: NotificationType, topic: str = None):
        for notification in notifications:
            if notification.type == ntype and (topic is None or topic == notification.topic):
                return True

        return False


class NotificationBucket:

    def __init__(self):
        self._dict: Dict[Notification, Notification] = {}

    def __str__(self):
        return '{}'.format(self._dict)

    def __repr__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self._dict)

    def __bool__(self):
        return bool(self._dict)

    def __len__(self):
        return len(self._dict)

    def add(self, notification: Notification):
        if notification:
            self._dict[notification] = notification

    def clear(self):
        self._dict = {}

    def get_list(self):
        return list(self._dict.values())

    def get_set(self):
        return set(self._dict.values())

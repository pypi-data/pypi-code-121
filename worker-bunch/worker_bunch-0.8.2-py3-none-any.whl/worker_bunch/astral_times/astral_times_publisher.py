from typing import Dict, Optional, List

from worker_bunch.astral_times.astral_times_manager import AstralTimesManager
from worker_bunch.dispatcher import Dispatcher
from worker_bunch.notification import Notification, NotificationType
from worker_bunch.worker.worker import Worker, WorkerSetup


class AstralTimesPublisherConfKey:
    MQTT_TOPIC_OUT = "mqtt_topic_out"
    MQTT_LAST_WILL = "mqtt_last_will"
    MQTT_RETAIN = "mqtt_retain"


ASTRAL_TIMES_PUBLISHER_JSONSCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        AstralTimesPublisherConfKey.MQTT_LAST_WILL: {"type": "string", "minLength": 1, "description": "MQTT last will message"},
        AstralTimesPublisherConfKey.MQTT_RETAIN: {"type": "boolean", "description": "Make MQTT message persistent."},
        AstralTimesPublisherConfKey.MQTT_TOPIC_OUT: {"type": "string", "minLength": 1, "description": "MQTT topic to write to"},
    },
    "required": [AstralTimesPublisherConfKey.MQTT_TOPIC_OUT]
}


class AstralTimesPublisher(Worker):

    def __init__(self, name: str):
        super().__init__(name)

        self._mqtt_last_will = ""
        self._mqtt_retain = False
        self._mqtt_topic_out = []
        self._mqtt_topics_in = ""

        self._astral_time_manager: Optional[AstralTimesManager] = None

    def setup(self, props):
        super().setup(props)

        self._astral_time_manager = props[WorkerSetup.ASTRAL_TIME_MANAGER]

        self._mqtt_last_will = self._worker_settings.get(AstralTimesPublisherConfKey.MQTT_LAST_WILL)
        self._mqtt_retain = self._worker_settings.get(AstralTimesPublisherConfKey.MQTT_RETAIN, False)
        self._mqtt_topic_out = self._worker_settings[AstralTimesPublisherConfKey.MQTT_TOPIC_OUT]

    def get_partial_settings_schema(self) -> Dict[str, any]:
        return ASTRAL_TIMES_PUBLISHER_JSONSCHEMA

    def make_partial_settings_required(self) -> bool:
        return True

    def set_last_will(self):
        """Set the last will at mqtt client. Explicitly triggered before the mqtt client connects."""
        if self._mqtt_topic_out and self._mqtt_last_will:
            self._mqtt_proxy.set_last_will(self._mqtt_topic_out, self._mqtt_last_will)

    def subscribe_notifications(self, dispatcher: Dispatcher):
        dispatcher.subscribe_cron(self, "0 * * * *", "cron-every-hour")

    def _work(self, notifications: List[Notification]):
        found_message = next((n for n in notifications if n.type in [NotificationType.CRON, NotificationType.JUST_STARTED]), None)

        if found_message:
            if self._astral_time_manager:
                astral_times = self._astral_time_manager.get_astral_times()
                astral_times["status"] = "ok"
                self._mqtt_proxy.queue(topic=self._mqtt_topic_out, payload=astral_times, retain=self._mqtt_retain)
            else:
                self._final_work()

    def _final_work(self):
        """sends the last will"""
        if self._mqtt_topic_out and self._mqtt_last_will:
            self._mqtt_proxy.queue(self._mqtt_topic_out, self._mqtt_last_will, retain=self._mqtt_retain)

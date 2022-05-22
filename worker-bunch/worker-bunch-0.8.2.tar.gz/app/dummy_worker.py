from typing import Dict, List, Optional

import schedule

from worker_bunch.dispatcher import Dispatcher
from worker_bunch.notification import Notification
from worker_bunch.worker.worker import Worker, WorkerSetup


class DummyWorkerConfKey:
    MQTT_TOPICS_IN = "mqtt_topics_in"
    MQTT_TOPIC_OUT = "mqtt_topic_out"
    MQTT_LAST_WILL = "mqtt_last_will"
    MQTT_RETAIN = "mqtt_retain"


DUMMY_WORKER_JSONSCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        DummyWorkerConfKey.MQTT_LAST_WILL: {"type": "string", "minLength": 1, "description": "MQTT last will message"},
        DummyWorkerConfKey.MQTT_RETAIN: {"type": "boolean", "description": "Make MQTT message persistent."},
        DummyWorkerConfKey.MQTT_TOPIC_OUT: {"type": "string", "minLength": 1, "description": "MQTT topic to write to"},

        DummyWorkerConfKey.MQTT_TOPICS_IN: {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
            "description": "List of MQTT topics to read from"
        }
    },
    "required": [DummyWorkerConfKey.MQTT_TOPICS_IN, DummyWorkerConfKey.MQTT_TOPIC_OUT]
}


class DummyWorker(Worker):

    def __init__(self, name: str):
        super().__init__(name)

        self._mqtt_last_will = ""
        self._mqtt_retain = False
        self._mqtt_topic_out = []
        self._mqtt_topics_in = ""

    def setup(self, props: Dict[WorkerSetup, any]):
        super().setup(props)

        self._mqtt_last_will = self._worker_settings.get(DummyWorkerConfKey.MQTT_LAST_WILL)
        self._mqtt_retain = self._worker_settings.get(DummyWorkerConfKey.MQTT_RETAIN, False)
        self._mqtt_topic_out = self._worker_settings.get(DummyWorkerConfKey.MQTT_TOPIC_OUT)
        self._mqtt_topics_in = self._worker_settings.get(DummyWorkerConfKey.MQTT_TOPICS_IN, [])

    def get_partial_settings_schema(self) -> Optional[Dict[str, any]]:
        """returns a partial JSON schema for extra setting if needed. overwrite..."""
        return DUMMY_WORKER_JSONSCHEMA

    def make_partial_settings_required(self) -> bool:
        """return True to force existence via JSON schema validation. overwrite..."""
        return True

    def set_last_will(self):
        """Set the last will at mqtt client. Explicitly triggered before the mqtt client connects."""
        if self._mqtt_topic_out and self._mqtt_last_will:
            self._mqtt_proxy.set_last_will(self._mqtt_topic_out, self._mqtt_last_will)

    def subscribe_notifications(self, dispatcher: Dispatcher):

        timer_job = schedule.every(5).to(7).seconds  # type: schedule.Job
        dispatcher.subscribe_timer(self, timer_job, "keyword-timer")

        dispatcher.subscribe_cron(self, "* * * * *", "cron-every-minute")

        dispatcher.subscribe_mqtt_topics(self, self._mqtt_topics_in, 0.2)

        self._logger.info("subscribe")

    def _work(self, notifications: List[Notification]):
        for notification in notifications:
            self._logger.info("notified: %s", notification)

            message = f"dummy message: {notification.topic}"
            self._mqtt_proxy.queue(topic=self._mqtt_topic_out, payload=message, retain=self._mqtt_retain)

    def _final_work(self):
        """
        E.g.: You may send explicitly the last will(s) here (as a normal message). Kind of:
        ```
        if self._topic and self._last_will:
            self._mqtt_proxy.publish(self._topic, self._last_will)
        ```
        """
        if self._mqtt_topic_out and self._mqtt_last_will:
            self._mqtt_proxy.queue(self._mqtt_topic_out, self._mqtt_last_will, retain=self._mqtt_retain)

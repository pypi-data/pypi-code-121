import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

from worker_bunch.astral_times.astral_times_config import AstralTimesConfKey
from worker_bunch.astral_times.astral_times_manager import AstralTimesManager
from worker_bunch.astral_times.astral_times_publisher import AstralTimesPublisher, AstralTimesPublisherConfKey
from worker_bunch.dispatcher import Dispatcher
from worker_bunch.mqtt.mqtt_proxy import MqttProxy
from worker_bunch.notification import Notification
from worker_bunch.worker.worker import WorkerSetup


class TestAstralTimesPublisher(unittest.TestCase):

    DUMMY_CONFIG = {
        AstralTimesConfKey.LATITUDE: 51.051873,
        AstralTimesConfKey.LONGITUDE: 13.741522,
        AstralTimesConfKey.ELEVATION: 125,
    }

    SETTINGS = {
        AstralTimesPublisherConfKey.MQTT_TOPIC_OUT: AstralTimesPublisherConfKey.MQTT_TOPIC_OUT,
        AstralTimesPublisherConfKey.MQTT_LAST_WILL: AstralTimesPublisherConfKey.MQTT_LAST_WILL,
        AstralTimesPublisherConfKey.MQTT_RETAIN: True,
    }

    def setUp(self):
        self.manager = AstralTimesManager(self.DUMMY_CONFIG)
        self.dispatcher = Dispatcher(self.manager)
        self.mqtt_proxy = None  # MagicMock[MqttProxy]

        self.mqtt_proxy = mock.MagicMock(MqttProxy, autospec=True)

        self.worker = AstralTimesPublisher("test")
        self.worker.setup({
            WorkerSetup.ASTRAL_TIME_MANAGER: self.manager,
            WorkerSetup.MQTT_PROXY: self.mqtt_proxy,
            WorkerSetup.WORKER_SETTINGS: self.SETTINGS,
        })

        self.reset_mqtt_proxy()

    def reset_mqtt_proxy(self):
        self.mqtt_proxy = mock.MagicMock(MqttProxy, autospec=True)
        self.worker._mqtt_proxy = self.mqtt_proxy

    @mock.patch("worker_bunch.utils.time_utils.TimeUtils.now")
    def test_round_trip(self, mocked_now):
        now = datetime(2022, 3, 19, 9, 55, 15, tzinfo=timezone(timedelta(seconds=3600)))
        mocked_now.return_value = now

        self.worker.subscribe_notifications(self.dispatcher)

        self.worker._work([Notification.create_cron("does-it-matter?")])

        expected_payload = self.manager.get_astral_times(now)
        expected_payload["status"] = "ok"

        self.mqtt_proxy.queue.assert_called_once_with(
            topic=AstralTimesPublisherConfKey.MQTT_TOPIC_OUT,
            payload=expected_payload,
            retain=True
        )

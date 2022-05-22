import datetime
import time
import unittest
from unittest import mock

import schedule
from paho.mqtt.client import MQTTMessage
from tzlocal import get_localzone

from worker_bunch.dispatcher import Dispatcher, DispatcherListener, TopicMatch
from worker_bunch.notification import Notification


class TestTopicMatch(unittest.TestCase):

    def test_instance_vs_class_properties(self):
        t1 = TopicMatch(topic="t1", search_pattern="s1")
        listener = mock.MagicMock(DispatcherListener)
        t1.listeners.add(listener)

        t2 = TopicMatch(topic="t2")

        self.assertEqual(t1.topic, "t1")
        self.assertEqual(t1.search_pattern, "s1")
        self.assertEqual(t1.listeners, {listener})

        self.assertEqual(t2.topic, "t2")
        self.assertEqual(t2.search_pattern, None)
        self.assertEqual(t2.listeners, set())


class TestDispatcher(unittest.TestCase):

    def setUp(self):
        self.dispatcher = Dispatcher(mock.MagicMock("AstralTimeManager"))

    def tearDown(self):
        self.dispatcher.close()

    # noinspection PyTypeChecker
    def test_get_mqtt_topics(self):
        self.dispatcher.subscribe_mqtt_topics(mock.MagicMock(DispatcherListener), ["test/a", "test/#"], 0.1)
        self.dispatcher.subscribe_mqtt_topics(mock.MagicMock(DispatcherListener), ["test/a", "test/#", "test/b"], 0.1)

        topics = self.dispatcher.get_mqtt_topics()
        topics.sort()
        self.assertEqual(topics, ["test/#", "test/a", "test/b"])

    # noinspection PyTypeChecker
    def test_mqtt_messages(self):
        listener = mock.MagicMock(DispatcherListener)
        listener.add_notifications = mock.MagicMock("add_notifications")

        self.dispatcher.subscribe_mqtt_topics(listener, ["test/a", "test/#"], 0.1)

        def c_msg(topic, payload):
            m = MQTTMessage(topic=topic)
            m.payload = payload
            return m

        messages = [c_msg(b"test/a", b"test/a.1"), c_msg(b"test/a", b"test/a.2"), c_msg(b"test/b", b"test/b.1")]
        self.dispatcher.push_mqtt_messages(messages)
        time.sleep(0.05)

        m_a4 = c_msg(b"test/a", b"test/a.4")
        m_b2 = c_msg(b"test/b", b"test/b.2")

        messages = [c_msg(b"test/a", b"test/a.3"), m_a4, m_b2]
        self.dispatcher.push_mqtt_messages(messages)
        time.sleep(0.2)

        expected = {Notification.create_from_mqtt(m_a4), Notification.create_from_mqtt(m_b2)}
        listener.add_notifications.assert_called_once_with(expected)

    def test_timer(self):
        listener = mock.MagicMock(DispatcherListener)
        listener.add_notifications = mock.MagicMock("add_notifications")

        timer_job = schedule.every(5).minutes  # type: schedule.Job
        self.dispatcher.subscribe_timer(listener, timer_job, "5-minutes")

        timer_job.next_run = datetime.datetime.now()  # mock start time
        time.sleep(0.05)

        self.dispatcher.trigger_timers()

        expected = {Notification.create_timer("5-minutes")}
        listener.add_notifications.assert_called_once_with(expected)

    # noinspection PyTypeChecker
    @mock.patch("worker_bunch.utils.time_utils.TimeUtils.now")
    def test_cron(self, mocked_now):
        time_start = datetime.datetime(2022, 1, 30, 10, 0, 0, tzinfo=get_localzone())

        self.dispatcher._last_timer_execution = time_start

        mocked_now.return_value = time_start

        listener = mock.MagicMock("listener")
        listener.add_notifications = mock.MagicMock("listener")

        self.dispatcher.subscribe_cron(listener, "* * * * *", "cron-trigger")

        self.dispatcher.trigger_timers()
        listener.add_notifications.assert_not_called()

        mocked_now.return_value = time_start + datetime.timedelta(seconds=55)
        self.dispatcher.trigger_timers()

        listener.add_notifications.assert_not_called()

        mocked_now.return_value = time_start + datetime.timedelta(seconds=65)
        self.dispatcher.trigger_timers()

        expected = {Notification.create_cron("cron-trigger")}
        listener.add_notifications.assert_called_once_with(expected)

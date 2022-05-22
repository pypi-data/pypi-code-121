import copy
import unittest

from paho.mqtt.client import MQTTMessage

from worker_bunch.notification import Notification, NotificationType, NotificationBucket


class TestNotification(unittest.TestCase):

    def test_key(self):
        n1 = Notification(type=NotificationType.MQTT_MESSAGE, topic="1", payload="1")
        n21 = Notification(type=NotificationType.MQTT_MESSAGE, topic="2", payload="2.1")
        n22 = Notification(type=NotificationType.MQTT_MESSAGE, topic="2", payload="2.2")
        n3 = Notification(type=NotificationType.TIMER, topic="1", payload="1")

        self.assertEqual(n21, copy.deepcopy(n21))
        self.assertTrue(n21 == n22)
        self.assertTrue(n1 != n3)

    def test_create_from_mqtt(self):
        def create_msg(topic, payload):
            m = MQTTMessage(topic=topic)  # topic must be "bytes"
            m.payload = payload
            return m

        self.assertEqual(
            Notification.create_from_mqtt(create_msg(b"1", "1")),
            Notification(type=NotificationType.MQTT_MESSAGE, topic="1", payload="1")
        )

        self.assertEqual(
            Notification.create_from_mqtt(create_msg(b"1", b"1")),
            Notification(type=NotificationType.MQTT_MESSAGE, topic="1", payload="1")
        )


class TestNotificationBucket(unittest.TestCase):

    def test_store(self):
        n1 = Notification(type=NotificationType.MQTT_MESSAGE, topic="1", payload="1")
        n21 = Notification(type=NotificationType.MQTT_MESSAGE, topic="2", payload="2.1")
        n22 = Notification(type=NotificationType.MQTT_MESSAGE, topic="2", payload="2.2")

        bucket = NotificationBucket()

        def add(n: Notification):
            n = copy.deepcopy(n)
            bucket.add(n)

        add(n1)
        add(n21)
        add(n22)

        self.assertEqual(len(bucket), 2)

        store_list = bucket.get_list()
        store_list.sort(key=lambda n: n.topic)
        self.assertEqual(store_list[0], n1)

        # n21 get overwritten by a newer version
        self.assertEqual(store_list[1], n22)
        self.assertEqual(store_list[1].payload, n22.payload)

        self.assertTrue(bucket)

        bucket.clear()
        self.assertEqual(len(bucket), 0)
        self.assertFalse(bucket)

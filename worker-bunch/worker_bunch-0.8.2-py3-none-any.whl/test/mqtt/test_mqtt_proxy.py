import unittest
import uuid
from datetime import timedelta, timezone, datetime
from unittest.mock import MagicMock, call

from worker_bunch.mqtt.mqtt_client import MqttClient
from worker_bunch.mqtt.mqtt_proxy import MqttProxy


class TestMqttProxy(unittest.TestCase):

    def test_roundtrip_strings(self):
        client = MagicMock(MqttClient, autospec=True)
        proxy = MqttProxy(client)

        calls = []

        for i in range(1, 20):
            topic = f"{i}-test123"
            payload = f"{i}-{uuid.uuid4()}"
            retain = True if i % 2 == 0 else False

            proxy.queue(topic=topic, payload=payload, retain=retain)
            calls.append(call(topic=topic, payload=payload, retain=retain))

        proxy.publish()
        client.publish.assert_has_calls(calls)

    def test_roundtrip_dict(self):
        client = MagicMock(MqttClient, autospec=True)
        proxy = MqttProxy(client)

        topic = "test123"
        payload_to_convert = {
            "timestamp": datetime(2022, 3, 19, 9, 55, 15, tzinfo=timezone(timedelta(seconds=3600))),
            "boolean": True,
            "integer": 456,
            "float": 1.234,
            "text": "text123",
        }
        payload = '{"boolean": true, "float": 1.234, "integer": 456, "text": "text123", "timestamp": "2022-03-19T09:55:15+01:00"}'
        retain = True

        proxy.queue(topic=topic, payload=payload_to_convert, retain=retain)
        proxy.publish()

        client.publish.assert_called_once_with(topic=topic, payload=payload, retain=retain)

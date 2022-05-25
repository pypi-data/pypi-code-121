from unittest import TestCase
from holour.mqtt import MQTTClient, MQTTConfig


class Test(TestCase):

    def setUp(self) -> None:
        name = 'test_client'
        self.client = MQTTClient(name, MQTTConfig(name))

    def test_mqtt_config(self):
        assert self.client


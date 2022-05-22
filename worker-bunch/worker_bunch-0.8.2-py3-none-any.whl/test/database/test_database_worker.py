import unittest

from worker_bunch.database.database_config import DatabaseConfKey
from worker_bunch.database.database_worker import Step


class TestStep(unittest.TestCase):

    def test_create_from_dict(self):
        """keys must match property names of `Step`"""
        config = {
            DatabaseConfKey.MQTT_LAST_WILL: "last_will_123",
            DatabaseConfKey.MQTT_OUTPUT_TYPE: "json",
            DatabaseConfKey.MQTT_RETAIN: True,
            DatabaseConfKey.MQTT_TOPIC: "topic234",
            DatabaseConfKey.REPLACEMENTS: {"a": "b", "c": "d"},
            DatabaseConfKey.SCRIPT_FILE: "file567",
            DatabaseConfKey.STATEMENT: "select *"
        }

        step = Step(**config)

        for key, value in config.items():
            self.assertTrue(hasattr(step, key))
            self.assertEqual(getattr(step, key), value)

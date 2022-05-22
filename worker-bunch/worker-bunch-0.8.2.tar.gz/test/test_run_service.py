import os
import unittest

import yaml

from test.setup_test import SetupTest
from worker_bunch.database.database_config import DatabaseConfKey, MqttOutputType
from worker_bunch.run_service import generate_json_schema_info


class TestGenerateJsonSchemaInfo(unittest.TestCase):

    MAIN_WORKER = "mainWorker"

    @classmethod
    def create_config_file(cls, steps):
        data = {
            "mqtt_broker": {"host": "mocked"},
            "database_connections": {"main-db": {
                "host": "host",
                "port": 5435,
                "database": "database"
            }},
            "worker_instances": {cls.MAIN_WORKER: "worker_bunch.database.database_worker.DatabaseWorker"},
            "worker_settings": {cls.MAIN_WORKER: {
                "connection_key": "main",
                "cron": "* * * * *",
                "steps": steps,
            }},
        }

        config_file = SetupTest.get_test_path("config_file.yaml")
        with open(config_file, 'w') as write_file:
            yaml.dump(data, write_file, default_flow_style=False)

        os.chmod(config_file, 0o600)

        return config_file

    def assert_step_properties(self, output: str):
        self.assertIn(DatabaseConfKey.MQTT_LAST_WILL, output)
        self.assertIn(DatabaseConfKey.MQTT_OUTPUT_TYPE, output)
        self.assertIn(DatabaseConfKey.MQTT_TOPIC, output)
        self.assertIn(DatabaseConfKey.REPLACEMENTS, output)
        self.assertIn(DatabaseConfKey.STATEMENT, output)
        self.assertIn(DatabaseConfKey.SCRIPT_FILE, output)

    def test_complex(self):
        output = generate_json_schema_info(None)
        lines_without_config_file = len(output.split("\n"))
        self.assertGreater(lines_without_config_file, 100)

        steps = [{
            DatabaseConfKey.MQTT_LAST_WILL: DatabaseConfKey.MQTT_LAST_WILL,
            DatabaseConfKey.MQTT_OUTPUT_TYPE: MqttOutputType.SCALAR,
            DatabaseConfKey.MQTT_TOPIC: DatabaseConfKey.MQTT_TOPIC,
            DatabaseConfKey.REPLACEMENTS: {"%XXX%": "dummy"},
            DatabaseConfKey.STATEMENT: "SELECT COUNT(1) FROM %XXX%",
        }]
        config_file = self.create_config_file(steps)
        output = generate_json_schema_info(config_file)
        lines_with_config_file = len(output.split("\n"))
        self.assertGreater(lines_with_config_file, lines_without_config_file)
        self.assert_step_properties(output)

        steps = []
        config_file = self.create_config_file(steps)
        output = generate_json_schema_info(config_file)
        lines_with_invalid_config_file = len(output.split("\n"))
        self.assertGreaterEqual(lines_with_invalid_config_file, lines_with_config_file)

        self.assert_step_properties(output)

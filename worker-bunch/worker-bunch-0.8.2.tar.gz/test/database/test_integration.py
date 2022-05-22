import abc
import copy
import os
import unittest
from unittest import mock
from unittest.mock import MagicMock, call

import yaml
from psycopg.errors import DuplicateTable

from test.setup_test import SetupTest
from worker_bunch.database.database_config import DatabaseConfKey, MqttOutputType
from worker_bunch.mqtt.mqtt_client import MqttClient, MqttClientFactory
from worker_bunch.run_service import run_service
from worker_bunch.service_config import ConfigException


class MockMqttClientFactory:
    mock: MagicMock = None

    @classmethod
    def create(cls, _):
        if not cls.mock:
            cls.reset()
        return cls.mock

    @classmethod
    def reset(cls):
        cls.mock = MagicMock(MqttClient, autospec=True)


class BaseTestIntegration(unittest.TestCase):

    DO_LOGGING = False
    MAIN_WORKER = "mainWorker"

    def setUp(self):
        SetupTest.init_database()
        if self.DO_LOGGING:
            SetupTest.init_logging()

        MockMqttClientFactory.reset()

        database_config = copy.deepcopy(SetupTest.get_database_params())

        steps = self.create_steps()
        worker_replacements = self.create_worker_replacements()
        self._config_file = self.create_config_file(database_config, steps, worker_replacements)

        try:
            SetupTest.execute_commands(["CREATE TABLE dummy (id SERIAL PRIMARY KEY, text VARCHAR(128))"])
        except DuplicateTable:
            SetupTest.execute_commands(["DELETE FROM dummy"])

        SetupTest.execute_commands(["INSERT INTO dummy (text) VALUES ('text1')"])

        # just to make that all is working
        fetched = SetupTest.query_one("select COUNT(1) AS count FROM dummy")
        self.assertEqual(fetched["count"], 1)

        self._mocked_mqtt_client = MagicMock(MqttClient, autospec=True)

    def tearDown(self):
        SetupTest.close_database()

    @abc.abstractmethod
    def create_steps(self):
        raise NotImplementedError()

    def create_worker_replacements(self):
        return None

    def run_service_single_mode(self, config_file):
        run_service(config_file=config_file, log_file=None, log_level="debug", print_log_console=True, skip_log_times=True,
                    test_single=self.MAIN_WORKER)

    @classmethod
    def prepare_mocked_mqtt_client(cls, mocked_mqtt_client):
        mocked_mqtt_client.is_connected.return_value = True

    @classmethod
    def create_config_file(cls, database_config, steps, worker_replacements=None):
        worker_settings = {
            "connection_key": "main",
            "cron": "* * * * *",
            "steps": steps,
        }
        if worker_replacements:
            worker_settings["replacements"] = worker_replacements

        data = {
            "mqtt_broker": {"host": "mocked"},
            "database_connections": {"main": database_config},
            "worker_instances": {cls.MAIN_WORKER: "worker_bunch.database.database_worker.DatabaseWorker"},
            "worker_settings": {cls.MAIN_WORKER: worker_settings},
        }

        config_file = SetupTest.get_test_path("config_file.yaml")
        with open(config_file, 'w') as write_file:
            yaml.dump(data, write_file, default_flow_style=False)

        os.chmod(config_file, 0o600)

        return config_file


class TestIntegrationScalar(BaseTestIntegration):

    def create_steps(self):
        return [{
            DatabaseConfKey.MQTT_LAST_WILL: DatabaseConfKey.MQTT_LAST_WILL,
            DatabaseConfKey.MQTT_OUTPUT_TYPE: MqttOutputType.SCALAR,
            DatabaseConfKey.MQTT_TOPIC: DatabaseConfKey.MQTT_TOPIC,
            DatabaseConfKey.REPLACEMENTS: {"%XXX%": "dummy"},
            DatabaseConfKey.STATEMENT: "SELECT COUNT(1) FROM %XXX%",
        }]

    @mock.patch.object(MqttClientFactory, "create", MockMqttClientFactory.create)
    def test_full_integration_scalar(self):
        mocked_mqtt_client = MockMqttClientFactory.mock
        self.prepare_mocked_mqtt_client(mocked_mqtt_client)

        self.run_service_single_mode(self._config_file)

        mocked_mqtt_client.set_last_will.assert_called_once_with(
            topic=DatabaseConfKey.MQTT_TOPIC, last_will=DatabaseConfKey.MQTT_LAST_WILL, retain=False
        )

        calls = [
            call(topic=DatabaseConfKey.MQTT_TOPIC, payload="1", retain=False),
            call(topic=DatabaseConfKey.MQTT_TOPIC, payload=DatabaseConfKey.MQTT_LAST_WILL, retain=False),
        ]
        mocked_mqtt_client.publish.assert_has_calls(calls)


class TestIntegrationJson(BaseTestIntegration):
    """Test JSON + script file"""

    def setUp(self):
        statement = "SELECT '{%a%}' as a, '{%b%}' as b"
        script_file = SetupTest.get_test_path("integration_template_file.sql")
        with open(script_file, 'w') as f:
            f.write(statement)

        self.steps = [{
            DatabaseConfKey.MQTT_LAST_WILL: DatabaseConfKey.MQTT_LAST_WILL,
            DatabaseConfKey.MQTT_OUTPUT_TYPE: MqttOutputType.JSON,
            DatabaseConfKey.MQTT_TOPIC: DatabaseConfKey.MQTT_TOPIC,
            DatabaseConfKey.REPLACEMENTS: {"{%a%}": "a_step"},
            DatabaseConfKey.SCRIPT_FILE: script_file,
        }]

        self.worker_replacements = {"{%a%}": "a_worker", "{%b%}": "b_worker"}

        super().setUp()

    def create_steps(self):
        return self.steps

    def create_worker_replacements(self):
        return self.worker_replacements

    @mock.patch.object(MqttClientFactory, "create", MockMqttClientFactory.create)
    def test_full_integration_json(self):
        mocked_mqtt_client = MockMqttClientFactory.mock
        self.prepare_mocked_mqtt_client(mocked_mqtt_client)

        self.run_service_single_mode(self._config_file)

        mocked_mqtt_client.set_last_will.assert_called_once_with(
            topic=DatabaseConfKey.MQTT_TOPIC, last_will=DatabaseConfKey.MQTT_LAST_WILL, retain=False
        )

        calls = [
            call(topic=DatabaseConfKey.MQTT_TOPIC, payload='{"a": "a_step", "b": "b_worker"}', retain=False),
            call(topic=DatabaseConfKey.MQTT_TOPIC, payload=DatabaseConfKey.MQTT_LAST_WILL, retain=False),
        ]
        mocked_mqtt_client.publish.assert_has_calls(calls)


class TestIntegrationFileNotFound(BaseTestIntegration):
    """Test JSON + script file"""

    def setUp(self):
        self.script_file = SetupTest.get_test_path("integration_template_file.sql")
        if os.path.exists(self.script_file):
            os.remove(self.script_file)

        self.steps = [{
            DatabaseConfKey.MQTT_OUTPUT_TYPE: MqttOutputType.JSON,
            DatabaseConfKey.MQTT_TOPIC: DatabaseConfKey.MQTT_TOPIC,
            DatabaseConfKey.SCRIPT_FILE: self.script_file,
        }]

        super().setUp()

    def create_steps(self):
        return self.steps

    @mock.patch.object(MqttClientFactory, "create", MockMqttClientFactory.create)
    def test_full_integration_json(self):
        with self.assertRaises(ConfigException):
            self.run_service_single_mode(self._config_file)


class TestIntegrationExecute(BaseTestIntegration):

    ADD_ROWS = 6

    def create_steps(self):
        steps = []
        for i in range(self.ADD_ROWS):
            text = f"text-{i}"
            steps.append({
                DatabaseConfKey.MQTT_OUTPUT_TYPE: MqttOutputType.NONE,
                DatabaseConfKey.STATEMENT: f"INSERT INTO dummy (text) VALUES ('{text}')",
            })
        return steps

    @mock.patch.object(MqttClientFactory, "create", MockMqttClientFactory.create)
    def test_full_integration_execute(self):
        mocked_mqtt_client = MockMqttClientFactory.mock
        self.prepare_mocked_mqtt_client(mocked_mqtt_client)

        self.run_service_single_mode(self._config_file)

        fetched = SetupTest.query_one("select COUNT(1) AS count FROM dummy")
        self.assertEqual(fetched["count"], 7)

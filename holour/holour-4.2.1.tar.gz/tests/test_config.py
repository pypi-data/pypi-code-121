from unittest import TestCase
import logging
import os
from holour.mqtt import MQTTConfig
from holour import load_configuration


class Test(TestCase):

    def setUp(self) -> None:
        pass

    @staticmethod
    def path(filename: str) -> str:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = os.path.join(dir_path, 'config')
        return os.path.join(dir_path, filename)

    def test_mqtt_config(self):
        raw_config = {'client_id': 'test'}
        config = MQTTConfig(**raw_config)
        assert config.client_id == 'test'

    def test_load_configuration_without_file(self):
        with self.assertLogs(level=logging.ERROR) as log:
            output = load_configuration(self.path('doesnt.exist'), logging.getLogger('test'))

            assert output == {}
            self.assertEqual(len(log.output), 1)

    def test_load_configuration_invalid_file(self):
        with self.assertLogs(level=logging.ERROR) as log:
            output = load_configuration(self.path('load_invalid_config.yml'), logging.getLogger('test'))
            expected = {}

            assert output == {}, f"Expected: {expected}, got: {output}"
            self.assertEqual(len(log.output), 1)

    def test_load_configuration(self):
        with self.assertLogs(level=logging.INFO) as log:
            output = load_configuration(self.path('load_config_test.yml'), logging.getLogger('test'))
            expected = {'mqtt': {'client_id': 'test'}}

            assert output == expected, f"Expected: {expected}, got: {output}"
            self.assertEqual(len(log.output), 1)

    def test_load_configuration_and_init_config(self):
        output = load_configuration(self.path('load_full_config_test.yml'), logging.getLogger('test'))
        expected = {'mqtt': {
            'client_id': 'test_client',
            'address': '192.168.0.50',
            'port': 18831,
            'keep_alive': 30,
            'prefix': 'roberta/'}
        }
        assert output == expected, f"Expected: {expected}, got: {output}"

        config = MQTTConfig(**output['mqtt'])
        assert config.client_id == 'test_client'
        assert config.address == '192.168.0.50'

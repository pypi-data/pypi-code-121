import unittest
from aos_prov.utils.config import Config


class TestConfig(unittest.TestCase):
    def test_config_can_be_created(self):
        c = Config()
        self.assertIsInstance(c, Config)

    def test_setters_and_getters(self):
        c = Config()
        c.system_id = 'some system id'
        self.assertEqual(c.system_id, 'some system id')

        c.supported_cert_types = ['um', 'sm']
        self.assertEqual(c.supported_cert_types, ['um', 'sm'])


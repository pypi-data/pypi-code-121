from configparser import ConfigParser

from extractor import load_config
from tests.main import BaseTest


class TestExtractor(BaseTest):
    def test_loading_config(self):
        config = load_config()
        self.assertIsInstance(config, ConfigParser)

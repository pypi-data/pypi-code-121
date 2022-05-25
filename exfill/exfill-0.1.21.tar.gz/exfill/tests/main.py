import os
import unittest
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path

CURRENT_DIR = Path(__file__).parent


class BaseTest(unittest.TestCase):
    @staticmethod
    def load_test_config(self):
        config_file = os.path.abspath(os.curdir) + "/src/exfill/config.ini"
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read(config_file)
        return self.config

    def load_test_data_html_path(self):
        return CURRENT_DIR / "test_data/html"

    # def test_print_config(self):
    #     for dir_path in self.config.sections():
    #         print(dir_path)
    #     assert 1


if __name__ == "__main__":
    unittest.main()

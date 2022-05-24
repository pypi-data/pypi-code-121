import os
from unittest import TestCase

from cloudshell.shell.flows.autoload.autoload_utils import get_device_name


class TestGetDeviceName(TestCase):
    FILE_PATH = os.path.join(os.path.dirname(__file__), "device_names_map.csv")

    def test_get_device_name(self):
        name = get_device_name(self.FILE_PATH, "cisco12012")
        self.assertEqual(name, "Cisco 12012")

    def test_get_device_name__name_does_not_exist(self):
        name = get_device_name(self.FILE_PATH, "fakename")
        self.assertEqual(name, "fakename")

    def test_get_device_name__csv_file_not_exists(self):
        name = get_device_name("not_exists_file.csv", "cisco")
        self.assertEqual(name, "cisco")

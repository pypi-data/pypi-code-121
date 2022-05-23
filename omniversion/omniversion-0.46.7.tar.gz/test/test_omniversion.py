import os
import unittest

from omniversion import Omniversion
from omniversion.models import DataSources, FileDataSource, ConfigDataSource, PackageMetadata

TEST_FILE_PATH = os.path.join(os.path.dirname(__file__), "../vectors/test-env.txt")


class OmniversionTestCase(unittest.TestCase):
    def test_str_for_no_data(self):
        omniversion = Omniversion(base_path=None)
        self.assertEqual("omniversion data: no sources loaded", omniversion.__str__())

    def test_str_for_single_file(self):
        data_sources = DataSources()
        data_sources.files = [FileDataSource()]
        omniversion = Omniversion(base_path=None, data_sources=data_sources)
        self.assertEqual("omniversion data: 1 file and 0 config items loaded for 1 host", omniversion.__str__())

    def test_str_for_multiple_files(self):
        data_sources = DataSources()
        data_sources.files = [FileDataSource(), FileDataSource()]
        omniversion = Omniversion(base_path=None, data_sources=data_sources)
        self.assertEqual("omniversion data: 2 files and 0 config items loaded for 1 host", omniversion.__str__())

    def test_str_for_files_and_configs(self):
        data_sources = DataSources()
        data_sources.files = [FileDataSource(), FileDataSource()]
        data_sources.configs = [ConfigDataSource(file_path="/test", regex="")]
        omniversion = Omniversion(base_path=None, data_sources=data_sources)
        self.assertEqual("omniversion data: 2 files and 1 config item loaded for 1 host", omniversion.__str__())

    def test_hostnames(self):
        data_sources = DataSources()
        data_sources.files = [FileDataSource(host="test1"),
                              FileDataSource(host="test2"),
                              FileDataSource(host="test2")]
        data_sources.configs = [ConfigDataSource(host="test1", file_path="/test", regex=""),
                                ConfigDataSource(host="test2", file_path="/test", regex="")]
        omniversion = Omniversion(base_path=None, data_sources=data_sources)
        self.assertListEqual(["test1", "test2"], omniversion.hostnames)

    def test_localhost(self):
        data_sources = DataSources()
        data_sources.packages = [
            PackageMetadata(name="test1", host="host1"),
            PackageMetadata(name="test2", host="localhost"),
            PackageMetadata(name="test3", host="localhost"),
            PackageMetadata(name="test4", host="host1"),
        ]
        omniversion = Omniversion(base_path=None, data_sources=data_sources)
        localhost = omniversion.localhost
        self.assertEqual(2, len(localhost.packages))

    def test_load_test_vectors(self):
        omniversion = Omniversion(base_path=os.path.join(os.path.dirname(__file__), "./vectors"))
        self.assertGreater(len(omniversion.packages), 0)


if __name__ == '__main__':
    unittest.main()

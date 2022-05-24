import unittest
from slpkg.pkg.installed import GetFromInstalled


class TestPkgInstalled(unittest.TestCase):

    def setUp(self):
        self.pkg_name = 'aaa_base'
        self.pkg_ver = '15.0'
        self.installed = GetFromInstalled('aaa_base')

    def test_pkg_name(self):
        """Testing the installed package name
        """
        self.assertEqual(self.pkg_name, self.installed.name())

    def test_pkg_version(self):
        """Testing the version of installed package"""
        self.assertEqual(self.pkg_ver, self.installed.version())


if __name__ == "__main__":
    unittest.main()

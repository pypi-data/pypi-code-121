import unittest

from deptools.versiontype import version_type


class TestChangeLog(unittest.TestCase):
    def test(self):
        self.assertEqual(version_type("meh"), "invalid")
        self.assertEqual(version_type("v1.2.3-beta2"), "pre-release")
        self.assertEqual(version_type("2.3.4"), "release")

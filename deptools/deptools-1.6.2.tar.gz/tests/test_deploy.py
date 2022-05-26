import unittest

from deptools import deploy as dpl


class TestDeploy(unittest.TestCase):
    def test_netloc(self):
        visitor = dpl.NetLocRuleVisitor()
        self.assertEqual(
            visitor.parse("ftp.alazartech.com"),
            dpl.NetLoc(None, None, "ftp.alazartech.com"))
        self.assertEqual(
            visitor.parse("administrator:H1pass@ftp.alazartech.com"),
            dpl.NetLoc("administrator", "H1pass", "ftp.alazartech.com"))


if __name__ == "__main__":
    unittest.main()

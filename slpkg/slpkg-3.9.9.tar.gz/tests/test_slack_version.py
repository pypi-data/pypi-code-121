import unittest
from slpkg.slack.slack_version import slack_ver


class TestSlackVersion(unittest.TestCase):

    def test_slack_version(self):
        """Testing the current Slackware version
        """
        ver = '15.0'
        self.assertEqual(ver, slack_ver())


if __name__ == "__main__":
    unittest.main()

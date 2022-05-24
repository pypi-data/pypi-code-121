import unittest
from slpkg.file_size import FileSize


class TestFileSize(unittest.TestCase):

    def test_FileSize(self):
        """Testing the remote and local servers
        """
        url = "https://mirrors.slackware.com/slackware/slackware64-14.2/ChangeLog.txt"
        lc = "test_units.py"
        fs1 = FileSize(url)
        fs2 = FileSize(lc)
        self.assertIsNotNone(fs1.server())
        self.assertIsNotNone(fs2.local())


if __name__ == "__main__":
    unittest.main()

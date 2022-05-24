import unittest
from slpkg.md5sum import md5


class TestMd5(unittest.TestCase):

    def test_md5_superuser(self):
        """Testing checksum for superuser.py file
        """
        result = md5('test_file_size.py')
        self.assertEqual(result, "e3e7b72be80efc922b0e1f1cd409a417")

    def test_md5_security(self):
        """Testing checksum for security.py file
        """
        result = md5('test_units.py')
        self.assertEqual(result, "58a694171449e923414e3e3339a0097e")


if __name__ == "__main__":
    unittest.main()

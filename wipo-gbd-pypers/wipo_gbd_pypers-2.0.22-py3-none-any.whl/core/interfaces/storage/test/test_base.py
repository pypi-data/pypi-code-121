import unittest
from pypers.core.interfaces.storage.test import MockS3
from pypers.core.interfaces.storage.base import StorageBase
from pypers.core.interfaces.storage import get_storage
from mock import patch, MagicMock


mockde_s3 = MockS3()


def mock_s3(*args, **kwargs):
    return mockde_s3


class TestDbBaseInit(unittest.TestCase):
    @patch("boto3.client", MagicMock(side_effect=mock_s3))
    def test_interfaces(self):
        self.assertTrue(get_storage() is not None)


class TestSQSBase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_interfaces(self):
        try:
            self.s3 = StorageBase()
            self.fail("should raise not implemented")
        except NotImplementedError as e:
            pass


if __name__ == "__main__":
    unittest.main()

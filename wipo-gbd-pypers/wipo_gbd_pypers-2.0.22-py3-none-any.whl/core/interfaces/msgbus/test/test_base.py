import unittest
from pypers.core.interfaces.msgbus.test import MockSQS
from pypers.core.interfaces.msgbus.base import MSGBase
from pypers.core.interfaces.msgbus import get_msg_bus
from mock import patch, MagicMock


mockde_sqs = MockSQS()


def mock_sqs(*args, **kwargs):
    return mockde_sqs


class TestDbBaseInit(unittest.TestCase):
    @patch("boto3.resource", MagicMock(side_effect=mock_sqs))
    def test_interfaces(self):
        self.assertTrue(get_msg_bus() is not None)


class TestSQSBase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_interfaces(self):
        try:
            self.sqs = MSGBase()
            self.fail("should raise not implemented")
        except NotImplementedError as e:
            pass


if __name__ == "__main__":
    unittest.main()

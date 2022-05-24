import unittest
from pypers.core.interfaces.msgbus.sqs import SQS
from pypers.core.interfaces.msgbus.test import MockSQS
from mock import patch, MagicMock
import os
from decimal import Decimal


mockde_sqs = MockSQS()


def mock_sqs(*args, **kwargs):
    return mockde_sqs


class TestDbBase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch("boto3.resource", MagicMock(side_effect=mock_sqs))
    def test_init(self):
        db = SQS()
        self.assertTrue(db is not None)
        os.environ['SQS_URL'] = 'http://google.com'
        db = SQS()
        self.assertTrue(db is not None)
        os.environ['GITHUB_TOKEN'] = 'http://google.com'
        db = SQS()
        self.assertTrue(db is not None)

    @patch("boto3.resource", MagicMock(side_effect=mock_sqs))
    def test_create_new_run_for_pipeline(self):
        db = SQS()
        self.assertEqual(
            db.send_message('test', 'test', 'test', 'test', 'test', True), None)
        db.reset_history('test', 'test')

    @patch("boto3.resource", MagicMock(side_effect=mock_sqs))
    def test_messge(self):
        db = SQS()
        m = db.get_messges()
        self.assertEqual(
            m[1], '1234')
        self.assertTrue(
            db.processing_messages.get('1234', None) is not None)
        db.delete_message('1234')
        self.assertTrue(
            db.processing_messages.get('1234', None) is None)


if __name__ == "__main__":
    unittest.main()

import unittest
from pypers.core.interfaces.db.dynamodb import DynamoDbLogger, DEBUG
from pypers.core.interfaces.db.test import MockDBLogger
from mock import patch, MagicMock
import os


mockde_db = MockDBLogger()


def mock_db(*args, **kwargs):
    return mockde_db


class TestDbBase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch("boto3.resource", MagicMock(side_effect=mock_db))
    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_init(self):
        db = DynamoDbLogger()
        self.assertTrue(db is not None)
        os.environ['DYDB_URL'] = 'http://google.com'
        db = DynamoDbLogger()
        self.assertTrue(db is not None)
        os.environ['GITHUB_TOKEN'] = 'http://google.com'
        db = DynamoDbLogger()
        self.assertTrue(db is not None)

    @patch("boto3.resource", MagicMock(side_effect=mock_db))
    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_create_schema(self):
        db = DynamoDbLogger()
        db.create_pypers_config_schema()
        mockde_db.display_error = True
        try:
            db.create_pypers_config_schema()
            self.fail("Should raise error")
        except Exception as e:
            pass

    @patch("boto3.resource", MagicMock(side_effect=mock_db))
    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_create_new_run_for_pipeline(self):
        global DEBUG
        DEBUG = True
        db = DynamoDbLogger()
        self.assertEqual(
            db.log_entry('test', 'test','test', type_log="DEBUG"),
            None)
       


if __name__ == "__main__":
    unittest.main()

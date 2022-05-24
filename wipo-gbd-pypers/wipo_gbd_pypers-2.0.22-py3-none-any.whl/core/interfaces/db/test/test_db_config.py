import unittest
from pypers.core.interfaces.db.dynamodb import DynamoDbConfig, DEBUG
from pypers.core.interfaces.db.test import MockDBConfig
from mock import patch, MagicMock
import os


mockde_db = MockDBConfig()


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
        db = DynamoDbConfig()
        self.assertTrue(db is not None)
        os.environ['DYDB_URL'] = 'http://google.com'
        db = DynamoDbConfig()
        self.assertTrue(db is not None)
        os.environ['GITHUB_TOKEN'] = 'http://google.com'
        db = DynamoDbConfig()
        self.assertTrue(db is not None)

    @patch("boto3.resource", MagicMock(side_effect=mock_db))
    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_create_schema(self):
        db = DynamoDbConfig()
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
        db = DynamoDbConfig()
        self.assertEqual(
            db.get_configuration('test'),
            mockde_db.get_configuration())


if __name__ == "__main__":
    unittest.main()

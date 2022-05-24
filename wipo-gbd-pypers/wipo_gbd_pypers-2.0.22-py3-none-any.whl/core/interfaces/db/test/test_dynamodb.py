import unittest
from pypers.core.interfaces.db.dynamodb import DynamoDBInterface
from pypers.core.interfaces.db.test import MockDB
from mock import patch, MagicMock
import os
from decimal import Decimal


mockde_db = MockDB()


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
        db = DynamoDBInterface()
        self.assertTrue(db is not None)
        os.environ['DYDB_URL'] = 'http://google.com'
        db = DynamoDBInterface()
        self.assertTrue(db is not None)
        os.environ['GITHUB_TOKEN'] = 'http://google.com'
        db = DynamoDBInterface()
        self.assertTrue(db is not None)

    @patch("boto3.resource", MagicMock(side_effect=mock_db))
    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_create_schema(self):
        db = DynamoDBInterface()
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
        db = DynamoDBInterface()
        self.assertEqual(
            db.create_new_run_for_pipeline('test', 'test', {}),
            None)

    @patch("boto3.resource", MagicMock(side_effect=mock_db))
    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_create_step_config(self):
        db = DynamoDBInterface()
        self.assertEqual(
            db.create_step_config('test', 'test', 'foo', {}, []),
            None)
        self.assertEqual(
            db.create_step_config('test', 'test', 'bar', {}, []),
            None)
        self.assertEqual(
            db.create_step_config('test', 'test', 'foo',  {}, [], '0'),
            None)

    @patch("boto3.resource", MagicMock(side_effect=mock_db))
    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_get_step_config(self):
        db = DynamoDBInterface()
        self.assertEqual(
            db.get_step_config('test', 'test', 'bar'),
            None)
        self.assertEqual(
            db.get_step_config('test', 'test', 'foo', '0'),
            None)

    @patch("boto3.resource", MagicMock(side_effect=mock_db))
    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_has_step_config_changed(self):
        db = DynamoDBInterface()
        self.assertEqual(
            db.has_step_config_changed('test', 'test', 'bar'),
            True)
        self.assertEqual(
            db.has_step_config_changed('test', 'test', 'foo', '0'),
            True)

    @patch("boto3.resource", MagicMock(side_effect=mock_db))
    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_reset_step_output(self):
        db = DynamoDBInterface()
        self.assertEqual(
            db.reset_step_output('test', 'test', 'bar'),
            None)
        self.assertEqual(
            db.reset_step_output('test', 'test', 'foo', '0'),
            None)
        self.assertEqual(
            db.get_report('test', 'test', 'test'),
            {})
        self.assertEqual(
            db.log_report('test', 'test', 'test', 'test'),
            None)

    @patch("boto3.resource", MagicMock(side_effect=mock_db))
    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_has_step_run(self):
        db = DynamoDBInterface()
        self.assertEqual(
            db.has_step_run('test', 'test', 'bar'),
            False)
        self.assertEqual(
            db.has_step_run('test', 'test', 'foo', '0'),
            False)

    @patch("boto3.resource", MagicMock(side_effect=mock_db))
    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_set_step_output(self):
        db = DynamoDBInterface()
        self.assertEqual(
            db.set_step_output('test', 'test', 'bar', {'status': 'Running'}),
            None)
        self.assertEqual(
            db.set_step_output('test', 'test', 'foo', {'status': 'Running'}, '0'),
            None)

    @patch("boto3.resource", MagicMock(side_effect=mock_db))
    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_replace_decimals(self):
        db = DynamoDBInterface()
        in_dict = [{
            'foo': Decimal(1),
            'bar': Decimal(1.1)
        }]
        in_dict = db.replace_decimals(in_dict)
        self.assertEqual(type(in_dict[0]['foo']), int)
        self.assertEqual(type(in_dict[0]['bar']), float)

    @patch("boto3.resource", MagicMock(side_effect=mock_db))
    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_dict_same(self):
        db = DynamoDBInterface()
        self.assertTrue(db.dict_same(['a'], ['b']))
        self.assertTrue(db.dict_same(['a'], []))
        self.assertTrue(db.dict_same({'a': '1'}, {'b': '1'}))


if __name__ == "__main__":
    unittest.main()

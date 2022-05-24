import unittest
from pypers.core.interfaces.db.secretsdb import SecretsManager
from pypers.core.interfaces.db.test import MockDB
from mock import patch, MagicMock
import os
from decimal import Decimal


mockde_db = MockDB()


def mock_db(*args, **kwargs):
    return mockde_db


class TestSecrets(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch("boto3.resource", MagicMock(side_effect=mock_db))
    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_init(self):
        db = SecretsManager()
        self.assertTrue(db is not None)
        os.environ['KSTR_URL'] = 'http://google.com'
        db = SecretsManager()
        self.assertTrue(db is not None)
        os.environ['GITHUB_TOKEN'] = 'http://google.com'
        db = SecretsManager()
        self.assertTrue(db is not None)

    @patch("boto3.resource", MagicMock(side_effect=mock_db))
    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_create_schema(self):
        db = SecretsManager()
        db.secrets = {
            'foo': 'bar'
        }
        db.secretes_revers = {v: k for k, v in db.secrets.items()}
        self.assertEqual(db.get('foo', 'foo'), 'bar')
        self.assertEqual(db.get('foo2', 'foo'), 'foo')
        self.assertEqual(db.key_from_value('bar'), '${foo}')


if __name__ == "__main__":
    unittest.main()

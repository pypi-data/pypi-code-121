import unittest
from pypers.core.interfaces.storage.s3 import S3Interface
from pypers.core.interfaces.storage.test import MockS3
from mock import patch, MagicMock
import os
from io import BufferedReader
from decimal import Decimal


mockde_s3 = MockS3()


def mock_s3(*args, **kwargs):
    return mockde_s3


class TestDbBase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch("boto3.resource", MagicMock(side_effect=mock_s3))
    def test_init(self):
        db = S3Interface('test')
        self.assertTrue(db is not None)
        os.environ['S3_URL'] = 'http://google.com'
        db = S3Interface('test')
        self.assertTrue(db is not None)
        os.environ['GITHUB_TOKEN'] = 'http://google.com'
        db = S3Interface('test')
        self.assertTrue(db is not None)

    @patch("boto3.resource", MagicMock(side_effect=mock_s3))
    def test_save_file(self):
        db = S3Interface('test')
        with open('test.txt', 'w') as f:
            f.write('test')
        self.assertEqual(
            db.save_file('test', 'test', 'test.txt', './test.txt'), None)
        self.assertEqual(
            db.list_files('test', 'test')[0]['Key'], 'test/test/test.txt')
        self.assertEqual(
            db.list_files()[0]['Key'], 'test/test/test.txt')
        self.assertEqual(
            db.get_file('test', 'test', 'test.txt', './test.txt'), None)
        self.assertEqual(
            type(db.get_file('test', 'test', 'test.txt')), BufferedReader)
        os.remove('test.txt')



if __name__ == "__main__":
    unittest.main()

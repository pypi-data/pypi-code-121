import unittest
from pypers.core.logger import Logger
import os
import shutil
from pypers.core.interfaces.db.test import MockDBLogger
from mock import patch, MagicMock


mocked_logger = MockDBLogger()


def mock_logger(*args, **kwargs):
    return mocked_logger


class TestLogger(unittest.TestCase):

    def setUp(self):
        self.path = 'toto/'
        try:
            shutil.rmtree('toto/')
        except Exception as e:
            pass
        os.makedirs(self.path)

    def tearDown(self):
        try:
            shutil.rmtree('toto/')
        except Exception as e:
            pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_logger(self):
        if os.environ.get('SHORT_TEST', None):
            return
        lo = Logger('test', 'test', 'test', 'test')
        self.assertTrue(hasattr(lo, 'debug'))


if __name__ == "__main__":
    unittest.main()

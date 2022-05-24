import unittest
from pypers.core.interfaces.db.test import MockDBLogger
from pypers.core.interfaces.db.base import DbBase
from pypers.core.interfaces.config.pypers_schema_db import PYPERS_RUN_CONFIG
from pypers.core.interfaces.db import get_db, get_db_logger, get_db_config, \
    get_db_error, get_seen_steps, get_done_file_manager, get_pre_prod_db
from mock import patch, MagicMock
import os


mockde_db = MockDBLogger()


def mock_db(*args, **kwargs):
    return mockde_db


class TestDbBaseInit(unittest.TestCase):
    @patch("boto3.client", MagicMock(side_effect=mock_db))
    @patch("boto3.resource", MagicMock(side_effect=mock_db))
    def test_interfaces(self):
        self.assertTrue(get_db() is not None)
        self.assertTrue(get_db_logger() is not None)
        self.assertTrue(get_db_config() is not None)
        self.assertTrue(get_db_error() is not None)
        self.assertTrue(get_seen_steps() is not None)
        self.assertTrue(get_done_file_manager() is not None)
        self.assertTrue(get_pre_prod_db() is not None)


class TestDbBase(unittest.TestCase):

    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def setUp(self):
        if os.environ.get("GITHUB_TOKEN", None):
            return
        self.db = DbBase(config=PYPERS_RUN_CONFIG, endpoint='DYDB_URL',
                         mocker=MockDBLogger)

    def tearDown(self):
        pass

    def test_interfaces(self):
        if os.environ.get("GITHUB_TOKEN", None):
            return
        try:
            self.db.create_new_run_for_pipeline('test', 'test', {})
            self.fail("should raise not implemented")
        except NotImplementedError as e:
            pass
        try:
            self.db.create_step_config('test', 'test', 'foo', {}, [])
            self.fail("should raise not implemented")
        except NotImplementedError as e:
            pass
        try:
            self.db.get_run_id_config('test', 'test')
            self.fail("should raise not implemented")
        except NotImplementedError as e:
            pass
        try:
            self.db.get_step_config('test', 'test', 'foo')
            self.fail("should raise not implemented")
        except NotImplementedError as e:
            pass
        try:
            self.db.has_step_config_changed('test', 'test', 'foo')
            self.fail("should raise not implemented")
        except NotImplementedError as e:
            pass
        try:
            self.db.reset_step_output('test', 'test', 'foo')
            self.fail("should raise not implemented")
        except NotImplementedError as e:
            pass
        try:
            self.db.has_step_run('test', 'test', 'foo')
            self.fail("should raise not implemented")
        except NotImplementedError as e:
            pass
        try:
            self.db.set_step_output('test', 'test', 'foo', {})
            self.fail("should raise not implemented")
        except NotImplementedError as e:
            pass


if __name__ == "__main__":
    unittest.main()

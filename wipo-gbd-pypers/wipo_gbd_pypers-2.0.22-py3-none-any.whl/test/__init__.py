import os
import shutil
from contextlib import contextmanager
from io import StringIO
import sys
import json
from pypers.core.interfaces.db.base import DbBase
from pypers.core.interfaces.db.test import MockDBLogger
from enum import Enum


def copy_files_to_path(dest_path, file_name):
    current_path = os.path.abspath(os.path.dirname(__file__))
    current_path = os.path.join(current_path, 'files', file_name)
    if os.path.exists(current_path):
        shutil.copy(current_path, dest_path)


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class MockXMLParser():
    def __init__(self, *args, **kwargs):
        pass

    def validate(self):
        return json.dumps({'foo': 'bar'}), None, None

class ErrorSeverityMock(Enum):
    CRITICAL = 'CRITICAL'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'

class MockRuleEngine():

    def __init__(self, *args, **kwargs):
        pass

    def validate(self):
        return []


class MockDB(DbBase):

    attributs = ['meta', 'client']
    func = ['get_waiter', 'wait', 'put_item', 'log_entry', 'log_report', 'put_items', 'batch_writer']

    def __enter__(self, *args, **kwargs):
        pass

    def __exit__(self, *args, **kwargs):
        pass

    def get_pipeline_config(self, *args, **kwargs):
        return {}

    def get_document(self, *args, **kwargs):
        return {}

    def __init__(self):
        self.display_error = False
        for func in self.attributs:
            setattr(self, func, self)
        for func in self.func:
            setattr(self, func, self.generic)
        super(MockDB, self).__init__()
        self._done = []

    def generic(self, *args, **kwargs):
        return self

    def update(self, cfg):
        self.cfg = cfg


    def get_report(self, run_id, collection, key):
        if key == 'del':
            return [{'fname': 'd1'}, {'fname': 'd2'}]
        return {
            'marks': 1
        }

    def update_process_report(self, *args, **kwargs):
        pass

    def update_done(self, *args, **kwargs):
        self._done.extend(args[1])

    def test_updated_done(self, done):
        to_return = []
        for d in done:
            res = d.split('\t')
            to_return.append({
                'gbd_collection': 'foo',
                'archive_name': res[1],
                'run_id': res[2],
                'process_date': 'toto'
            })
        self._done=to_return

    def get_done(self, *args, **kwargs):
        return self._done

    def params(self, name, value):
        setattr(self, name, value)

    def create_pypers_config_schema(self):
        return

    def get_step_config(self, *args, **kwargs):
        return self.cfg

    def has_step_config_changed(self, *args, **kwargs):
        return self.step_changed

    def create_step_config(self, *args, **kwargs):
        return

    def send_raw_email(self, *args, **kwargs):
        return

    def has_step_run(self, *args, **kwargs):
        return self.step_run

    def get_run_id_config(self, *args, **kwargs):
        return self.run_config

    def set_step_output(self, *args, **kwargs):
        return args[3]


mockde_db = MockDB()


def mock_db(*args, **kwargs):
    return mockde_db


mocked_logger = MockDBLogger()


def mock_logger(*args, **kwargs):
    return mocked_logger

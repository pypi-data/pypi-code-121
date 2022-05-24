import unittest
from pypers.steps.index.notify import Notify
from pypers.test import captured_output
from pypers.utils.utils import dict_update
import os
import shutil
import json
import copy
import smtplib
import paramiko
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock


class MockSMTP:
    def __init__(self, server):
        self.result = None

    def close(self):
        pass

    def sendmail(self, f, t, m):
        print("%s %s %s" % (f, t, m))


class FtpMock:

    defined_generic_func = ['load_system_host_keys', 'connect', 'close']

    def __init__(self, *args, **kwargs):
        for func in self.defined_generic_func:
            setattr(self, func, self._generic)

    def _generic(self, *args ,**kwargs):
        pass

    def exec_command(self, cmd):
        print(cmd)


class TestLoad(unittest.TestCase):
    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.index.notify.Notify',
        'sys_path': None,
        'name': 'notify',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {

                },
                'output_dir': path_test,
                'collection': 'ROROnotifytm',
                'run_id': 1,
                'log_dir': path_test
            },
            'step': {}
        },
    }

    extended_cfg = {
        'processed_list': ['a1.zip', 'a2.zip'],
        'report_file': [],
        'del_file': [],
        'recipients': ['unit_test@wipo.int'],
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        self.old_sftp = paramiko.SSHClient
        paramiko.SSHClient = FtpMock
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        report = {
            'marks': 1
        }

        deleted = [{'fname': 'd1'}, {'fname': 'd2'}]
        report_file = os.path.abspath(os.path.join(self.path_test,
                                                   'report.json'))
        deleted_file = os.path.abspath(os.path.join(self.path_test,
                                                    'del.json'))
        with open(report_file, 'w') as f:
            f.write(json.dumps(report))
        with open(deleted_file, 'w') as f:
            f.write(json.dumps(deleted))
        os.environ['PYPERS_HOME'] = os.path.abspath(
            os.path.join(self.path_test,  '..', '..', '..'))
        self.extended_cfg['report_file'] = [report_file]
        self.extended_cfg['del_file'] = [deleted_file]

        self.cfg = dict_update(self.cfg, self.extended_cfg)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def tearDown(self):
        paramiko.SSHClient = self.old_sftp

        try:
            shutil.rmtree(self.path_test)
            pass
        except Exception as e:
            pass

    @patch("boto3.client", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.run_config = {}
        mockde_db.update(self.cfg)
        step = Notify.load_step("test", "test", "step")
        smtplib.SMTP = MockSMTP
        with captured_output() as (out, err):
            step.process()
            output = out.getvalue().strip()
        output = output.split('\n')[0]

    @patch("boto3.client", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process2(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.run_config = {}
        mockde_db.update(tmp)
        tmp['server'] = 'gbd.wip.int'
        step = Notify.load_step("test", "test", "step")
        with captured_output() as (out, err):
            step.process()
            output = out.getvalue().strip()
        output = output.split('\n')[0]

    @patch("boto3.client", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_proces3(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.run_config = {}
        mockde_db.update(tmp)
        tmp['recipients'] = []
        step = Notify.load_step("test", "test", "step")
        with captured_output() as (out, err):
            step.process()
            output = out.getvalue().strip()
        output = output.split('\n')[0]


if __name__ == "__main__":
    unittest.main()

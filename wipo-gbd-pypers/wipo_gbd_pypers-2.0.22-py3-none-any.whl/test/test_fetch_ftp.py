import unittest
from pypers.steps.fetch.download.ftp import FTP
from pypers.utils.utils import dict_update
import os
import shutil
import copy
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import ftplib
from pypers.utils import ftpw

return_fail = False



def mock_validate(*args, **kwargs):
    return True


class FtpMock:

    defined_generic_func = ['login', 'cwd', 'close', 'setsockopt',
                            'retrlines', 'set_debuglevel', 'voidcmd',
                            'set_missing_host_key_policy',
                            'set_pasv', 'quit']

    def __init__(self, mock_sock=True, *args, **kwargs):
        if mock_sock:
            self.sock = FtpMock(mock_sock=False)
        for func in self.defined_generic_func:
            setattr(self, func, self._generic)

    def _generic(self, *args, **kwargs):
        pass

    def exec_command(self, cmd):
        print(cmd)

    def walk(self, *args, **kwargs):
        to_return_files = ['archive%s.zip' % i for i in range(0, 10)]
        return [('foo', to_return_files)]

    def retrbinary(self, *args, **kwargs):
        global return_fail
        if return_fail:
            return ''
        return '226 '


class TestLire(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.fetch.download.ftp.FTP',
        'sys_path': None,
        'name': 'FTP',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {
                    'done_file': os.path.join(path_test, 'done.done'),
                    'from_dir': os.path.join(path_test, 'from_dir'),
                },
                'run_id': 1,
                'log_dir': path_test
            },
            'step': {},
        },
        'output_dir': path_test
    }

    extended_cfg = {
        'limit': 0,
        'file_regex': ".*.zip",
        'ftp_dir': 'ftp/',
        'sleep_secs': 0
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        self.old_ftp = ftplib.FTP
        self.old_ftp_walk = ftpw.FTPWalk
        ftpw.FTPWalk = FtpMock
        ftplib.FTP = FtpMock
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        os.makedirs(os.path.join(self.path_test, 'from_dir'))
        with open(os.path.join(self.path_test, 'done.done'), 'w') as f:
            f.write('0\t../foo/archive1.zip\ttoto\t')
        for i in range(0, 10):
            with open(os.path.join(self.path_test,
                                   'from_dir', 'archive%s.zip' % i), 'w') as f:
                f.write('toto')
        self.cfg = dict_update(self.cfg, self.extended_cfg)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def tearDown(self):
        ftplib.FTP = self.old_ftp
        ftpw.FTPWalk = self.old_ftp_walk
        try:
            shutil.rmtree(self.path_test)
            pass
        except Exception as e:
            pass

    @patch("pypers.utils.utils.validate_archive", MagicMock(side_effect=mock_validate))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = FTP.load_step("test", "test", "step")
        step.process()
        for i in range(0, 10):
            if i == 1:
                continue
            archive = os.path.join(self.path_test, 'from_dir',
                                   'archive%s.zip' % i)
            self.assertTrue(archive in step.output_files)

    @patch("pypers.utils.utils.validate_archive", MagicMock(side_effect=mock_validate))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process_exception(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['meta']['pipeline']['input'].pop('from_dir')
        step = FTP.load_step("test", "test", "step")
        try:
            step.process()
            self.fail('Should rise exception because no input is given')
        except Exception as e:
            pass

    @patch("pypers.utils.utils.validate_archive", MagicMock(side_effect=mock_validate))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process_from_ftp(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['meta']['pipeline']['input'].pop('from_dir')
        tmp['meta']['pipeline']['input']['from_ftp'] = {
            'ftp_user': 'toto',
            'ftp_passwd': 'password',
            'ftp_server': 'localhost'
        }
        step = FTP.load_step("test", "test", "step")
        step.process()
        for i in range(0, 10):
            if i == 1:
                continue
            archive = os.path.join(self.path_test, '..', 'foo',
                                   'archive%s.zip' % i)
            self.assertTrue(archive in step.output_files)

    @patch("pypers.utils.utils.validate_archive", MagicMock(side_effect=mock_validate))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process_from_ftp_exception(self):
        global return_fail
        return_fail = True
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['meta']['pipeline']['input'].pop('from_dir')
        tmp['meta']['pipeline']['input']['from_ftp'] = {
            'ftp_user': 'toto',
            'ftp_passwd': 'password',
            'ftp_server': 'localhost'
        }
        step = FTP.load_step("test", "test", "step")
        try:
            step.process()
            self.fail("FAIL because the downlaod was not ok")
        except Exception as e:
            return_fail = False

    @patch("pypers.utils.utils.validate_archive", MagicMock(side_effect=mock_validate))
    @patch('subprocess.check_call', MagicMock(return_value=None))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process_from_wget(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['meta']['pipeline']['input'].pop('from_dir')
        tmp['meta']['pipeline']['input']['from_ftp'] = {
            'ftp_user': 'toto',
            'ftp_passwd': 'password',
            'ftp_server': 'localhost'
        }
        tmp['use_wget'] = 1
        step = FTP.load_step("test", "test", "step")
        step.process()
        for i in range(0, 10):
            if i == 1:
                continue
            archive = os.path.join(self.path_test, '..', 'foo',
                                   'archive%s.zip' % i)
            self.assertTrue(archive in step.output_files)


if __name__ == "__main__":
    unittest.main()

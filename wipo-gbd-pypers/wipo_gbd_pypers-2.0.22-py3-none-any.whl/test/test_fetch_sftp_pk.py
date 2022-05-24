import unittest
from pypers.steps.fetch.download.sftp_pk import SFTP_PK
from pypers.utils.utils import dict_update
import os
import shutil
import copy
import paramiko
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock

return_fail = False


class MockFileSSH:

    def __init__(self, name, mode):
        self.filename = name
        self.st_mode = mode
        self.st_mtime = 100


class FtpMock:

    defined_generic_func = ['login', 'cwd', 'close', 'setsockopt',
                            'retrlines', 'set_debuglevel', 'voidcmd',
                            'set_pasv', 'quit', 'load_system_host_keys',
                            'connect', 'chdir', 'get',
                            'set_missing_host_key_policy']

    def __init__(self, mock_sock=True, *args, **kwargs):
        if mock_sock:
            self.sock = FtpMock(mock_sock=False)
        for func in self.defined_generic_func:
            setattr(self, func, self._generic)

    def _generic(self, *args, **kwargs):
        pass

    def stat(self, *args, **kwargs):
        return MockFileSSH('a', 0)

    def open_sftp(self, *args, **kwargs):
        return FtpMock()

    def listdir_attr(self, *args, **kwargs):
        if 'Others' in args[0]:
            return []
        mode_dir = 0o040000 & 0o170000
        to_return_files = [MockFileSSH('archive%s.zip' % i, 0)
                           for i in range(0, 10)]
        to_return_files.append(MockFileSSH("Others", mode_dir))
        return to_return_files

    def retrbinary(self, *args, **kwargs):
        global return_fail
        if return_fail:
            return ''
        return '226 '


def mock_validate(*args, **kwargs):
    return True


class TestLire(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.fetch.download.sftp_pk.SFTP_PK',
        'sys_path': None,
        'name': 'SFTP_PK',
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
        'sleep_secs': 0
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        self.old_sftp_proxy = paramiko.proxy.ProxyCommand
        self.old_sftp_transport = paramiko.Transport
        self.old_sftp_client = paramiko.SFTPClient.from_transport
        self.ssh_clinet = paramiko.SSHClient

        paramiko.proxy.ProxyCommand = FtpMock
        paramiko.Transport = FtpMock
        paramiko.SFTPClient.from_transport = FtpMock
        paramiko.SSHClient = FtpMock
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        os.makedirs(os.path.join(self.path_test, 'from_dir'))
        with open(os.path.join(self.path_test, 'done.done'), 'w') as f:
            f.write('0\tarchive1.zip\ttoto\t')
        for i in range(0, 10):
            with open(os.path.join(self.path_test,
                                   'from_dir', 'archive%s.zip' % i), 'w') as f:
                f.write('toto')
        self.cfg = dict_update(self.cfg, self.extended_cfg)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def tearDown(self):
        paramiko.proxy.ProxyCommand = self.old_sftp_proxy
        paramiko.Transport = self.old_sftp_transport
        paramiko.SFTPClient.from_transport = self.old_sftp_client
        paramiko.SSHClient = self.ssh_clinet
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
        step = SFTP_PK.load_step("test", "test", "step")
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
        step = SFTP_PK.load_step("test", "test", "step")
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
        tmp['meta']['pipeline']['input']['from_sftp'] = {
            'sftp_user': 'toto',
            'sftp_dir': '/',
            'sftp_server': 'localhost',
            'sftp_proxy': 'localhost',
            'sftp_port': '22',
            'sftp_pkey': 'password',
            'sftp_phrase': 'password'

        }
        step = SFTP_PK.load_step("test", "test", "step")
        step.process()
        for i in range(0, 10):
            if i == 1:
                continue
            archive = os.path.join(self.path_test,
                                   'archive%s.zip' % i)
            self.assertTrue(archive in step.output_files)


if __name__ == "__main__":
    unittest.main()

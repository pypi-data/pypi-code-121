import unittest
from pypers.steps.fetch.common.cleanup import Cleanup
from pypers.utils.utils import dict_update
import os
import shutil
import copy
import ftplib
import paramiko
from pypers.test import mock_db, mockde_db, mock_logger

from mock import patch, MagicMock


class FtpMock:

    defined_generic_func = ['login', 'cwd', 'delete', 'quit',
                            'load_system_host_keys', 'connect', 'chdir',
                            'remove', 'close']

    def __init__(self, *args, **kwargs):
        for func in self.defined_generic_func:
            setattr(self, func, self._generic)

    def _generic(self, *args ,**kwargs):
        pass

    def open_sftp(self, *args, **kwargs):
        return FtpMock()


class TestCleanup(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.fetch.common.cleanup.Cleanup',
        'sys_path': None,
        'name': 'clean',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {
                    'from_dir': path_test,
                    'done_file': os.path.join(path_test, 'done.file')
                },
                'run_id': 1
            },
            'step': {}
        },
        'output_dir': path_test,
    }

    extended_cfg = {
        'remove_orig': 0,
        'extracted_list': [{}],
        'del_list': ['T0102', 'T0202'],
        'archive_names': [{}],
        'reset_done': 1,
        'processed_dir': os.path.join(path_test, '0', '__processed'),
        'store_archives': 1,
        'processed_list': [],
        'processing_done': [os.path.join(path_test, 'release')]

    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        self.old_ftp = ftplib.FTP
        self.old_sftp = paramiko.SSHClient
        ftplib.FTP = FtpMock
        paramiko.SSHClient = FtpMock
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)

        # Create the env
        archives_folder = os.path.join(self.path_test, 'archives')
        os.makedirs(archives_folder)
        os.makedirs(self.extended_cfg['processing_done'][0])
        self.extended_cfg['processed_list'] = []
        self.extended_cfg['extracted_list'] = []
        self.extended_cfg['archive_names'] = []
        for i in range(0, 10):
            archive_name = 'archive_%s.zip' % i

            self.extended_cfg['processed_list'].append(
                os.path.join(archives_folder, archive_name)
            )
            with open(os.path.join(archives_folder, archive_name), 'w') as f:
                f.write('12345')
            self.extended_cfg['extracted_list'] = {}
            for j in range(0, 10):
                self.extended_cfg['extracted_list']["F%s%s" % (i, j)] = {
                    'appnum': "F%s%s" % (i, j),
                     'img': ["I%s%s%s" % (i, j, k) for k in range(0, 10)]
                 }
            self.extended_cfg['extracted_list'] = [self.extended_cfg['extracted_list']]
            self.extended_cfg['archive_names'].append({'2020-05': archive_name})

        self.cfg = dict_update(self.cfg, self.extended_cfg)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def tearDown(self):
        ftplib.FTP = self.old_ftp
        paramiko.SSHClient = self.old_sftp
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_done_file_manager", MagicMock(side_effect=mock_db))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Cleanup.load_step('test', 'test', 'step')
        self.assertEqual(step._get_common_path('/root/path1/path2/path3/path4',
                                               '/root/path1/path2/path5/path6'),
                         '/root/path1/path2')
        step.process()
        self.assertTrue(os.path.exists(os.path.join(self.path_test,
                                                    'archives')))

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_done_file_manager", MagicMock(side_effect=mock_db))
    def test_process_with_no_proceesed_list(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['processed_list'] = []
        mockde_db.update(tmp)
        step = Cleanup.load_step('test', 'test', 'step')
        step.process()

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_done_file_manager", MagicMock(side_effect=mock_db))
    def test_process_with_remove_origin(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['remove_orig'] = 1
        mockde_db.update(tmp)
        step = Cleanup.load_step('test', 'test', 'step')
        step.process()
        self.assertTrue(os.path.exists(os.path.join(self.path_test,
                                                    'archives')))
        self.assertEqual(os.listdir(os.path.join(self.path_test,
                                                 'archives')), [])

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_done_file_manager", MagicMock(side_effect=mock_db))
    def test_from_ftp(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['remove_orig'] = 1
        tmp['meta']['pipeline']['input'].pop('from_dir', None)
        tmp['meta']['pipeline']['input']['from_ftp'] = {
            'ftp_server': 'toto',
            'ftp_user': 'toto',
            'ftp_passwd': 'toto',
            'ftp_dir': 'toto'
        }
        tmp['meta']['pipeline']['input']['from_sftp'] = {
            'sftp_server': 'toto',
            'sftp_dir': 'toto'
        }
        mockde_db.update(tmp)
        step = Cleanup.load_step('test', 'test', 'step')
        step.process()
        self.assertTrue(os.path.exists(os.path.join(self.path_test,
                                                    'archives')))

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_done_file_manager", MagicMock(side_effect=mock_db))
    def test_without_store(self):
        tmp = copy.deepcopy(self.cfg)
        from pprint import pprint
        pprint(tmp['archive_names'])
        mockde_db.update(tmp)
        tmp['remove_orig'] = 1
        tmp['meta']['pipeline']['input'].pop('from_dir', None)
        tmp['meta']['pipeline']['input']['from_ftp'] = {
            'ftp_server': 'toto',
            'ftp_user': 'toto',
            'ftp_passwd': 'toto',
            'ftp_dir': 'toto'
        }
        tmp['meta']['pipeline']['input']['from_sftp'] = {
            'sftp_server': 'toto',
            'sftp_dir': 'toto'
        }
        tmp['store_archives'] = 0
        mockde_db.update(tmp)
        step = Cleanup.load_step('test', 'test', 'step')
        step.process()
        self.assertTrue(os.path.exists(os.path.join(self.path_test,
                                                    'archives')))


if __name__ == "__main__":
    unittest.main()

import unittest
from pypers.steps.fetch.download.rss import RSS
from pypers.utils.utils import dict_update
import os
import shutil
import copy
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
from pypers.utils import download


def mock_validate(*args, **kwargs):
    return True

class MockStream:

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def read(self):
        return '''<?xml version='1.0'?>
            <channels>
                <channel>
                  <item>
                    <link>http://foo.bar/archive0.zip</link>
                  </item>
                  <item>
                    <link>http://foo.bar/archive1.zip</link>
                  </item>
                </channel>
               
            </channels>
            '''.encode('utf-8')

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def close(self):
        pass


def mock_download(*args, **kwargs):
    return MockStream()


class TestCHTM(unittest.TestCase):
    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.fetch.download.rss.RSS',
        'sys_path': None,
        'name': 'RSS',
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
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        self._old_download = download.download
        download.download = mock_download
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
        download.download = self._old_download
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
        step = RSS.load_step("test", "test", "step")
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
        step = RSS.load_step("test", "test", "step")
        try:
            step.process()
            self.fail('Should rise exception because no input is given')
        except Exception as e:
            pass

    @patch("pypers.utils.utils.validate_archive", MagicMock(side_effect=mock_validate))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process_from_web(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['meta']['pipeline']['input'].pop('from_dir')
        tmp['meta']['pipeline']['input']['from_url'] = {
            'from_url': 'http://my_url.url.com'
        }

        step = RSS.load_step("test", "test", "step")
        step.process()
        self.assertTrue(os.path.exists(step.output_files[0]))


if __name__ == "__main__":
    unittest.main()

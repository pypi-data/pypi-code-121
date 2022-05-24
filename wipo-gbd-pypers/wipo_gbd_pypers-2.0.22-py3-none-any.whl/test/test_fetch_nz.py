import unittest
from pypers.steps.fetch.download.nz import NZ
from pypers.utils.utils import dict_update
import os
import shutil
import copy
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import datetime


class MockStream:

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def read(self, *args, **kwargs):
        return ''


class MockPage:

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __init__(self, no_content=False):
        self.content = []
        self.status_code = 200
        if not no_content:
            self.content = '''<?xml version='1.0'?>
            <AppplicationNumbers>
              <AppplicationNumber>
                <FromDate>2018-01-01</FromDate>
                <nom>Dupond</nom>
              </AppplicationNumber>
            </AppplicationNumbers>
            '''

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __exit__(self, *args, **kwargs):
        pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __enter__(self, *args, **kwargs):
        pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def iter_content(self, *args, **kwargs):
        return 'toto'


no_content = 0


def side_effect_mock_page(*args, **kwargs):
    global no_content
    no_content += 1
    return MockPage(no_content=no_content > 3)


class TestLire(unittest.TestCase):
    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.fetch.download.nz.NZ',
        'sys_path': None,
        'name': 'NZ',
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
        'api': 'foo.php?interval=%s',
        'token': '12234',
        'file_regex': ".*.zip",
        'id_tagname': "AppplicationNumber"
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        os.makedirs(os.path.join(self.path_test, 'from_dir'))
        mock_db().test_updated_done(['0\tarchive1.zip\ttoto\t'])
        for i in range(0, 10):
            with open(os.path.join(self.path_test,
                                   'from_dir', 'archive%s.zip' % i), 'w') as f:
                f.write('toto')
        self.cfg = dict_update(self.cfg, self.extended_cfg)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def tearDown(self):
        mock_db().test_updated_done([])
        try:
            shutil.rmtree(self.path_test)
            pass
        except Exception as e:
            pass

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_done_file_manager", MagicMock(side_effect=mock_db))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = NZ.load_step("test", "test", "step")
        step.process()
        for i in range(0, 10):
            if i == 1:
                continue
            archive = os.path.join(self.path_test, 'from_dir',
                                   'archive%s.zip' % i)
            self.assertTrue(archive in step.output_files)

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_done_file_manager", MagicMock(side_effect=mock_db))
    def test_process_exception(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['meta']['pipeline']['input'].pop('from_dir')
        step = NZ.load_step("test", "test", "step")
        try:
            step.process()
            self.fail('Should rise exception because no input is given')
        except Exception as e:
            pass

    @patch("requests.sessions.Session.get",
           MagicMock(side_effect=side_effect_mock_page))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_done_file_manager", MagicMock(side_effect=mock_db))
    def test_process_from_web(self):
        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        yesterday = yesterday.strftime('%Y%m%d')
        mock_db().test_updated_done(['0\t20180107-%s\ttoto\t' % yesterday])
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['meta']['pipeline']['input'].pop('from_dir')
        tmp['meta']['pipeline']['input']['from_api'] = {
            'token': '12234',
            'url': 'http://my_url.url.com'
        }

        step = NZ.load_step("test", "test", "step")
        step.process()
        self.assertTrue(os.path.exists(step.output_files[0]))


if __name__ == "__main__":
    unittest.main()

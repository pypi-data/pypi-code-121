import unittest
from pypers.steps.fetch.download.chtm import CHTM
from pypers.utils.utils import dict_update
import os
import shutil
import copy
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import datetime


class MockPage:

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __init__(self, raw=False):
        self.content = '''<?xml version = "1.0"?>
<SOAP-ENV:Envelope
   xmlns:SOAP-ENV = "http://www.w3.org/2001/12/soap-envelope"
   SOAP-ENV:encodingStyle = "http://www.w3.org/2001/12/soap-encoding">
   <SOAP-ENV:Body xmlns:m = "http://www.xyz.org/">
          <searchModifiedIpRightReturn>ff00,ff01,ff02</searchModifiedIpRightReturn>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __exit__(self, *args, **kwargs):
        pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __enter__(self, *args, **kwargs):
        pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def iter_content(self, *args, **kwargs):
        return 'toto'


def side_effect_mock_page(*args, **kwargs):
    return MockPage(raw=('stream' in kwargs))


class TestCHTM(unittest.TestCase):
    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.fetch.download.chtm.CHTM',
        'sys_path': None,
        'name': 'CHTM',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {
                    'done_file': os.path.join(path_test, 'done.done'),
                    'from_api': {
                        'credentials': {
                            'user': 'toto',
                            'password': 'password'
                        },
                        'url': 'http://my_url.url.com'
                    }
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
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        os.makedirs(os.path.join(self.path_test, 'from_dir'))
        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        yesterday = yesterday.strftime('%Y-%m-%d')
        mock_db().test_updated_done(['0\t2018-01-07.TO.%s.zip\ttoto\t' % yesterday])
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
    def test_process_today(self):
        tdoay = datetime.datetime.today()
        tdoay = tdoay.strftime('%Y-%m-%d')
        mock_db().test_updated_done(['0\t2018-01-07.TO.%s.zip\ttoto\t' % tdoay])
        step = CHTM.load_step("test", "test", "step")
        step.process()
        self.assertEqual(step.output_files, [])

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process_exception(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['meta']['pipeline']['input'].pop('from_api')
        step = CHTM.load_step("test", "test", "step")
        try:
            step.process()
            self.fail('Should rise exception because no input is given')
        except Exception as e:
            pass

    @patch("requests.sessions.Session.post",
           MagicMock(side_effect=side_effect_mock_page))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_done_file_manager", MagicMock(side_effect=mock_db))
    def test_process_from_web(self):
        mockde_db.update(self.cfg)
        step = CHTM.load_step("test", "test", "step")
        step.process()



if __name__ == "__main__":
    unittest.main()

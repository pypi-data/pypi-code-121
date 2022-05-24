import unittest
from pypers.steps.fetch.common.pdf2imgs import PDF2IMGs
from pypers.test import copy_files_to_path
from pypers.utils.utils import dict_update
import os
import shutil
import copy
from pypers.test import mock_db, mockde_db, mock_logger

from mock import patch, MagicMock


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.fetch.common.pdf2imgs.PDF2IMGs',
        'sys_path': None,
        'name': 'pdf2imgs',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {

                },
                'run_id': 1,
                'log_dir': path_test
            },
            'step': {},
        },
        'output_dir': path_test
    }

    extended_cfg = {
        'input_data': [
            {'no_pdf': 'no_pdf'},
            {'pdf': 'indexisting/path'},
            {'pdf': os.path.join(path_test, 'test.pdf'),
             'appnum': 'fff0010'}
        ],
        'input_dir': path_test,
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        copy_files_to_path(os.path.join(self.path_test, 'test.pdf'),
                           'test1.pdf')
        self.cfg = dict_update(self.cfg, self.extended_cfg)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def tearDown(self):
        try:
            shutil.rmtree(self.path_test)
            pass
        except Exception as e:
            pass

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = PDF2IMGs.load_step("test", "test", "step")
        step.process()
        self.assertEqual(len(os.listdir(self.path_test)), 75)

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process2(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['input_data'] = []
        step = PDF2IMGs.load_step("test", "test", "step")
        step.process()
        self.assertEqual(len(os.listdir(self.path_test)), 1)


if __name__ == "__main__":
    unittest.main()

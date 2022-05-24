import unittest
from pypers.steps.harmonize.organize import Organize
from pypers.utils.utils import dict_update
import os
import shutil
from pypers.test import mock_db, mockde_db, mock_logger

from mock import patch, MagicMock


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.harmonize.organize.Organize',
        'sys_path': None,
        'name': 'organize',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {

                },
                'output_dir': path_test,
                'run_id': 1,
                'log_dir': path_test
            },
            'step': {},
        },
        'output_dir': path_test
    }

    extended_cfg = {
        'data_files': {},
        'img_files': {},
        'archive_name': '',
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_pre_prod_db_history", MagicMock(side_effect=mock_db))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        self.cfg = dict_update(self.cfg, self.extended_cfg)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_pre_prod_db_history", MagicMock(side_effect=mock_db))
    def tearDown(self):
        try:
            shutil.rmtree(self.path_test)
            pass
        except Exception as e:
            pass

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_pre_prod_db_history", MagicMock(side_effect=mock_db))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Organize.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()

import unittest
from pypers.steps.harmonize.merge import Merge
from pypers.utils.utils import dict_update
import os
import json
import shutil
from pypers.test import mock_db, mockde_db, mock_logger

from mock import patch, MagicMock


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.harmonize.merge.Merge',
        'sys_path': None,
        'name': 'load',
        'meta': {
            'job': {},
            'pipeline': {
                'output_dir': path_test,
                'input': {

                },
                'run_id': 1,
                'log_dir': path_test
            },
            'step': {}
        },
    }

    extended_cfg = {
        'appnums_per_archive': [{'f01': {'path': os.path.join(path_test, 'archive_1'), 'time': 'foo'}}],
        'merged_dir': None,
        'to_dir': '',
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        self.extended_cfg['input_dirs'] = [
            os.path.abspath(os.path.join(self.path_test, 'input', 'dir%s' % i))
            for i in range(0, 10)
        ]
        self.extended_cfg['to_dir'] = os.path.abspath(
            os.path.join(self.path_test, 'out'))
        os.mkdir(os.path.join(self.path_test, '_cache'))
        with open(os.path.join(self.path_test, '_cache', 'test_f01_foo.json'), 'w') as f:
            json.dump({}, f)
        with open(os.path.join(self.path_test, 'archive_1'), 'w') as f:
            json.dump({}, f)
        for idx, path in enumerate(self.extended_cfg['input_dirs']):
            os.makedirs(path)
            with open(os.path.join(path, 'f%s' % idx), 'w') as f:
                f.write('toto')
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
    @patch("pypers.core.interfaces.db.get_pre_prod_db", MagicMock(side_effect=mock_db))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Merge.load_step("test", "test", "step")
        step.process()

if __name__ == "__main__":
    unittest.main()

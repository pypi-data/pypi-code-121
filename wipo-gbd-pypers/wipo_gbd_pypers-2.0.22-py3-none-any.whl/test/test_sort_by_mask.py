import unittest
from pypers.steps.fetch.sort.by_mask import SortByMask
from pypers.utils.utils import dict_update
import os
import shutil
from random import shuffle
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock


class TestLoad(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.fetch.sort.by_mask.SortByMask',
        'sys_path': None,
        'name': 'SortByMask',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {

                },
                'run_id': 1,
                'log_dir': path_test
            },
            'step': {}
        },
    }

    extended_cfg = {
        'input_files': [],
        'mask_input': '.*(\d{1})',
        'mask_output': r'\1',
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        self.extended_cfg['input_files'].extend(
            ['foo/bar/filename%s.xml' % i
             for i in range(0, 10)]
        )
        shuffle(self.extended_cfg['input_files'])
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
        step = SortByMask.load_step("test", "test", "step")
        step.process()
        expected = [{0: 'foo/bar/filename0.xml'},
                    {1: 'foo/bar/filename1.xml'},
                    {2: 'foo/bar/filename2.xml'},
                    {3: 'foo/bar/filename3.xml'},
                    {4: 'foo/bar/filename4.xml'},
                    {5: 'foo/bar/filename5.xml'},
                    {6: 'foo/bar/filename6.xml'},
                    {7: 'foo/bar/filename7.xml'},
                    {8: 'foo/bar/filename8.xml'},
                    {9: 'foo/bar/filename9.xml'}]
        self.assertEqual(step.output_files, expected)


if __name__ == "__main__":
    unittest.main()

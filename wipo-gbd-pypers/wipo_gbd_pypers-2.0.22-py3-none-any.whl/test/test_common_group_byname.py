import unittest
from pypers.steps.fetch.common.group_byname import GroupByName
from pypers.utils.utils import dict_update
import os
import shutil
from pypers.test import mock_db, mockde_db, mock_logger

from mock import patch, MagicMock


class TestCleanup(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.fetch.common.group_byname.GroupByName',
        'sys_path': None,
        'name': 'group_byname',
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
        'output_files': [],

    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)

        self.extended_cfg['input_files'].extend(
            [{'file%s.zip' % i: '/path/to/file%s%s' % (i, j)}
             for i in range(0, 10) for j in range(0, 10)]
        )

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
        step = GroupByName.load_step('test', 'test', 'step')
        step.process()
        for el in step.output_files:
            for key in el.keys():
                for filename in el[key]:
                    self.assertTrue(filename.startswith(
                        '/path/to/' + key.split('.')[0]))


if __name__ == "__main__":
    unittest.main()

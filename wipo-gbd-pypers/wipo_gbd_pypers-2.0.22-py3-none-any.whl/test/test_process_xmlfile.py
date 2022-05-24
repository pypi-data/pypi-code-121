import unittest
from pypers.steps.harmonize.transform import Transform
from pypers.utils.utils import dict_update
import os
import shutil
import copy
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock


class TestLire(unittest.TestCase):
    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.harmonize.transform.Transform',
        'sys_path': None,
        'name': 'ProcessXML',
        'meta': {
            'job': {},
            'pipeline': {
                'output_dir': path_test,
                'collection': 'uatm',
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
        'data_files': {
            '0010': {
                'ori': os.path.join(path_test, 'F0234.xml')
            },
            '0012': {
                'ori': os.path.join(path_test, 'F0235.xml')
            }
        },
        'extraction_dir': path_test,
        'archive_name': "xml_test",
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        for appnum, el in copy.deepcopy(self.extended_cfg['data_files']).items():
            xml_path = el
            xml_path = os.path.join(self.path_test, xml_path['ori'])
            with open(xml_path, 'w') as f:
                f.write('<document></document>')
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
        step = Transform.load_step("test", "uatm", "step")
        step.process()

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process_no_timestamp(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        step = Transform.load_step("test", "uatm", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()

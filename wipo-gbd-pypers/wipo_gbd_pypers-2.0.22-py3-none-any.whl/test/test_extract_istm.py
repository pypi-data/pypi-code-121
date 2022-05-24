import unittest
from pypers.steps.fetch.extract.is_.trademarks import Trademarks
from pypers.utils.utils import dict_update
import os
import shutil
import json
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.is_.trademarks.Trademarks',
        'sys_path': None,
        'name': 'ISTM',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {
                    'from_web': {
                        'credentials': {
                            'user': 'toto',
                            'password': 'password'
                        }
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
        'input_json': [os.path.join(path_test, 'toto.json')],
        'img_ref_dir': path_test
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        payload = [{
            'vmid': 'F01',
            'applicationNumber': '0',
        }, {
            'vmid': 'F02',
            'applicationNumber': '20',
            'orginalImagePath': self.path_test,
        },
        ]
        for fin in self.extended_cfg['input_json']:
            with open(fin, 'w') as f:
                f.write(json.dumps(payload))

        img_alreday = os.path.join(self.path_test, '01', '20')
        os.makedirs(img_alreday)
        img_alreday = os.path.join(img_alreday, '120.foooo.high.png')
        with open(img_alreday, 'w') as f:
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
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Trademarks.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()

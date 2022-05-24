import unittest
from pypers.steps.fetch.extract.ua.trademarks import Trademarks
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil
import json


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.ua.trademarks.Trademarks',
        'sys_path': None,
        'name': 'Trademarks',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {
                    'from_api': {
                        'token': '12234',
                        'url': 'http://my_url.url.com'
                    }

                },
                'run_id': 1,
                'log_dir': path_test
            },
            'step': {},
        },
        'output_dir': os.path.join(path_test, 'out')
    }

    extended_cfg = {
        'input_archive': [os.path.join(path_test, 'toto')],
        'img_ref_dir': path_test
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        os.makedirs(os.path.join(self.path_test, 'out'))

        payload = [{
            'app_number': 'F01',
            'applicationNumber': '0',
            'data': {
                'MarkImageDetails': {
                    'MarkImage': {
                        'MarkImageFilename': ''
                    }
                }
            }
        }, {
            'app_number': 'F02',
            'applicationNumber': '20',
            'data': {
                'MarkImageDetails': {
                    'MarkImage': {
                        'MarkImageFilename': self.path_test
                    }
                }
            },
        },
        ]
        for fin in self.extended_cfg['input_archive']:
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

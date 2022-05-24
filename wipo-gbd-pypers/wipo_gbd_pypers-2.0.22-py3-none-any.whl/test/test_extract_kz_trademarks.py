import unittest
from pypers.steps.fetch.extract.kz.trademarks import Trademarks
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil

mock_get_value_counter = 0


def mock_get_nodevalue(*args, **kwargs):
    global mock_get_value_counter
    if args[0] == 'inid_210':
        r = '102'
    else:
        r = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/' \
            '5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
    mock_get_value_counter = 1
    return r


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.kz.trademarks.Trademarks',
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
        'output_dir': path_test
    }

    extended_cfg = {
        'input_archives': [{'toto': os.path.join(path_test, 'toto.xml')}],
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <U_IDs>
        <U_ID>
          <inid_211>F121-ff</inid_211>
        </U_ID>
        <U_ID>
          <inid_210>F122-ff</inid_210>
          <image>iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/' \
            '5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==</image>
        </U_ID>
        <U_ID>
          <inid_210>F132-ff</inid_210>
        </U_ID>
        </U_IDs>
        '''
        for _, fin in self.extended_cfg['input_archives'][0].items():
            with open(fin, 'w') as f:
                f.write(xml_content)

        path = os.path.join(self.path_test, 'F', '01')
        os.makedirs(path)
        path = os.path.join(path, 'F01-0001.1.high.jpg')
        with open(path, 'w') as f:
            f.write("totot")
        self.cfg = dict_update(self.cfg, self.extended_cfg)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def tearDown(self):
        try:
            shutil.rmtree(self.path_test)
            pass
        except Exception as e:
            pass

    @patch('pypers.utils.xmldom.get_nodevalue',
           MagicMock(side_effect=mock_get_nodevalue))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Trademarks.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()

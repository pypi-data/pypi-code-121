import unittest
from pypers.steps.fetch.extract.us.designs import Designs
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil


def mock_tarextract(source, dest):
    path = os.path.join(dest, 'toto', 'DESIGN')
    os.makedirs(path)
    for i in range(0, 2):
        with open(os.path.join(path, 'USD%s.ZIP' % i), 'w') as f:
            f.write('totot')


def mock_zipextract(source, dest):
    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    if not os.path.exists(dest):
        os.makedirs(dest)
    for i in range(0, 10):
        path = os.path.join(dest, "F010%s.xml" % i)
        with open(path, 'w') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<case-file>
</case-file>
''')
        path = os.path.join(dest, "F010%s-D.jpg" % i)
        with open(path, 'w') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<case-file>
</case-file>
''')


mock_get_value_counter = -1


def mock_get_nodevalue(*args, **kwargs):
    global mock_get_value_counter
    mock_get_value_counter += 1
    if mock_get_value_counter == 0:
        return ''
    return 'F010'


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.us.designs.Designs',
        'sys_path': None,
        'name': 'Designs',
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
        'input_archive': {'toto': os.path.join(path_test, 'toto.zip')},
        'img_ref_dir': path_test,
        'img_dest_dir': [os.path.join(path_test, 'old')],
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        os.environ['PYPERS_HOME'] = os.path.abspath(
            os.path.join(self.path_test,  '..', '..', '..'))
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        for fin in [v for f, v in self.extended_cfg['input_archive'].items()]:
            with open(fin, 'w') as f:
                f.write('toto')
        self.cfg = dict_update(self.cfg, self.extended_cfg)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def tearDown(self):
        try:
            shutil.rmtree(self.path_test)
            pass
        except Exception as e:
            pass

    @patch('pypers.utils.utils.tarextract',
           MagicMock(side_effect=mock_tarextract))
    @patch('pypers.utils.utils.zipextract',
           MagicMock(side_effect=mock_zipextract))
    @patch('pypers.utils.xmldom.get_nodevalue',
           MagicMock(side_effect=mock_get_nodevalue))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Designs.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()

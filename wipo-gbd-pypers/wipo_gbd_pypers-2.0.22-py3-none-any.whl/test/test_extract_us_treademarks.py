import unittest
from pypers.steps.fetch.extract.us.trademarks import Trademarks
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import gzip
import shutil


def mock_zipextract(source, dest):
    path_test = os.path.join(os.path.dirname(__file__), 'foo')

    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<case-file>
  <serial-number>F0%(i)s</serial-number>
  <case-file-header>
    <status-code>F0%(i)s</status-code>
    <mark-drawing-code>%(code)s</mark-drawing-code>
  </case-file-header>
</case-file>'''
    for i in range(0, 10):
        code = 10
        if i == 6:
            code = 1000
        path = os.path.join(dest, "F0%s.xml" % i)
        with open(path, 'w') as f:
            f.write(xml_content % {'i': i,
                                   'code': code})
        path = os.path.join(path_test, 'FF', '0%s' % i)
        os.makedirs(path)
        path = os.path.join(path, 'FF0%s.xml.gz' % i)
        with gzip.open(path, 'wb') as f:
            f.write((xml_content % {'i': i,
                                    'code': code}).encode('utf-8'))
        if i < 6:
            path = os.path.join(dest, "F0%s.jpg" % i)
            with open(path, 'w') as f:
                f.write('toto')
            path = os.path.join(dest, "FF0%s.jpg" % i)
            with open(path, 'w') as f:
                f.write('toto')
    path = os.path.join(dest, "F0100.xml")
    with open(path, 'w') as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<case-file>
</case-file>
''')


mock_get_value_counter = 0


def mock_get_nodevalue(*args, **kwargs):
    global mock_get_value_counter
    res = '12%s' % mock_get_value_counter
    mock_get_value_counter += 1
    return res


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.us.trademarks.Trademarks',
        'sys_path': None,
        'name': 'Trademarks',
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
        'input_archive': {'toto': [os.path.join(path_test, 'toto.zip')]},
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
        path = os.path.join(self.path_test, '0F', '08')
        os.makedirs(path)
        with open(os.path.join(path, 'F08.high.jpg'), 'w') as f:
            f.write('totto')
        self.cfg = dict_update(self.cfg, self.extended_cfg)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def tearDown(self):
        try:
            shutil.rmtree(self.path_test)
            pass
        except Exception as e:
            pass

    @patch('pypers.utils.utils.zipextract',
           MagicMock(side_effect=mock_zipextract))
    @patch('pypers.utils.xmldom.get_nodevalue',
           MagicMock(side_effect=mock_get_nodevalue))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Trademarks.load_step("test", "test", "step")
        step.preprocess()
        step.process()


if __name__ == "__main__":
    unittest.main()

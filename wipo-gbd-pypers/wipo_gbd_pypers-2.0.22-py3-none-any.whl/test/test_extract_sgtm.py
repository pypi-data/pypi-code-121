import unittest
from pypers.steps.fetch.extract.sg.trademarks import Trademarks
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil


nb_calls_zip = -1


def mock_zipextract(source, dest):
    global nb_calls_zip
    nb_calls_zip += 1
    if nb_calls_zip == 0:
        for i in range(0, 2):
            path = os.path.join(dest, 'F0%s.zip' % i)
            with open(path, 'w') as f:
                f.write('totot')
        return
    if nb_calls_zip % 2 == 0:
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <Article6ter>
        <article_6ter_no>F01</article_6ter_no>
        <logo_details>
            <file_name>jpg%s.jpg</file_name>
        </logo_details>
    </Article6ter>
    '''
    else:
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <FOoo>%s
        </FOoo>'''
    if not os.path.exists(dest):
        os.makedirs(dest)
    jpg_dest = os.path.join(dest, 'jpg1.jpg')
    zip_dest = os.path.join(dest, 'zip1.zip')
    for path in [jpg_dest, zip_dest]:
        with open(path, 'w') as f:
            f.write('toto')
    for i in range(0, 5):
        xml_dest = os.path.join(dest, '12%s.xml' % i)
        with open(xml_dest, 'w') as f:
            f.write(xml_content % i)


mock_get_value_counter = 0


def mock_get_nodevalue(*args, **kwargs):
    global mock_get_value_counter
    res = '12%s' % mock_get_value_counter
    mock_get_value_counter += 1
    return res


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.sg.trademarks.Trademarks',
        'sys_path': None,
        'name': 'SGTM',
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
        'img_ref_dir': path_test
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        for fin in [v for f, v in self.extended_cfg['input_archive'].items()]:
            with open(fin, 'w') as f:
                f.write('toto')

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

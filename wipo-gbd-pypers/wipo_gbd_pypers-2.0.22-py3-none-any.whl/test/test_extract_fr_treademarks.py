import unittest
from pypers.steps.fetch.extract.fr.trademarks import Trademarks
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil
import copy


def mock_zipextract(source, dest):
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Transaction xmlns="http://www.inpi.fr/schemas/frst66/v1_00_13">
  <TradeMark>
    <ApplicationNumber>FMARK%(i)s</ApplicationNumber>
    <MarkImageDetails>
        <MarkImage>
          <MarkImageFilename>F0%(i)s</MarkImageFilename>
        </MarkImage>
    </MarkImageDetails>
  </TradeMark>
</Transaction>'''
    for f_name in ['FR_FRNEW', 'FR_FRAMD', 'FR_FRDEL']:
        for i in range(0, 10):
            path = os.path.join(dest, "%sF0%s.xml" % (f_name, i))
            with open(path, 'w') as f:
                if f_name == 'FR_FRNEW':
                    f.write(xml_content % {'i': i})
                else:
                    f.write('''<?xml version="1.0" encoding="UTF-8"?>
<Transaction xmlns="http://www.inpi.fr/schemas/frst66/v1_00_13">
<TradeMark>
    <ApplicationNumber>F0%(i)s</ApplicationNumber>
  </TradeMark>
</Transaction>''' % {'i': i})
            other_xml = os.path.join(dest, '%sE0%s.xml' % (f_name, i))
            with open(other_xml, 'w') as f:
                f.write('''<?xml version="1.0" encoding="UTF-8"?>
            <Transaction>
            </Transaction>
            ''')


def mock_zipextract_global(source, dest):
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Transaction xmlns="http://www.inpi.fr/schemas/frst66/v1_00_13">
  <TradeMark>
    <ApplicationNumber>FMARK%(i)s</ApplicationNumber>
    <MarkImageDetails>
        <MarkImage>
          <MarkImageFilename>F0%(i)s</MarkImageFilename>
        </MarkImage>
    </MarkImageDetails>
  </TradeMark>
</Transaction>'''
    for i in range(0, 10):
        path = os.path.join(dest, "ST66_F0%s.xml" % i)
        with open(path, 'w') as f:
            f.write(xml_content % {'i': i})


mock_get_value_counter = 0


def mock_get_nodevalue(*args, **kwargs):
    global mock_get_value_counter
    res = '12%s' % mock_get_value_counter
    mock_get_value_counter += 1
    return res


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.fr.trademarks.Trademarks',
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
        'input_archive': {'toto': os.path.join(path_test, 'toto.zip')},
        'img_ref_dir': path_test,
        'img_dest_dir': [os.path.join(path_test, 'old')],
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        os.makedirs(os.path.join(self.path_test, 'old'))
        for i in range(0, 4):
            path = os.path.join(self.path_test, 'old', '00000000', '00FM',
                                'ARK%s' % i)
            os.makedirs(path)
            img_path = os.path.join(path, 'F0%s.jpg' % i)
            with open(img_path, 'w') as f:
                f.write('toto')
        path = os.path.join(self.path_test, 'AR', 'K5')
        os.makedirs(path)
        with open(os.path.join(path, 'FMARK5.high.jpg'), 'w') as f:
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
        step.process()

    @patch('pypers.utils.utils.zipextract',
           MagicMock(side_effect=mock_zipextract_global))
    @patch('pypers.utils.xmldom.get_nodevalue',
           MagicMock(side_effect=mock_get_nodevalue))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process_global(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['input_archive'] = {'toto': os.path.join(self.path_test,
                                                     'FR_BCKST_foo.zip')}
        step = Trademarks.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()

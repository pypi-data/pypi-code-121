import unittest
from pypers.steps.fetch.extract.kr.designs import Designs
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil


mock_get_value_counter_rnb = 0
mock_get_value_counter_anb = 0
mock_get_value_counter_ipnb = 0
mock_get_value_counter_cnb = 0
mock_get_value_counter = 0


def mock_get_nodevalue(*args, **kwargs):
    global mock_get_value_counter_rnb, mock_get_value_counter_anb, \
        mock_get_value_counter_ipnb, mock_get_value_counter_cnb, \
        mock_get_value_counter
    if args[0] == 'RegistrationNumber':
        if mock_get_value_counter_rnb == 0:
            mock_get_value_counter_rnb += 1
            return 'DMTotot'
        else:
            mock_get_value_counter_rnb += 1
            return "F01%s" % mock_get_value_counter_rnb
    if args[0] == 'ApplicationNumberText':
        mock_get_value_counter_anb += 1
        return "F01%s" % mock_get_value_counter_anb

    if args[0] == 'IPOfficeCode':
        if mock_get_value_counter_ipnb == 0:
            mock_get_value_counter_ipnb += 1
            return 'DMTotot'
        else:
            mock_get_value_counter_ipnb += 1
            return "KR"
    if args[0] == 'FileFormatCategory':
        if mock_get_value_counter_cnb == 0:
            mock_get_value_counter_cnb += 1
            return ''
        else:
            mock_get_value_counter_ipnb += 1
            return ".jpg"
    mock_get_value_counter += 1
    if mock_get_value_counter % 2 == 0:
        return '12%s' % mock_get_value_counter
    return '22'


def mock_zipextract(source, dest):
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Transaction xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
  <DesignBibliographicData xmlns="urn:kr:gov:doc:kipo:design">
    <ApplicationNumber xmlns="http://www.wipo.int/standards/XMLSchema/ST96/Common">F01</ApplicationNumber>
  </DesignBibliographicData>
  <Drawing xmlns="urn:kr:gov:doc:kipo:design">
    <View>
    </View>
            <View>
    </View>
            <View>
    </View>
            <View>
    </View>
  </Drawing>
</Transaction>'''
    for i in range(0, 5):
        xml_dest = os.path.join(dest, '12%s.xml' % i)
        with open(xml_dest, 'w') as f:
            f.write(xml_content)
        xml_dest = os.path.join(dest, '12%s.jpg' % i)
        with open(xml_dest, 'w') as f:
            f.write(xml_content)


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.kr.designs.Designs',
        'sys_path': None,
        'name': 'Designs',
        'meta': {
            'job': {},
            'pipeline': {
                'collection': 'peid',
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
        os.makedirs(os.path.join(self.path_test, 'image'))
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
        step = Designs.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()

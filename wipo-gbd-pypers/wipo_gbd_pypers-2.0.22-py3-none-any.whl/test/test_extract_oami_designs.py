import unittest
from pypers.steps.fetch.extract.oami.designs import Designs
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil


def mock_zipextract(source, dest):
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Transaction xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
  <TradeMarkTransactionBody>
    <DesignImageFilename>PE120.jpg</DesignImageFilename>
    <DesignImageFilename>PE220.jpg</DesignImageFilename>
  </TradeMarkTransactionBody>
</Transaction>'''

    for i in range(0, 1):
        if 'img' not in dest:
            zip_dest = os.path.join(dest, '700000000000000.xml')
            with open(zip_dest, 'w') as f:
                f.write(xml_content)
            xml_dest = os.path.join(dest, '12%s.xml' % i)
            with open(xml_dest, 'w') as f:
                f.write(xml_content)
        else:
            xml_dest = os.path.join(dest, 'PE12%s.jpg' % i)
            with open(xml_dest, 'w') as f:
                f.write(xml_content)


mock_get_value_counter = 0


def mock_get_nodevalue(*args, **kwargs):
    global mock_get_value_counter
    res = '12%s' % mock_get_value_counter
    if mock_get_value_counter == 0:
        res = '120-23'
    mock_get_value_counter += 1
    return res


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.oami.designs.Designs',
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
        'input_archive': {'toto': [os.path.join(path_test, 'toto.zip'),
                                   os.path.join(path_test, 'IMG.zip')]},
        'img_ref_dir': path_test
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        for _, v in self.extended_cfg['input_archive'].items():
            for fin in v:
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

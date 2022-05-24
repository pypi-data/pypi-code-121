import unittest
from pypers.steps.fetch.extract.il.trademarks import Trademarks
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil


def mock_zipextract(source, dest):
    if 'xml' in dest:
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<TMBRANDS>
    <TMBRAND>
      <DETAILS>
        <OFFICENUMBER>F01</OFFICENUMBER>
      </DETAILS>
      <IMAGEFILE>F121.jpg</IMAGEFILE>
    </TMBRAND>
    <TMBRAND>
      <DETAILS>
        <OFFICENUMBER>F02</OFFICENUMBER>
      </DETAILS>
      <IMAGEFILE></IMAGEFILE>
    </TMBRAND>
    <TMBRAND>
      <DETAILS>
        <OFFICENUMBER>F02</OFFICENUMBER>
      </DETAILS>
     <IMAGEFILE>F22.jpg</IMAGEFILE>
    </TMBRAND>
</TMBRANDS>'''
        for i in range(0, 10):
            xml_dest = os.path.join(dest, 'F12%s.xml' % i)
            with open(xml_dest, 'w') as f:
                f.write(xml_content)
    if 'img' in dest:
        for i in range(0, 10):
            xml_dest = os.path.join(dest, 'F12%s.jpg' % i)
            with open(xml_dest, 'w') as f:
                f.write('toto')


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.il.trademarks.Trademarks',
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
        'input_archive': {'toto': [os.path.join(path_test, 'xml', 'xml.zip'),
                                   os.path.join(path_test, 'images',
                                                'images.zip')
                                   ]},
        'img_ref_dir': path_test
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        os.makedirs(os.path.join(self.path_test, 'xml'))
        os.makedirs(os.path.join(self.path_test, 'images'))

        for _, v in self.extended_cfg['input_archive'].items():
            for fin in v:
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
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Trademarks.load_step("test", "test", "step")
        step.process()



if __name__ == "__main__":
    unittest.main()

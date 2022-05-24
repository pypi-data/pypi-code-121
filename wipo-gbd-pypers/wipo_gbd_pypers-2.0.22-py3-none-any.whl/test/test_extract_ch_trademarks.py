import unittest
from pypers.steps.fetch.extract.ch.trademarks import Trademarks
from pypers.utils.utils import dict_update
import os
import shutil
import re
from pypers.test import mock_db, mockde_db, mock_logger

from mock import patch, MagicMock


class MockPage:

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __init__(self):
        self.content = '''<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope
   xmlns:SOAP-ENV = "http://www.w3.org/2001/12/soap-envelope"
   SOAP-ENV:encodingStyle = "http://www.w3.org/2001/12/soap-encoding">
    <SOAP-ENV:Body xmlns:transac = "http://www.xyz.org/">
        <getIpRightXMLReturn>
        &lt;transac&gt;
         &lt;marinfo&gt;
            &lt;basappn&gt;F001&lt;/basappn&gt;
            &lt;marpicn&gt;F001&lt;/marpicn&gt;
          &lt;/marinfo&gt;
          &lt;marinfo&gt;
            &lt;basappn&gt;F002&lt;/basappn&gt;
            &lt;marpicn&gt;&lt;/marpicn&gt;
          &lt;/marinfo&gt;
          &lt;/transac&gt;
        </getIpRightXMLReturn>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''
        self.content = self.content.replace('\n', '').replace('\t', '')
        self.content = re.sub('\s+<', '<', self.content)
        self.content = re.sub('\s+&', '&', self.content)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __exit__(self, *args, **kwargs):
        pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __enter__(self, *args, **kwargs):
        pass


def mock_page(*args, **kwargs):
    return MockPage()


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.ch.trademarks.Trademarks',
        'sys_path': None,
        'name': 'Trademarks',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {
                    'from_api': {
                        'url': 'http://my.url.com',
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
        'input_appnums': os.path.join(path_test, 'toto.txt'),
        'img_ref_dir': path_test
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        fin = self.extended_cfg['input_appnums']
        with open(fin, 'w') as f:
            for i in range(0, 10):
                f.write('F00%s\n' % i)
        self.cfg = dict_update(self.cfg, self.extended_cfg)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def tearDown(self):
        try:
            shutil.rmtree(self.path_test)
            pass
        except Exception as e:
            pass

    @patch("requests.sessions.Session.post",
           MagicMock(side_effect=mock_page))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Trademarks.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()

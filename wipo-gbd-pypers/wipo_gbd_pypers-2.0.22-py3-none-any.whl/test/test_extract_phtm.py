import unittest
from pypers.steps.fetch.extract.ph.trademarks import Trademarks
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil
import json
import subprocess
import codecs


class StreamMock:
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __init__(self):
        pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def close(self):
        pass


class PopenMockObj:

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.stdout = StreamMock()
        self.stderr = StreamMock()
        self.returncode = 0

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def communicate(self):
        return b'toto foo', b'1234'


class MockPage:

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __init__(self, vals):
        self.content = []
        for i in vals:
            self.content.append(
                {
                    'markId': str(i),
                    'media': ['img%s.jpg' % k for k in range(0, 10)],
                    'images': [{'location': 'img%s.jpg' % k}
                               for k in range(0, 10)]
                }
            )
        if len(vals) == 100:
            self.content[0]['images'] = [{'location': 'foo.jpg'}]
        self.content = json.dumps(self.content)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __exit__(self, *args, **kwargs):
        pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __enter__(self, *args, **kwargs):
        pass


def mock_page(media, *args, **kwargs):
    vals = media.split('markId=')[1].split(',')
    return MockPage(vals)


def mock_zipextract(source, dest):
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Records>
    <RECORD>
      <APPNO>F12%(i)s</APPNO>
      <LOGO>
        <LOGO>F12%(i)s.jpg</LOGO>
      </LOGO>
    </RECORD>
</Records>'''
    ext = 'xml'
    if ext not in dest:
        ext = 'jpg'
    for i in range(0, 10):
        xml_dest = os.path.join(dest, 'F12%s.%s' % (i, ext))
        with codecs.open(xml_dest, 'wb', 'utf-16le') as f:
            f.write(xml_content % {
                'i': i
            })
    if ext == 'xml':
        xml_dest = os.path.join(dest, 'F1210.%s' % ext)
        with codecs.open(xml_dest, 'wb', 'utf-16le') as f:
            f.write(xml_content % {'i': 1})


mock_get_value_counter = 0


def mock_get_nodevalue(*args, **kwargs):
    global mock_get_value_counter
    res = '12%s' % mock_get_value_counter
    mock_get_value_counter += 1
    return res


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.ph.trademarks.Trademarks',
        'sys_path': None,
        'name': 'PHTM',
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
        'input_archive': {'toto': [os.path.join(path_test, 'toto.xml.rar'),
                                   os.path.join(path_test, 'toto.xml.md5'),
                                   os.path.join(path_test, 'toto.img.rar'),
                                   os.path.join(path_test, 'toto.xml.md5')]},
        'img_ref_dir': path_test
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        self.old_popen = subprocess.Popen
        subprocess.Popen = PopenMockObj
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
        subprocess.Popen = self.old_popen
        try:
            shutil.rmtree(self.path_test)
            pass
        except Exception as e:
            pass

    @patch('pypers.utils.utils.rarextract',
           MagicMock(side_effect=mock_zipextract))
    @patch('pypers.utils.xmldom.get_nodevalue',
           MagicMock(side_effect=mock_get_nodevalue))
    @patch("requests.sessions.Session.get",
           MagicMock(side_effect=mock_page))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Trademarks.load_step("test", "test", "step")
        step.process()



if __name__ == "__main__":
    unittest.main()

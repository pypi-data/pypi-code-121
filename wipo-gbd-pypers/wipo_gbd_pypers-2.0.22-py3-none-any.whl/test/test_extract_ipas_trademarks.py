import unittest
from pypers.steps.fetch.extract.ipas.trademarks import Trademarks
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil

counter_zip = -1


def mock_zipextract(source, dest):
    global counter_zip
    if not os.path.exists(dest):
        os.makedirs(dest)

    if counter_zip == -1:
        for i in [0, 1]:
            xml_dest = os.path.join(dest, 'sub%s.zip' % i)
            with open(xml_dest, 'w') as f:
                f.write('toto')
    else:
        ns = 'xmlns="http://www.wipo.int/standards/XMLSchema/designs"'
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<DesignApplication %(ns)s>
  <DesignApplicationNumber>F0%(i)s</DesignApplicationNumber>
  <DesignDetails>
    <Design>
        <DesignRepresentationSheetDetails>
          <DesignRepresentationSheet>
            <RepresentationSheetFilename></RepresentationSheetFilename>
           </DesignRepresentationSheet>
        </DesignRepresentationSheetDetails>
        <DesignRepresentationSheetDetails>
          <DesignRepresentationSheet>
            <RepresentationSheetFilename>FOOOBAR.jpg</RepresentationSheetFilename>
           </DesignRepresentationSheet>
        </DesignRepresentationSheetDetails>
        <DesignRepresentationSheetDetails>
          <DesignRepresentationSheet>
            <RepresentationSheetFilename>F101.jpg</RepresentationSheetFilename>
           </DesignRepresentationSheet>
        </DesignRepresentationSheetDetails>
    </Design>
  </DesignDetails>
</DesignApplication>'''
        for i in range(0, 2):
            if counter_zip % 4 == 3:
                ns = ''
            path = os.path.join(dest, 'F10%s_biblio.xml' % i)
            with open(path, 'w') as f:
                f.write(xml_content % {
                    'ns': ns,
                    'i': i,
                })
            path = os.path.join(dest, 'F10%s.xml' % i)
            with open(path, 'w') as f:
                f.write(xml_content)
            if not os.path.exists(os.path.join(dest, 'ATTACHMENT')):
                os.makedirs(os.path.join(dest, 'ATTACHMENT'))
            path = os.path.join(dest, 'ATTACHMENT', 'f10%s.jpg' % i)
            with open(path, 'w') as f:
                f.write('toto')
            path = os.path.join(dest, 'ATTACHMENT', 'f10%s.mpeg' % i)
            with open(path, 'w') as f:
                f.write('toto')
    counter_zip += 1


mock_get_value_counter = 0


def mock_get_nodevalue(*args, **kwargs):
    global mock_get_value_counter
    res = '12%s' % mock_get_value_counter
    mock_get_value_counter += 1
    if mock_get_value_counter == 2:
        return ""
    return res


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.ipas.trademarks.Trademarks',
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
        'version': '1.5.1'
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
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


if __name__ == "__main__":
    unittest.main()

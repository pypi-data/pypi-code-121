import unittest
from pypers.steps.fetch.extract.de.designs import Designs
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger

from mock import patch, MagicMock
import os
import shutil
import json
import gzip


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


def mock_set_nodevalue(*args, **kwargs):
    pass


def mock_zipextract(source, dest):
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Transaction>
  <TEIL Teil="Teil_A">
    <AKTE>
        <C_AKTE_REGISTER_NR>F001</C_AKTE_REGISTER_NR>
        <MUSTER_LISTE>
            <MUSTER>
                <C_MUSTER_MUSTER_NR>20</C_MUSTER_MUSTER_NR>
                <C_MUSTER_ANZAHL_DARSTELLUNGEN>2</C_MUSTER_ANZAHL_DARSTELLUNGEN>
            </MUSTER>
            <MUSTER>
                <C_MUSTER_MUSTER_NR>21</C_MUSTER_MUSTER_NR>
            </MUSTER>
        </MUSTER_LISTE>
    </AKTE>
    <AKTE>
        <C_AKTE_REGISTER_NR>F002</C_AKTE_REGISTER_NR>
    </AKTE>
  </TEIL>
  <TEIL Teil="Teil_B">
    <AKTE>
        <C_AKTE_REGISTER_NR>F001</C_AKTE_REGISTER_NR>
        <MUSTER_LISTE>
            <MUSTER>
                <C_MUSTER_MUSTER_NR>20</C_MUSTER_MUSTER_NR>
                <C_MUSTER_ANZAHL_DARSTELLUNGEN>2</C_MUSTER_ANZAHL_DARSTELLUNGEN>
            </MUSTER>
            <MUSTER>
                <C_MUSTER_MUSTER_NR>21</C_MUSTER_MUSTER_NR>
            </MUSTER>
        </MUSTER_LISTE>
    </AKTE>
    <AKTE>
        <C_AKTE_REGISTER_NR>F002</C_AKTE_REGISTER_NR>
    </AKTE>
  </TEIL>
  <TEIL Teil="Teil_D">
   <SUBTEIL SubTeil="D">
    <AKTE>
        <C_AKTE_REGISTER_NR>F002</C_AKTE_REGISTER_NR>
        <C_AKTE_BETROFFENE_MUSTER_NRN>20, 21</C_AKTE_BETROFFENE_MUSTER_NRN>
    </AKTE>
    <AKTE>
        <C_AKTE_REGISTER_NR>F002</C_AKTE_REGISTER_NR>
    </AKTE>
    </SUBTEIL>
  </TEIL>
  <TEIL Teil="Teil_E">
   <SUBTEIL SubTeil="D">
    <AKTE>
        <C_AKTE_REGISTER_NR>F002</C_AKTE_REGISTER_NR>
        <C_AKTE_BETROFFENE_MUSTER_NRN>20, 21</C_AKTE_BETROFFENE_MUSTER_NRN>
    </AKTE>
    <AKTE>
        <C_AKTE_REGISTER_NR>F002</C_AKTE_REGISTER_NR>
    </AKTE>
    </SUBTEIL>
  </TEIL>
  <TEIL Teil="Teil_F">
   <SUBTEIL SubTeil="C_AL_HL_AENDERUNG_INHABER">
    <AKTE>
        <C_AKTE_REGISTER_NR>F002</C_AKTE_REGISTER_NR>
        <C_AKTE_BETROFFENE_MUSTER_NRN>20, 21</C_AKTE_BETROFFENE_MUSTER_NRN>
        <C_AKTE_ERLAEUTERUNG_ZUR_HL>Foo</C_AKTE_ERLAEUTERUNG_ZUR_HL>
    </AKTE>
    </SUBTEIL>
  </TEIL>
    <TEIL Teil="Teil_F">
   <SUBTEIL SubTeil="C_AL_HL_AENDERUNG_ENTWERFER">
    <AKTE>
        <C_AKTE_REGISTER_NR>F5353534</C_AKTE_REGISTER_NR>
        <MUSTER_LISTE>
            <MUSTER>
                <C_AKTE_ERLAEUTERUNG_ZUR_HL>Foo</C_AKTE_ERLAEUTERUNG_ZUR_HL>
                <C_MUSTER_MUSTER_NR>4535</C_MUSTER_MUSTER_NR>
                <C_MUSTER_ANZAHL_DARSTELLUNGEN>2</C_MUSTER_ANZAHL_DARSTELLUNGEN>
            </MUSTER>
        </MUSTER_LISTE>
    </AKTE>
    </SUBTEIL>
  </TEIL>
  <TEIL Teil="Teil_F">
   <SUBTEIL SubTeil="C_AL_HL_AENDERUNG_VERTRETER">
    <AKTE>
        <C_AKTE_REGISTER_NR>F002</C_AKTE_REGISTER_NR>
        <C_AKTE_BETROFFENE_MUSTER_NRN>20, 21</C_AKTE_BETROFFENE_MUSTER_NRN>
        <C_AKTE_ERLAEUTERUNG_ZUR_HL>Foo</C_AKTE_ERLAEUTERUNG_ZUR_HL>
    </AKTE>
    </SUBTEIL>
  </TEIL>
    <TEIL Teil="Teil_F">
   <SUBTEIL SubTeil="C_AL_HL_AENDERUNG_ZUSTELL">
    <AKTE>
        <C_AKTE_REGISTER_NR>F002</C_AKTE_REGISTER_NR>
        <C_AKTE_BETROFFENE_MUSTER_NRN>20, 21</C_AKTE_BETROFFENE_MUSTER_NRN>
        <C_AKTE_ERLAEUTERUNG_ZUR_HL>Foo</C_AKTE_ERLAEUTERUNG_ZUR_HL>
    </AKTE>
    </SUBTEIL>
  </TEIL>
    <TEIL Teil="Teil_F">
   <SUBTEIL SubTeil="C_AL_HL_BERICHTIGUNG">
    <AKTE>
        <C_AKTE_REGISTER_NR>F002</C_AKTE_REGISTER_NR>
        <C_AKTE_BETROFFENE_MUSTER_NRN>20, 21</C_AKTE_BETROFFENE_MUSTER_NRN>
        <C_AKTE_ERLAEUTERUNG_ZUR_HL>Foo</C_AKTE_ERLAEUTERUNG_ZUR_HL>
    </AKTE>
    </SUBTEIL>
  </TEIL>
     <TEIL Teil="Teil_F">
   <SUBTEIL SubTeil="C_AL_HL_INTERESSE_LIZ_JA">
    <AKTE>
        <C_AKTE_REGISTER_NR>F002</C_AKTE_REGISTER_NR>
        <C_AKTE_BETROFFENE_MUSTER_NRN>20, 21</C_AKTE_BETROFFENE_MUSTER_NRN>
        <C_AKTE_ERLAEUTERUNG_ZUR_HL>Foo</C_AKTE_ERLAEUTERUNG_ZUR_HL>
    </AKTE>
    </SUBTEIL>
  </TEIL>
</Transaction>'''
    jpg_dest = os.path.join(dest, '01F00102101.jpg')
    zip_dest = os.path.join(dest, 'toto.7z')
    for path in [jpg_dest, zip_dest]:
        with open(path, 'w') as f:
            f.write('toto')
    for i in range(0, 101):
        xml_dest = os.path.join(dest, '12%s.xml' % i)
        with open(xml_dest, 'w') as f:
            f.write(xml_content)
    xml_file = os.path.join(dest, 'xml')
    xml_file = os.path.join(xml_file, 'F5353534-4535.xml')
    with open(xml_file, 'w') as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<MUSTER>
<C_AKTE_ERLAEUTERUNG_ZUR_HL>20</C_AKTE_ERLAEUTERUNG_ZUR_HL>
</MUSTER>''')


def mock_7zipextract(source, dest):
    pass


mock_get_value_counter = 0


def mock_get_nodevalue(*args, **kwargs):
    global mock_get_value_counter
    res = '12%s' % mock_get_value_counter
    mock_get_value_counter += 1
    return res


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.de.designs.Designs',
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
        'input_archive': {'toto': [os.path.join(path_test, 'toto.zip'),
                                   os.path.join(path_test, 'toto.7z')]},
        'xml_store': path_test
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        # Create the files needed (Only filenames with no content)
        for els in [v for f, v in self.extended_cfg['input_archive'].items()]:
            for fin in els:
                with open(fin, 'w') as f:
                    f.write('toto')

        img_alreday = os.path.join(self.path_test, '01', '20')
        os.makedirs(img_alreday)
        img_alreday = os.path.join(img_alreday, '120.foooo.high.png')
        with open(img_alreday, 'w') as f:
            f.write('toto')

        img_alreday = os.path.join(self.path_test, 'F0', '02')
        os.makedirs(img_alreday)
        zip_f = os.path.join(img_alreday, 'F002-0020.xml.gz')
        with gzip.open(zip_f, 'wb') as f:
            f.write(b'toto')
        img_f = os.path.join(img_alreday, 'F002-0020.foooo.high.jpg')
        with open(img_f, 'w') as f:
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
    @patch('pypers.utils.utils.sevenzextract',
           MagicMock(side_effect=mock_7zipextract))
    @patch('pypers.utils.xmldom.get_nodevalue',
           MagicMock(side_effect=mock_get_nodevalue))
    @patch('pypers.utils.xmldom.set_nodevalue',
           MagicMock(side_effect=mock_set_nodevalue))
    @patch('pypers.utils.xmldom.save_xml',
           MagicMock(side_effect=mock_set_nodevalue))
    @patch("requests.sessions.Session.get",
           MagicMock(side_effect=mock_page))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Designs.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()

import unittest
from pypers.steps.fetch.extract.em.representatives import Representatives
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil


def mock_zipextract(source, dest):
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Representatives>
<Representative xmlns="http://www.euipo.europa.eu/EUTM/EUTM_Download" operationCode="Delete">
  <RepresentativeIdentifier>F121-ff</RepresentativeIdentifier>
</Representative>
<Representative xmlns="http://www.euipo.europa.eu/EUTM/EUTM_Download" operationCode="Totot">
  <RepresentativeIdentifier>F122-ff</RepresentativeIdentifier>
</Representative>
<Representative xmlns="http://www.euipo.europa.eu/EUTM/EUTM_Download" operationCode="Totot">
  <RepresentativeIdentifier>F132-ff</RepresentativeIdentifier>
</Representative>
</Representatives>
'''
    for i in range(0, 10):
        xml_dest = os.path.join(dest, '12%s.xml' % i)
        with open(xml_dest, 'w') as f:
            f.write(xml_content)
        xml_dest = os.path.join(dest, 'F12%s-fff.jpg' % i)
        with open(xml_dest, 'w') as f:
            f.write(xml_content)


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.em.representatives.Representatives',
        'sys_path': None,
        'name': 'Representatives',
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
        'img_dest_dir': [os.path.join(path_test, 'toto')]
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        for _, fin in self.extended_cfg['input_archive'].items():
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
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Representatives.load_step("test", "test", "step")
        step.preprocess()
        step.process()



if __name__ == "__main__":
    unittest.main()

import unittest
from pypers.steps.fetch.extract.wo.designs import Designs
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.wo.designs.Designs',
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
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <Transaction>
      <HagueExpressTransaction  xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
        <HagueCurrent xmlns="http://www.wipo.int/standards/XMLSchema/ST96/Design">
          <HagueRegistration xmlns="http://www.wipo.int/standards/XMLSchema/ST96/Design">
            <InternationalRegistrationNumber xmlns="http://www.wipo.int/standards/XMLSchema/ST96/Common">F001</InternationalRegistrationNumber>
        </HagueRegistration></HagueCurrent>
      </HagueExpressTransaction>
      <HagueExpressTransaction>
        <HagueHistory xmlns="http://www.wipo.int/standards/XMLSchema/ST96/Design">
          <InternationalRegistrationNumber xmlns="http://www.wipo.int/standards/XMLSchema/ST96/Common">FOOO01</InternationalRegistrationNumber>
        </HagueHistory>
        <HagueCurrent xmlns="http://www.wipo.int/standards/XMLSchema/ST96/Design">
            <F001 xmlns="http://foo.bar">f001</F001>
        </HagueCurrent>
      </HagueExpressTransaction>
     <HagueExpressTransaction>
      </HagueExpressTransaction>
    </Transaction>
        
        '''
        for _, fin in self.extended_cfg['input_archive'].items():
            with open(fin, 'w') as f:
                f.write(xml_content)
        self.cfg = dict_update(self.cfg, self.extended_cfg)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def tearDown(self):
        try:
            shutil.rmtree(self.path_test)
            pass
        except Exception as e:
            pass

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Designs.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()

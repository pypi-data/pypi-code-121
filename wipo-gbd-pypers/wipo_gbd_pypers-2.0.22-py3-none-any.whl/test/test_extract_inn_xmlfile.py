import unittest
from pypers.steps.fetch.extract.who.inn import INN
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import gzip
import os
import shutil


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.who.inn.INN',
        'sys_path': None,
        'name': 'XML',
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
        'inns': [{
            'recommended': [{
                'number': 'F01',
                'publications': {
                    'F/01': {
                        'list_entry': 'toto',
                        'names': {
                            'ro': 'toto',
                        }
                    },
                    'F/02': {
                        'list_entry': 'toto',
                        'names': {
                            'ro': 'toto',
                        }
                    },
                    'F/03': {
                        'list_entry': 'toto',
                        'names': {
                            'ro': 'toto',
                        }
                    },
                }
            }],
            'proposed': []
        }],
        'xml_store': os.path.join(path_test, 'store')
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        os.makedirs(os.path.join(self.path_test, 'store'))
        with open(os.path.join(self.path_test, 'F-01.xml'), 'w') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
        <Transaction xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
          <recommended>
          </recommended>
        </Transaction>''')
        path = os.path.join(self.path_test, 'store', '00','02')
        os.makedirs(path)
        with gzip.open(os.path.join(path, 'F-02.xml.gz'), 'wb') as f:
            f.write(b'''<?xml version="1.0" encoding="UTF-8"?>
        <Transaction xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
          <recommended>
          </recommended>
        </Transaction>''')
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
        step = INN.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()

import unittest
from pypers.steps.fetch.extract.es.designs import Designs
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil
import copy


def mock_zipextract(source, dest):
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <Transaction xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
          <TradeMarkTransactionBody>
            <ApplicantDetails>
                <Applicant></Applicant>
            </ApplicantDetails>
            <RepresentativeDetails>
            </RepresentativeDetails>
            <PreviousApplicantDetails>
            </PreviousApplicantDetails>
          </TradeMarkTransactionBody>
        </Transaction>'''
    path = os.path.join(dest, "my_test")
    try:
        os.makedirs(path)
    except Exception as e:
        pass
    for i in range(0, 10):
        data_path = os.path.join(path, 'DATA-F001%s.xml' % i)
        with open(data_path, 'w') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
        <Transaction xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
          <TradeMarkTransactionBody>
          
          </TradeMarkTransactionBody>
        </Transaction>''')
    path = os.path.join(dest, "my_test_1")
    try:
        os.makedirs(path)
    except Exception as e:
        pass
    for i in range(0, 10):
        data_path = os.path.join(path, 'DATA-F001%s.xml' % i)
        with open(data_path, 'w') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
        <Transaction xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
          <TradeMarkTransactionBody>
            with_error
        </Transaction>''')
    path = os.path.join(dest, "my_test_1_bis")
    try:
        os.makedirs(path)
    except Exception as e:
        pass
    for i in range(0, 10):
        data_path = os.path.join(path, 'DATA-F001%s.xml' % i)
        with open(data_path, 'w') as f:
            f.write(xml_content)
    path = os.path.join(dest, "my_test2")
    try:
        os.makedirs(path)
    except Exception as e:
        pass

    for i in range(0, 10):
        data_path = os.path.join(path, 'DATA-F001%s.xml' % i)
        with open(data_path, 'w') as f:
            f.write(xml_content)
        data_path = os.path.join(path, 'APPLICANT-F001%s.xml' % i)
        with open(data_path, 'w') as f:
            f.write(xml_content)
        data_path = os.path.join(path, 'PREVIOUSAPPLICANT-F001%s.xml' % i)
        with open(data_path, 'w') as f:
            f.write(xml_content)
        data_path = os.path.join(path, 'REPRESENTATIVE-F001%s.xml' % i)
        with open(data_path, 'w') as f:
            f.write(xml_content)
    img_path = os.path.join(os.path.dirname(__file__), 'foo', 'F0', '01')
    os.makedirs(img_path)
    img_path = os.path.join(img_path, 'FF001-F001.1.high.jpg')
    with open(img_path, 'w') as f:
        f.write('toto')


mock_get_value_counter = 0


def mock_get_nodevalue(*args, **kwargs):
    global mock_get_value_counter
    if args[0] == "ViewURI":
        if mock_get_value_counter == 0:
            mock_get_value_counter = 1
            return []
        return ['link1', 'link2']
    if args[0] == "URI":
        return ['ff/Fr-F0010']
    return "FF001"


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.es.designs.Designs',
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
        'input_archive': {'toto': os.path.join(path_test, 'toto.zip')},
        'img_ref_dir': path_test,
        'get_imgs_pdf': 1
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
    @patch('pypers.utils.xmldom.get_nodevalues',
           MagicMock(side_effect=mock_get_nodevalue))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Designs.load_step("test", "test", "step")
        step.process()


    @patch('pypers.utils.utils.zipextract',
           MagicMock(side_effect=mock_zipextract))
    @patch('pypers.utils.xmldom.get_nodevalue',
           MagicMock(side_effect=mock_get_nodevalue))
    @patch('pypers.utils.xmldom.get_nodevalues',
           MagicMock(side_effect=mock_get_nodevalue))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process_2(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['get_imgs_pdf'] = 0
        step = Designs.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()

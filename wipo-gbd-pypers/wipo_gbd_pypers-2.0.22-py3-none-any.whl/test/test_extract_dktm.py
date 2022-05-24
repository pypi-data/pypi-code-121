import unittest
from pypers.steps.fetch.extract.dk.trademarks import Trademarks
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger

from mock import patch, MagicMock
import os
import shutil
import copy


xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Transaction xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
  <TradeMarkTransactionBody>
    <TransactionContentDetails>
    <ApplicationNumber>12%s</ApplicationNumber>
    <ApplicantKey>
      
    </ApplicantKey>
    <RepresentativeKey>
    </RepresentativeKey>
    </TransactionContentDetails>
  </TradeMarkTransactionBody>
<Applicant></Applicant>
<Applicant></Applicant>
<Representative></Representative>
</Transaction>'''


class MockPage:

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __init__(self):
        self.content = xml_content

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __exit__(self, *args, **kwargs):
        pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __enter__(self, *args, **kwargs):
        pass


def mock_page(*args, **kwargs):
    return MockPage()


def mock_zipextract(source, dest):
    for i in range(0, 10):
        xml_dest = os.path.join(dest, '12%s.xml' % i)
        with open(xml_dest, 'w') as f:
            f.write(xml_content % i)


nb_call_nodevalue = 0
nb_call_nodevalue_2 = 0


def mock_get_nodevalue(*args, **kwargs):
    global nb_call_nodevalue, nb_call_nodevalue_2
    if args[0] == 'ApplicationNumber':
        if nb_call_nodevalue_2 == 0:
            nb_call_nodevalue_2 = 1
            return ''
        return '120'
    nb_call_nodevalue += 1
    if nb_call_nodevalue % 2 == 0:
        return 'http://totot/uri/foo/140'
    return 'http://totot/uri/foo/120'


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.dk.trademarks.Trademarks',
        'sys_path': None,
        'name': 'DKTM',
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
        'input_archive': [{'toto': [os.path.join(path_test,
                                                 'foo_DKPTO_TM_EXPORT_foo.zip'
                                                 ),
                                    os.path.join(path_test,
                                                 'foo_DKPTO_AP_EXPORT_foo.zip'
                                                 ),
                                    os.path.join(path_test,
                                                 'foo_DKPTO_RE_EXPORT_foo.zip'
                                                 )
                                    ]}],
        'img_ref_dir': path_test
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        for archives in self.extended_cfg['input_archive']:
            for p in [v for _, v in archives.items()]:
                for fin in p:
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
    @patch('pypers.utils.xmldom.get_nodevalue',
           MagicMock(side_effect=mock_get_nodevalue))
    @patch("requests.sessions.Session.get",
           MagicMock(side_effect=mock_page))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Trademarks.load_step("test", "test", "step")
        step.preprocess()
        step.process()

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process_no_input(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['input_archive'] = []
        step = Trademarks.load_step("test", "test", "step")
        step.preprocess()
        step.process()


if __name__ == "__main__":
    unittest.main()

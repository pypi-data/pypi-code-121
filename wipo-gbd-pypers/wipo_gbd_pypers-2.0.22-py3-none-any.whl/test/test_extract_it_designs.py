import unittest
from pypers.steps.fetch.extract.it.designs import Designs
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil
import copy


class MockPage:

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __init__(self, include_error=False):
        self.content = '''<?xml version="1.0" encoding="UTF-8"?>
        <Transaction xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
          <TradeMarkTransactionBody>
            <ApplicantKey>
              <Applicant>toto</Applicant>
            </ApplicantKey>
            <RepresentativeKey>
              <Representative>foo</Representative>
            </RepresentativeKey>
          </TradeMarkTransactionBody>
          <DesignRepresentationSheetDetails>
          </DesignRepresentationSheetDetails>
        </Transaction>'''
        if include_error:
            self.content = '''<?xml version="1.0" encoding="UTF-8"?>
<Transaction xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
 <exceptionVO>
   <TransactionContentDetails>
   </TransactionContentDetails>
 </exceptionVO>
</Transaction>'''

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __exit__(self, *args, **kwargs):
        pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __enter__(self, *args, **kwargs):
        pass


nb_calls = 0


def mock_page(*args, **kwargs):
    global nb_calls
    nb_calls += 1
    return MockPage(include_error=(nb_calls == 1))


def mock_get_nodevalue(*args, **kwargs):
    return 'fooo'


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.it.designs.Designs',
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
        'output_dir': path_test,
    }

    extended_cfg = {
        'input_files': [os.path.join(path_test, 'foobar.txt')],
        'img_dir': path_test,
        'store_dir': path_test,
        'img_map_file': os.path.join(path_test, 'query_design_id.csv'),
        'img_map_redo_f': os.path.join(path_test, 'query_design_id.redo.csv')
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        with open(self.extended_cfg['img_map_file'], 'w') as f:
            lines = """
tototo,xx2020001,FF000001
tototo,xx2020001,FF000004
t,xx2000002,FF000002
tototo,xx0000001,FF000003
FF000001,xx2000002,
"""
            f.write(lines)
        with open(self.extended_cfg['img_map_redo_f'], 'w') as f:
            f.write('tototo\nfofofofof\nfooooff')

        with open(os.path.join(self.path_test, 'foobar.txt'), 'w') as f:
            f.write('<br>'.join(
                ['<a href="http://foo.bar.url/">FF00000%s</a>' % i
                 for i in range(0, 10)]))
        media_path = os.path.join(
            self.path_test,'00', '00', 'tototo')
        os.makedirs(media_path)
        for i in range(0, 10):
            img_path = os.path.join(media_path, 'tototo_%s-media.jpg' % i)
            with open(img_path, 'w') as f:
                f.write('toto')
        self.cfg = dict_update(self.cfg, self.extended_cfg)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def tearDown(self):
        try:
            shutil.rmtree(self.path_test)
            pass
        except Exception as e:
            pass

    @patch('pypers.utils.xmldom.get_nodevalue',
           MagicMock(side_effect=mock_get_nodevalue))
    @patch("requests.sessions.Session.get",
           MagicMock(side_effect=mock_page))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Designs.load_step("test", "test", "step")
        step.process()


    @patch('pypers.utils.xmldom.get_nodevalue',
           MagicMock(side_effect=mock_get_nodevalue))
    @patch("requests.sessions.Session.get",
           MagicMock(side_effect=mock_page))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process2(self):
        with open(os.path.join(self.path_test, '2020001.xml'), 'w') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
        <Transaction xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
          <TradeMarkTransactionBody>
            <ApplicantKey>
              <Applicant>toto</Applicant>
            </ApplicantKey>
            <RepresentativeKey>
              <Representative>foo</Representative>
            </RepresentativeKey>
          </TradeMarkTransactionBody>
          <DesignRepresentationSheetDetails>
          </DesignRepresentationSheetDetails>
        </Transaction>''')
        step = Designs.load_step("test", "test", "step")
        step.process()


    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process_no_input(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['input_files'] = []
        step = Designs.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()

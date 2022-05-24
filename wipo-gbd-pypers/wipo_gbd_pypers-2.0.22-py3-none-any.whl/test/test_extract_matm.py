import unittest
from pypers.steps.fetch.extract.ma.trademarks import Trademarks
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil
import copy


def mock_zipextract(source, dest):
    marks = """
(511) tototo
1     tototo
2     tototo
1     tototo
(210) F000123
------------
(111) img0001
(001) 
(116) toto
(210) F000120
(220) toto
(180) toto
(190) toto
(117) toto
(441) toto
(540) toto
(550) toto
(551) toto
(591) toto
(300) t1 t2 t3;t1 t2 t3;t1 t2
(730) fooo@;RO : totot @ foooffof@;
(740) toto
(000) toto
------------
(111) img0020
(210) F000130
------------

    """
    try:
        os.makedirs(dest)
    except Exception as e:
        pass
    # mark file
    with open(os.path.join(dest, 'mark_file.txt'), 'w') as f:
        f.write(marks)
    # images
    img_path = os.path.join(dest, 'images')
    os.makedirs(img_path)
    for i in range(0, 10):
        with open(os.path.join(img_path, 'img000%s.jpg' % i), 'w') as f:
            f.write('totot')


mock_get_value_counter = 0


def mock_get_nodevalue(*args, **kwargs):
    global mock_get_value_counter
    res = '12%s' % mock_get_value_counter
    mock_get_value_counter += 1
    return res


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.ma.trademarks.Trademarks',
        'sys_path': None,
        'name': 'MATM',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {
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
        for fin in [v for f, v in self.extended_cfg['input_archive'].items()]:
            with open(fin, 'w') as f:
                f.write('toto')

        img_alreday = os.path.join(self.path_test, '00', '20')
        os.makedirs(img_alreday)
        img_alreday = os.path.join(img_alreday, 'img0020.high.png')
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
    @patch('pypers.utils.utils.rarextract',
           MagicMock(side_effect=mock_zipextract))
    @patch('pypers.utils.xmldom.get_nodevalue',
           MagicMock(side_effect=mock_get_nodevalue))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Trademarks.load_step("test", "test", "step")
        step.process()

    @patch('pypers.utils.utils.zipextract',
           MagicMock(side_effect=mock_zipextract))
    @patch('pypers.utils.utils.rarextract',
           MagicMock(side_effect=mock_zipextract))
    @patch('pypers.utils.xmldom.get_nodevalue',
           MagicMock(side_effect=mock_get_nodevalue))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process2(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['input_archive']['toto'] = os.path.join(self.path_test,
                                                    'toto.rar')
        step = Trademarks.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()

import unittest
from pypers.steps.fetch.extract.ee.trademarks import Trademarks
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil


def mock_zipextract(source, dest):
    try:
        os.makedirs(dest)
    except Exception as e:
        pass
    # mark files
    _generate_file(dest, 'mark.txt')
    _generate_file(dest, 'categpict.txt', with_extra=True)
    _generate_file(dest, 'priority.txt', with_extra=True)
    _generate_file(dest, 'owner.txt', with_extra=True)
    _generate_file(dest, 'class.txt', with_extra=True)
    # Empty file
    with open(os.path.join(dest, 'representative.txt'), 'w') as f:
        pass

    # images
    img_path = os.path.join(dest, 'images')
    os.makedirs(img_path)
    for i in range(0, 10):
        with open(os.path.join(img_path, 'img000%s.jpg' % i), 'w') as f:
            f.write('totot')


def _generate_file(dest, name, with_extra=False):
    with open(os.path.join(dest, name), 'w') as f:
        for i in range(0, 10):
            # Multiple app number entries
            appNumber = 'FFTM000%s' % i
            col_text = [appNumber]
            mark_image = "img000%s" % (i+1)
            for col in range(0, 10):
                if col == 6:
                    if i == 1:
                        col_text.append("")
                    else:
                        col_text.append(mark_image)
                else:
                    col_text.append('toto')
            if i < 2:
                f.write('|'.join(col_text) + '\n')
                f.write('|\n')
            f.write('|'.join(col_text) + '|\n')
        if with_extra:
            f.write('|'.join(['FFTM0100', 'toto']) + '\n')
            f.write('|'.join(['F_F', 'toto']) + '\n')


mock_get_value_counter = 0


def mock_get_nodevalue(*args, **kwargs):
    global mock_get_value_counter
    res = '12%s' % mock_get_value_counter
    mock_get_value_counter += 1
    return res


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.ee.trademarks.Trademarks',
        'sys_path': None,
        'name': 'Trademarks',
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

import unittest
from pypers.steps.harmonize.resize import Resize
from pypers.utils.utils import dict_update
import os
import shutil
import copy
from pypers.test import mock_db, mockde_db, mock_logger
from pypers.core.interfaces.storage.test import MockS3
from mock import patch, MagicMock

mockde_s3 = MockS3()


def mock_s3(*args, **kwargs):
    return mockde_s3


nb_calls_to_high = 0
nb_calls_to_covert = -1
nb_calls_to_high_2 = 0
nb_calls_to_compress = 0
nb_calls_to_th = 0


def side_effect_cover_to_png(img_file):
    img_name, img_ext = os.path.splitext(os.path.basename(img_file))
    return "%s.png" % img_name


def side_effect_generate_ico(img_file, *args, **kwargs):
    img_name, img_ext = os.path.splitext(os.path.basename(img_file))
    res = "%s.ico.png" % img_name
    with open(res, 'w') as f:
        f.write('foo')
    return res


def side_effect_cover_to_high(img_file, *args, **kwargs):
    global nb_calls_to_high
    if nb_calls_to_high == 0:
        nb_calls_to_high += 1
        raise Exception()
    img_name, img_ext = os.path.splitext(os.path.basename(img_file))
    res = os.path.join(os.path.dirname(__file__), 'foo',
                       '%s.high.png' % img_name)
    with open(res, 'w') as f:
        f.write('foo')
    return res


def side_effect_crop(*args, **kwargs):
    global nb_calls_to_covert
    nb_calls_to_covert += 1
    if nb_calls_to_covert == 3:
        raise Exception()
    if nb_calls_to_covert > 2:
        return 0
    return nb_calls_to_covert


def side_effect_high(*args, **kwargs):
    global nb_calls_to_high_2
    nb_calls_to_high_2 += 1
    if nb_calls_to_high_2 == 1:
        raise Exception()


def side_effect_compress(*args, **kwargs):
    global nb_calls_to_compress
    nb_calls_to_compress += 1
    if nb_calls_to_compress == 1:
        raise Exception()


def side_effect_th(img_file, img_name, *args, **kwargs):
    global nb_calls_to_th
    nb_calls_to_th += 1
    if nb_calls_to_th == 1:
        raise Exception()
    img_dir = os.path.dirname(img_file)
    img_thm = os.path.join(img_dir, '%s-th.jpg' % img_name)
    with open(img_thm, 'w') as f:
        f.write('foo')
    return img_thm


class TestLire(unittest.TestCase):
    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.harmonize.resize.Resize',
        'sys_path': None,
        'name': 'ProcessIMG',
        'meta': {
            'job': {},
            'pipeline': {
                'output_dir': path_test,
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
        'img_files':
            {'0010': [],
             '0011': [{'ori': 'img1.gif'},
                      {'ori': 'img2.jpg'},
                      {'ori': 'img3.png'},
                      {'ori': 'img5.png'},
                      {'ori': 'img6.png'},
                      {'ori': 'img7.png'},
                      {'ori': 'img8.png'},
                      {'ori': 'img9.png'}],
             '0012': [{'ori': 'img4.png'}]
             }
        ,
        'extraction_dir': path_test,
        'archive_name': "img_test",
        'compress': 1
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("boto3.resource", MagicMock(side_effect=mock_s3))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        for appnum, el in copy.deepcopy(self.extended_cfg['img_files']).items():
            imgs = el
            if not imgs:
                continue
            for img in imgs:
                if img:
                    path_img = os.path.join(self.path_test, img['ori'])
                    with open(path_img, 'w') as f:
                        f.write('toto')
        for i in range(0, 9):
            path_img = os.path.join(self.path_test, 'img%s.high.png' % i)
            with open(path_img, 'w') as f:
                f.write('toto')
        path_img = os.path.join(self.path_test, 'img9.high.png')
        with open(path_img, 'w') as f:
            pass
        self.extended_cfg['img_files']['0013'] = [{
            'ori': 'foo.jpg'}]
        self.cfg = dict_update(self.cfg, self.extended_cfg)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def tearDown(self):
        try:
            shutil.rmtree(self.path_test)
            pass
        except Exception as e:
            pass

    @patch('pypers.utils.img.compress',
           MagicMock(side_effect=side_effect_compress))
    @patch('pypers.utils.img.crop',
           MagicMock(side_effect=side_effect_crop))
    @patch('pypers.utils.img.Convert.from_gif',
           MagicMock(side_effect=side_effect_cover_to_png))
    @patch('pypers.utils.img.Convert.to_hgh',
           MagicMock(side_effect=side_effect_cover_to_high))
    @patch('pypers.utils.img.Generate.high',
           MagicMock(side_effect=side_effect_high))
    @patch('pypers.utils.img.Generate.thumbnail',
           MagicMock(side_effect=side_effect_th))
    @patch('pypers.utils.img.Generate.icon',
           MagicMock(side_effect=side_effect_generate_ico))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.storage.get_storage", MagicMock(side_effect=mock_s3))
    def test_process(self):
        mockde_db.update(self.cfg)
        from pprint import pprint
        pprint(self.cfg)
        step = Resize.load_step("test", "test", "step")
        step.process()
        # After throwing all the exceptions, only 3 images will be processed
        self.assertEqual(len(step.img_files.keys()), 4)


if __name__ == "__main__":
    unittest.main()

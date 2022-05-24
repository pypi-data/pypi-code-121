import unittest
from pypers.steps.fetch.common.download_images import DownloadIMG
from pypers.utils.utils import dict_update
import os
import shutil
from pypers.utils import download
import copy
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock


class MockStreamReader:

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __init__(self):
        self.counter = 0

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def read(self):
        self.counter += 1
        if self.counter % 2 == 0:
            return 'image_content'.encode('utf-8')
        return ""

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def close(self):
        pass


stream_reader = MockStreamReader()


def mock_download(*args, **kwargs):
    return stream_reader


subprocess_counter = 0


def mock_subprocess(*args, **kwargs):
    global subprocess_counter
    if subprocess_counter > 0:
        raise Exception()
    subprocess_counter += 1


class TestCleanup(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.fetch.common.download_images.DownloadIMG',
        'sys_path': None,
        'name': 'download_images',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {

                },
                'run_id': 1,
                'log_dir': path_test
            },
            'step': {}
        },
        'output_dir': path_test,
    }

    extended_cfg = {
        'file_ext': 'jpg',
        'img_files': '',
        'extraction_dir': path_test,
        'archive_name': '',
        'output_data': '',
        'dest_dir': ''
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        self.old_download = download.download
        download.download = mock_download
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)

        # Create the env
        images_folder = os.path.join(self.path_test, 'imgs')
        os.makedirs(images_folder)
        self.extended_cfg['img_files'] = {
            j :[{
                'ori': 'image%s%s.jpg' % (i, j)
            }] for i in range(0, 2)
            for j in range(0,2)
        }
        for i in range(0, 2):
            for j in range(0, 2):
                dir_name = self.path_test
                with open(os.path.join(
                        dir_name, "image%s%s.jpg" % (i, j)), 'w') as f:
                    f.write('toto')
        self.cfg['manifest'] = self.extended_cfg

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def tearDown(self):
        download.download = self.old_download
        try:
            shutil.rmtree(self.path_test)
            pass
        except Exception as e:
            pass

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = DownloadIMG.load_step('test', 'test', 'step')
        step.process()


    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process2(self):
        mock_download()
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['input_data'] = []
        mockde_db.update(tmp)
        step = DownloadIMG.load_step('test', 'test', 'step')
        step.process()

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process3(self):
        mock_download()
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['limit'] = 1
        mockde_db.update(tmp)
        step = DownloadIMG.load_step('test', 'test', 'step')
        step.process()

    @patch('subprocess.check_call',
           MagicMock(side_effect=mock_subprocess))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process4(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['use_wget'] = 1
        step = DownloadIMG.load_step('test', 'test', 'step')
        step.process()

if __name__ == "__main__":
    unittest.main()

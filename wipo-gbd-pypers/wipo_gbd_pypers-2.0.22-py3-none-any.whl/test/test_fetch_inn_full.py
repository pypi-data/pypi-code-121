import unittest
from pypers.steps.fetch.download.who.inn import Inn
from pypers.utils.utils import dict_update
import os
import shutil
import copy
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock


class MockStream:

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def read(self, *args, **kwargs):
        return ''


class MockPage:

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __init__(self, stop=False):
        self.text = ""
        if stop:
            return
        for i in range(0, 10):
            self.text += '<br> <a class="INN_Hub" href="http://toto.re.re/' \
                         'archive%s.zip?code=1234">' \
                         'archive%i.zip</a>'
            self.text = self.text % (i, i)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __exit__(self, *args, **kwargs):
        pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __enter__(self, *args, **kwargs):
        pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def iter_content(self, *args, **kwargs):
        return 'toto'


nb_call_get = 0


def side_effect_mock_page(*args, **kwargs):
    global nb_call_get
    nb_call_get += 1
    return MockPage(stop=nb_call_get>4)


class TestLire(unittest.TestCase):
    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.fetch.download.who.inn.Inn',
        'sys_path': None,
        'name': 'Full',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {
                    'done_file': os.path.join(path_test, 'done.done'),
                    'credentials': {
                        'client': 'python',
                        'password': 'password'
                    },
                    'url': 'http://my_url.url.com'
                },
                'run_id': 1,
                'log_dir': path_test
            },
            'step': {},
        },
        'output_dir': path_test
    }

    extended_cfg = {
        'new_publication': ['Proposed List 11 - 10 names'],
        'recipients': ['unit_test@wipo.int'],
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

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_exception(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['meta']['pipeline']['input'].pop('url')
        step = Inn.load_step("test", "test", "step")
        try:
            step.process()
            self.fail("Url not found")
        except Exception as e:
            pass

    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process_no_pubications(self):
        tmp = copy.deepcopy(self.cfg)
        mockde_db.update(tmp)
        tmp['new_publication'] = []
        step = Inn.load_step("test", "test", "step")
        self.assertEqual(step.process(), None)

    @patch("requests.sessions.Session.get",
           MagicMock(side_effect=side_effect_mock_page))
    @patch("time.sleep",
           MagicMock(return_value='foo'))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process_from_web(self):
        mockde_db.update(self.cfg)
        step = Inn.load_step("test", "test", "step")
        step.preprocess()
        step.process()
        self.assertEqual(len(step.output_files), 1)


if __name__ == "__main__":
    unittest.main()

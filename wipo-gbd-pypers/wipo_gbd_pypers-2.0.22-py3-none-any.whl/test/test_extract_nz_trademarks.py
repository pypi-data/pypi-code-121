import unittest
from pypers.steps.fetch.extract.nz.trademarks import Trademarks
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil


class MockPage:

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __init__(self, method):
        self.content = ""
        try:
            path_test = os.path.join(os.path.dirname(__file__), 'foo')
            path = os.path.join(path_test, 'inpu2t2', 'xml')
            with open(os.path.join(path, 'F02.xml'), 'w') as f:
                f.write('toto')
            path = os.path.join(path_test, 'inpu2t2', 'img')
            with open(os.path.join(path, 'F02.jpg'), 'w') as f:
                f.write('toto')
        except Exception as e:
            pass
        if method == 'get':
            self.content = '''<?xml version="1.0" encoding="UTF-8"?>
<Transaction xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
  <DesignArticle>
    <MarkImageFilename>
        Foo_bar.jpg
    </MarkImageFilename>
    <MarkImageFilename>
        Foo_bar_2x.jpg
    </MarkImageFilename>
    <MarkImageFilename>
        Foo_bar_4x.jpg
    </MarkImageFilename>
</DesignArticle>
</Transaction>'''
        if method == 'get2':
            self.content = '''<?xml version="1.0" encoding="UTF-8"?>
<Transaction xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
  <DesignArticle>
</DesignArticle>
</Transaction>'''
        if method == 'post2':
            self.content = '''<?xml version="1.0" encoding="UTF-8"?>
    <Transaction xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
        <ObjectFormat>.jpg</ObjectFormat>
        <ObjectData>iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==</ObjectData>
    </Transaction>'''

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __exit__(self, *args, **kwargs):
        pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __enter__(self, *args, **kwargs):
        pass


def mock_page(*args, **kwargs):
    global mock_get_value_counter
    mock_get_value_counter += 1
    if mock_get_value_counter % 2 == 0:
        return MockPage('get2')
    return MockPage('get')


def mock_page2(*args, **kwargs):
    global mock_get_value_counter2
    mock_get_value_counter2 += 1
    return MockPage('post2')


mock_get_value_counter = 0
mock_get_value_counter2 = 0


def mock_get_nodevalue(*args, **kwargs):
    return None


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.nz.trademarks.Trademarks',
        'sys_path': None,
        'name': 'Trademarks',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {
                    'from_api': {
                        'token': '12234',
                        'url': 'http://my_url.url.com'
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
        'input_xml': [os.path.join(path_test, 'input.xml'),
                      os.path.join(path_test, 'input2.xml'),
                      os.path.join(path_test, 'inpu2t2.xml')],
        'img_ref_dir': path_test,
        'api_details': 'details/%s',
        'api_image': 'image/%s'
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        for fin in self.extended_cfg['input_xml']:
            if fin.endswith('t.xml'):
                with open(fin, 'w') as f:
                    f.write('''<?xml version="1.0" encoding="UTF-8"?>
                <Transaction></Transaction>''')
            elif fin.endswith('t2.xml'):
                with open(fin, 'w') as f:
                    f.write('''<?xml version="1.0" encoding="UTF-8"?>
<Trademarks>
    <TradeMark xmlns="http://www.iponz.govt.nz/XMLSchema/trademarks/information">
        <ApplicationNumber>F01</ApplicationNumber>
    </TradeMark>
    <TradeMark xmlns="http://www.iponz.govt.nz/XMLSchema/trademarks/information">
        <ApplicationNumber>F02</ApplicationNumber>
    </TradeMark>
</Trademarks>''')
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
    @patch("requests.sessions.Session.post",
           MagicMock(side_effect=mock_page2))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Trademarks.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()

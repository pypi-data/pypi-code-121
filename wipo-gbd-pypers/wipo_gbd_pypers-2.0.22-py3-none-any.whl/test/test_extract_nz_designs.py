import unittest
from pypers.steps.fetch.extract.nz.designs import Designs
from pypers.utils.utils import dict_update
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import os
import shutil


class MockPage:

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __init__(self, method):
        self.content = ""
        if method == 'error':
            raise Exception()
        if method == 'get':
            self.content = '''<?xml version="1.0" encoding="UTF-8"?>
<Transaction xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
  <DesignArticle>
    <RepresentationSheetFilename>
        Foo_bar.jpg
    </RepresentationSheetFilename>
    <RepresentationSheetFilename>
        Foo_bar_2x.jpg
    </RepresentationSheetFilename>
    <RepresentationSheetFilename>
        Foo_bar_4x.jpg
    </RepresentationSheetFilename>
</DesignArticle>
</Transaction>'''
        if method == 'post':
            self.content = '''<?xml version="1.0" encoding="UTF-8"?>
    <Transaction xmlns="http://www.wipo.int/standards/XMLSchema/trademarks">
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
    if mock_get_value_counter == 1:
        return MockPage('error')
    return MockPage('get')


def mock_page2(*args, **kwargs):
    global mock_get_value_counter2
    mock_get_value_counter2 += 1
    if mock_get_value_counter2 == 1:
        return MockPage('post2')
    return MockPage('post')


mock_get_value_counter = 0
mock_get_value_counter2 = 0


def mock_get_nodevalue(*args, **kwargs):
    return None


class TestMerge(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': ' pypers.steps.fetch.extract.nz.designs.Designs',
        'sys_path': None,
        'name': 'Designs',
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
    <Design xmlns="http://www.iponz.govt.nz/XMLSchema/designs/information">
        <RegistrationNumber>F01</RegistrationNumber>
    </Design>''')

        path = os.path.join(self.path_test, 'F', '01')
        os.makedirs(path)
        path = os.path.join(path, 'F01-0001.1.high.jpg')
        with open(path, 'w') as f:
            f.write("totot")
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
        step = Designs.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()

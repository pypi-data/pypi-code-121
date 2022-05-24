'''
Test for utils.utils
'''
import unittest
from pypers.utils import utils
import os
import shutil
import sys
from contextlib import contextmanager
from io import StringIO
import smtplib
from pypers.core.interfaces.db.test import MockDB
from mock import patch, MagicMock


mockde_db = MockDB()

def mock_db(*args, **kwargs):
    return mockde_db


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def EmptyClass():
    pass


class EmptyObjectClass(object):
    pass


class MockSMTP:
    def __init__(self, server):
        self.result = None

    def close(self):
        pass

    def sendmail(self, f, t, m):
        print("%s %s %s" % (f, t, m))


class Test(unittest.TestCase):

    def setUp(self):
        self.path = 'toto/foo/bar'
        try:
            shutil.rmtree('toto/')
        except Exception as e:
            pass
        os.makedirs(self.path)
        for i in range(10):
            os.mkdir(os.path.join(self.path, '%s_f' % i))
            for j in range(10):
                with open(os.path.join(self.path,
                                       '%s_f' % i,
                                       '%s_f.xml' % j), 'w') as f:
                    f.write("test_file")

    def tearDown(self):
        try:
            shutil.rmtree('toto/')
        except Exception as e:
            pass

    def test_sort_human(self):
        if os.environ.get('SHORT_TEST', None):
            return
        t_input = ['foo1234.xml', 'foo12.xml', 'bar245.xml', 'bar123.xml']
        t_output = ['bar123.xml', 'bar245.xml', 'foo12.xml', 'foo1234.xml']
        self.assertEqual(t_output, utils.sort_human(t_input))

    def test_get_dirs(self):
        if os.environ.get('SHORT_TEST', None):
            return
        t_functions = [utils.get_xsldir, utils.get_tmpldir, utils.get_fabfile,
                       utils.get_fabfile7, utils.get_collconf,
                       utils.get_indexer_root, utils.get_indexer7_root]
        # Test with no env set
        os.environ.pop('PYPERS_HOME', '')
        os.environ.pop('FAB_FILE', '')
        os.environ.pop('INDEXER_HOME', '')
        os.environ.pop('INDEXER7_HOME', '')

        for func in t_functions:
            try:
                func()
                self.fail("The environment is deleted. "
                          "Should raise an execption for %s" % func.__name__)
            except Exception as e:
                pass

        # Test with env
        os.environ['PYPERS_HOME'] = "test/foo/bar"
        os.environ['FAB_FILE'] = "test/foo/bar"
        os.environ['INDEXER_HOME'] = "test/foo/bar"
        os.environ['INDEXER7_HOME'] = "test/foo/bar"

        t_expected = ['test/foo/bar/pypers/xsl',
                      'test/foo/bar/pypers/templates',
                      'test/foo/bar/fabfile.py',
                      'test/foo/bar',
                      'test/foo/bar/coll.yml', 'test/foo/bar', 'test/foo/bar']
        for pos, func in enumerate(t_functions):
            self.assertEqual(func(), t_expected[pos])

    def test_mkdir_p(self):
        if os.environ.get('SHORT_TEST', None):
            return
        dir_path = 'toto/foo'
        path = os.path.join(dir_path, 'bar')
        try:
            shutil.rmtree(path)
        except Exception:
            pass
        # Create a initial folder
        utils.mkdir_p(path)
        self.assertTrue(os.path.exists(path))

        # Verify if the recreating a path
        try:
            utils.mkdir_p(path)
        except Exception as e:
            self.fail("The exception in mkdir_p should have been "
                      "captured before")

        # Verify with other exception
        shutil.rmtree(path)
        utils.mkdir_p(dir_path)
        with open(path, 'w') as f:
            f.write('This is a file')
        try:
            utils.mkdir_p(path)
            self.fail("Should raise an exception before because "
                      "the path is a file")
        except Exception as e:
            pass

    def test_ls_dir(self):
        if os.environ.get('SHORT_TEST', None):
            return
        res = utils.ls_dir(os.path.join(self.path, '*'))
        self.assertEqual(len(res), 10)
        self.assertEqual(res[0], 'toto/foo/bar/0_f')
        res = utils.ls_dir(os.path.join(self.path, '*'), limit=5)
        self.assertEqual(len(res), 5)
        res = utils.ls_dir(os.path.join(self.path, '*'), skip=['0_f', '1_f'])
        self.assertEqual(len(res), 8)
        res = utils.ls_dir(os.path.join(self.path, '*'), regex="[0-9]_toto")
        self.assertEqual(len(res), 0)

    def test_extract(self):
        if os.environ.get('SHORT_TEST', None):
            return
        functions = {
            'zip': utils.zipextract,
            'tar': utils.tarextract,
            'rar': utils.rarextract,
            '7z': utils.sevenzextract,
        }
        for extension in functions.keys():
            f = os.path.join(os.path.dirname(__file__), 'files',
                             'a.%s' % extension)
            try:
                shutil.rmtree('toto/%s/' % extension)
            except Exception:
                pass
            functions[extension](f, 'toto/%s/' % extension)
            self.assertTrue(os.path.exists('toto/%s/empty.csv' % extension))
            try:
                functions[extension](
                    'nofile.%s' % extension, 'toto/%s' % extension)
                self.fail("Should raise an exception in extractor for " %
                          extension)
            except Exception:
                pass

    def test_ziplist(self):
        if os.environ.get('SHORT_TEST', None):
            return
        f = os.path.join(os.path.dirname(__file__), 'files', 'a.zip')
        res = utils.ziplist(f)
        self.assertEqual(res, ['empty.csv'])
        try:
            utils.ziplist('nofile.zip')
            self.fail("Should raise an exception in extractor for zip")
        except Exception:
            pass

    def test_dict_differ(self):
        if os.environ.get('SHORT_TEST', None):
            return
        dict_a = {
            'a': '1',
            'b': '2',
        }
        dict_b = dict_a.copy()
        dict_c = dict_a.copy()
        dict_c['c'] = '3'
        dict_d = dict_a.copy()
        dict_d['a'] = '2'

        self.assertFalse(utils.DictDiffer(dict_a, dict_b))
        self.assertFalse(utils.DictDiffer(dict_a, dict_c))
        self.assertTrue(utils.DictDiffer(dict_a, dict_d))

    def test_import_class(self):
        if os.environ.get('SHORT_TEST', None):
            return
        # Test with no correct package
        try:
            full_name = 'foo/bar'
            utils.import_class(full_name)
            self.fail("No class is present")
        except ImportError as e:
            pass
        # Test with a non object class
        try:
            full_name = 'pypers.utils.test.test_utils.EmptyClass'
            utils.import_class(full_name, config_file='toto')
            self.fail("Class is not extending object")
        except TypeError as e:
            pass

        full_name = 'pypers.utils.test.test_utils.EmptyObjectClass'
        clz = utils.import_class(full_name, config_file='toto')
        self.assertTrue(isinstance(clz(), EmptyObjectClass))

    def test_which(self):
        if os.environ.get('SHORT_TEST', None):
            return
        # Test with no existing command
        exe = 'foo_bar_toto'
        self.assertTrue(utils.which(exe) is None)
        # Test with existing command
        exe = 'python'
        self.assertTrue(utils.which(exe) is not None)

    def test_find(self):
        if os.environ.get('SHORT_TEST', None):
            return
        # Test with no regex
        dir = os.path.join(self.path, '1_f')
        matches = utils.find(dir, '*_f.xml')
        self.assertTrue(len(matches) == 10)
        # Test with regex on
        matches = utils.find(dir, '[1-9]_f.xml', regex=True)
        self.assertTrue(len(matches) == 9)

    def test_find_one(self):
        if os.environ.get('SHORT_TEST', None):
            return
        dir = os.path.join(self.path, '1_f')
        match = utils.find_one(dir, '*_f.xml')
        self.assertTrue('toto/foo/bar/1_f/' in match)
        self.assertTrue('_f.xml' in match)

    def test_pretty_print(self):
        if os.environ.get('SHORT_TEST', None):
            return
        with captured_output() as (out, err):
            utils.pretty_print('toto')
            output = out.getvalue().strip()
        self.assertTrue(output.endswith('toto'))

    def test_dict_update(self):
        if os.environ.get('SHORT_TEST', None):
            return
        dict_a = {
            'a': '1',
            'b': {
                'c': '2',
                'd': '3'
            },
        }
        dict_b = {
            'a': '1',
            'b': {
                'c': '2',
                'd': '5',
                'e': '6'
            },
        }
        expected = {
            'a': '1',
            'b': {
                'c': '2',
                'd': '3',
                'e': '6'
            },
        }
        res = utils.dict_update(dict_a, dict_b, replace=False)
        self.assertEqual(res, expected)
        expected['b']['d'] = '5'
        res = utils.dict_update(dict_a, dict_b)
        self.assertEqual(res, expected)

    def test_has_write_access(self):
        if os.environ.get('SHORT_TEST', None):
            return
        self.assertTrue(utils.has_write_access(self.path))

    def test_template_render(self):
        if os.environ.get('SHORT_TEST', None):
            return
        template = 'test.html'
        os.environ['PYPERS_HOME'] = os.path.join(os.path.dirname(__file__),
                                                 'files')
        res = utils.template_render(template, a=1)
        self.assertEqual(res, '1')

    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_send_mail(self):
        if os.environ.get('SHORT_TEST', None):
            return
        with captured_output() as (out, err):
            utils.send_mail('unit_test@python.org',
                            ['unit_testing@wipo.int'],
                            "test", text='text',
                            html='<html>text</html>',
                            files=[os.path.join(self.path, '1_f', '1_f.xml')])

    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_notify_err(self):
        if os.environ.get('SHORT_TEST', None):
            return

        def caller(conf, logger):
            process_name = 'test_process'
            fetch_id = '1'
            msg = 'test'
            utils.notify_err(conf, logger, process_name, fetch_id, msg)
        self._notification_tester(caller)

    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def test_notify_success(self):
        if os.environ.get('SHORT_TEST', None):
            return

        def caller(conf, logger):
            fetch_id = '1'
            colls = ['1,2,3']
            cores = ['1,2,3']
            utils.notify_success(conf, logger, fetch_id, colls, cores)
        self._notification_tester(caller)

    @patch("boto3.client", MagicMock(side_effect=mock_db))
    def _notification_tester(self, caller):
        if os.environ.get('SHORT_TEST', None):
            return
        conf = {
            '_all_': {
                'notify': {
                    'error': ['unit_testing@wipo.int'],
                    'success': ['unit_testing@wipo.int']
                }
            }
        }
        process_name = 'test_process'
        fetch_id = '1'
        logger = utils.init_logger(self.path, process_name, fetch_id)
        with captured_output() as (out, err):
            caller(conf, logger)
            output = out.getvalue().strip()
        output = output.split('\n')

    def test_appnum_to_subdirs(self):
        if os.environ.get('SHORT_TEST', None):
            return
        self.assertEqual(utils.appnum_to_subdirs('1'), '00/01')
        self.assertEqual(utils.appnum_to_subdirs('1234'), '12/34')
        self.assertEqual(utils.appnum_to_subdirs('123456'), '34/56')
        self.assertEqual(utils.appnum_to_dirs('/test/toto', '123456'),
                         '/test/toto/34/56')


if __name__ == "__main__":
    unittest.main()

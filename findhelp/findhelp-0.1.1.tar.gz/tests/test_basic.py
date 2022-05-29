import unittest
import sys
from findhelp.finder import go_search
from setup_files import setup_tests
from tear_down import tear_down_tests
from findhelp.custom_exceptions import NotValidArgumentError


def main(out=sys.stderr, verbosity=2):
    loader = unittest.TestLoader()

    suite = loader.loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(out, verbosity=verbosity).run(suite)


class BasicTests(unittest.TestCase):
    # sys.stdout = sys.__stdout__
    # print("Captured", capturedOutput.getvalue())
    @classmethod
    def setUpClass(cls):
        setup_tests()

    @classmethod
    def tearDownClass(cls):
        tear_down_tests()

    def test_search_nothing(self):

        base_dict = {
            "stringsearch": "nothing_to_match",
        }
        result = go_search(base_dict)
        self.assertEqual(result, 0)

    def test_search_one(self):
        base_dict = {
            "path": "./__search_tests_dummy_folder__",
            "stringsearch": "one",
            "output": "list"
        }
        result = go_search(base_dict)

        base_result = [
            ['./__search_tests_dummy_folder__',
                'folder', '.', 'one', None, None],
            ['./__search_tests_dummy_folder__/test/dir1', 'file',
                './__search_tests_dummy_folder__/test', 'dir1', 'one.txt', '.txt'],
            ['./__search_tests_dummy_folder__/test/dir2', 'file',
                './__search_tests_dummy_folder__/test', 'dir2', 'one.md', '.md'],
            ['./__search_tests_dummy_folder__/test1', 'file',
                './__search_tests_dummy_folder__', 'test1', 'one.csv', '.csv'],
            ['./__search_tests_dummy_folder__/test2/test01', 'file',
                './__search_tests_dummy_folder__/test2', 'test01', 'one.md', '.md']
        ]

        self.assertListEqual(sorted(base_result), sorted(result))

    def test_extension(self):
        base_dict = {
            "path": ".",
            "output": "list",
            "ext": ["md", "json"]
        }
        result = go_search(base_dict)

        base_result = [
            ['./__search_tests_dummy_folder__/test/dir2', 'file',
                './__search_tests_dummy_folder__/test', 'dir2', 'one.md', '.md'],
            ['./__search_tests_dummy_folder__/test1', 'file',
                './__search_tests_dummy_folder__', 'test1', 'onè.json', '.json'],
            ['./__search_tests_dummy_folder__/test2/test01', 'file',
                './__search_tests_dummy_folder__/test2', 'test01', 'one.md', '.md']
        ]

        self.assertListEqual(sorted(base_result), sorted(result))

    def test_dummy_extension(self):
        base_dict = {
            "path": ".",
            "output": "list",
            "ext": ["dummy"]
        }
        result = go_search(base_dict)
        base_result = []
        self.assertListEqual(sorted(base_result), sorted(result))

    def test_only_dirs(self):
        base_dict = {
            "path": ".",
            "stringsearch": "2",
            "output": "list",
            "onlydirs": True
        }
        result = go_search(base_dict)
        base_result = [
            ['./__search_tests_dummy_folder__',
                'folder', '.', 'test2', None, None],
            ['./__search_tests_dummy_folder__/test', 'folder',
                './__search_tests_dummy_folder__', 'dir2', None, None],
            ['./__search_tests_dummy_folder__/test2', 'folder',
                './__search_tests_dummy_folder__', 'test02', None, None]
        ]
        self.assertListEqual(sorted(base_result), sorted(result))

    def test_only_files(self):
        base_dict = {
            "path": ".",
            "stringsearch": "2",
            "output": "list",
            "onlyfiles": True
        }
        result = go_search(base_dict)
        base_result = [
            ['./__search_tests_dummy_folder__/test2/test01', 'file',
                './__search_tests_dummy_folder__/test2', 'test01', 'file2.mp3', '.mp3'],
            ['./__search_tests_dummy_folder__/test2/test02', 'file',
                './__search_tests_dummy_folder__/test2', 'test02', '2.avi', '.avi']
        ]
        self.assertListEqual(sorted(base_result), sorted(result))

    def test_extension_and_string(self):
        base_dict = {
            "path": ".",
            "stringsearch": "w",
            "output": "list",
            "ext": ["csv", "txt"]
        }
        result = go_search(base_dict)
        base_result = [
            ['./__search_tests_dummy_folder__/test/dir1', 'file',
                './__search_tests_dummy_folder__/test', 'dir1', 'two.txt', '.txt'],
            ['./__search_tests_dummy_folder__/test1', 'file',
                './__search_tests_dummy_folder__', 'test1', 'twò.txt', '.txt']
        ]
        self.assertListEqual(sorted(base_result), sorted(result))

    def test_no_accents(self):
        base_dict = {
            "path": ".",
            "stringsearch": "one",
            "output": "list",
            "ignoreaccents": True
        }
        result = go_search(base_dict)
        base_result = [
            ['./__search_tests_dummy_folder__',
                'folder', '.', 'one', None, None],
            ['./__search_tests_dummy_folder__',
                'folder', '.', 'oné', None, None],
            ['./__search_tests_dummy_folder__', 'file', '.',
                '__search_tests_dummy_folder__', 'oñe', ''],
            ['./__search_tests_dummy_folder__', 'file', '.',
                '__search_tests_dummy_folder__', 'óne', ''],
            ['./__search_tests_dummy_folder__/test/dir1', 'file',
                './__search_tests_dummy_folder__/test', 'dir1', 'one.txt', '.txt'],
            ['./__search_tests_dummy_folder__/test/dir2', 'file',
                './__search_tests_dummy_folder__/test', 'dir2', 'one.md', '.md'],
            ['./__search_tests_dummy_folder__/test1', 'file',
                './__search_tests_dummy_folder__', 'test1', 'one.csv', '.csv'],
            ['./__search_tests_dummy_folder__/test1', 'file',
                './__search_tests_dummy_folder__', 'test1', 'onè.json', '.json'],
            ['./__search_tests_dummy_folder__/test1', 'file',
                './__search_tests_dummy_folder__', 'test1', 'oné.csv', '.csv'],
            ['./__search_tests_dummy_folder__/test2/test01', 'file',
                './__search_tests_dummy_folder__/test2', 'test01', 'one.md', '.md']
        ]
        self.assertListEqual(sorted(base_result), sorted(result))

    def test_use_case(self):
        base_dict = {
            "path": ".",
            "stringsearch": "OnE",
            "output": "list"
        }
        result = go_search(base_dict)
        base_result = []
        self.assertListEqual(sorted(base_result), sorted(result))

    def test_ignore_case(self):
        base_dict = {
            "path": ".",
            "stringsearch": "OnE",
            "output": "list",
            "ignorecase": True
        }
        base_result = [
            ['./__search_tests_dummy_folder__',
                'folder', '.', 'one', None, None],
            ['./__search_tests_dummy_folder__/test/dir1', 'file',
                './__search_tests_dummy_folder__/test', 'dir1', 'one.txt', '.txt'],
            ['./__search_tests_dummy_folder__/test/dir2', 'file',
                './__search_tests_dummy_folder__/test', 'dir2', 'one.md', '.md'],
            ['./__search_tests_dummy_folder__/test1', 'file',
                './__search_tests_dummy_folder__', 'test1', 'one.csv', '.csv'],
            ['./__search_tests_dummy_folder__/test2/test01', 'file',
                './__search_tests_dummy_folder__/test2', 'test01', 'one.md', '.md']
        ]
        result = go_search(base_dict)
        self.assertListEqual(sorted(base_result), sorted(result))

    def test_regexp(self):
        base_dict = {
            "path": ".",
            "stringsearch": "o[nñ][eéè].",
            "output": "list",
            "regexp": True
        }
        base_result = [
            ['./__search_tests_dummy_folder__/test/dir1', 'file',
                './__search_tests_dummy_folder__/test', 'dir1', 'one.txt', '.txt'],
            ['./__search_tests_dummy_folder__/test/dir2', 'file',
                './__search_tests_dummy_folder__/test', 'dir2', 'one.md', '.md'],
            ['./__search_tests_dummy_folder__/test1', 'file',
                './__search_tests_dummy_folder__', 'test1', 'one.csv', '.csv'],
            ['./__search_tests_dummy_folder__/test1', 'file',
                './__search_tests_dummy_folder__', 'test1', 'onè.json', '.json'],
            ['./__search_tests_dummy_folder__/test1', 'file',
                './__search_tests_dummy_folder__', 'test1', 'oné.csv', '.csv'],
            ['./__search_tests_dummy_folder__/test2/test01', 'file',
                './__search_tests_dummy_folder__/test2', 'test01', 'one.md', '.md']
        ]
        result = go_search(base_dict)
        self.assertListEqual(sorted(base_result), sorted(result))

    def test_include_all(self):
        base_dict = {
            "path": ".",
            "stringsearch": "one",
            "output": "list",
            "all": True
        }
        base_result = [
            ['./__search_tests_dummy_folder__',
                'folder', '.', 'one', None, None],
            ['./__search_tests_dummy_folder__/test/dir1', 'file',
                './__search_tests_dummy_folder__/test', 'dir1', 'one.txt', '.txt'],
            ['./__search_tests_dummy_folder__/test/dir2', 'file',
                './__search_tests_dummy_folder__/test', 'dir2', 'one.md', '.md'],
            ['./__search_tests_dummy_folder__/test1', 'file',
                './__search_tests_dummy_folder__', 'test1', 'one.csv', '.csv'],
            ['./__search_tests_dummy_folder__/test2/site-packages', 'file',
                './__search_tests_dummy_folder__/test2', 'site-packages', 'one', ''],
            ['./__search_tests_dummy_folder__/test2/site-packages', 'file',
                './__search_tests_dummy_folder__/test2', 'site-packages', 'one.json', '.json'],
            ['./__search_tests_dummy_folder__/test2/site-packages/site_inside1', 'file',
                './__search_tests_dummy_folder__/test2/site-packages', 'site_inside1', 'sp_one', ''],
            ['./__search_tests_dummy_folder__/test2/site-packages/site_inside1', 'file',
                './__search_tests_dummy_folder__/test2/site-packages', 'site_inside1', 'sp_one.json', '.json'],
            ['./__search_tests_dummy_folder__/test2/test01', 'file',
                './__search_tests_dummy_folder__/test2', 'test01', 'one.md', '.md']
        ]
        result = go_search(base_dict)
        self.assertListEqual(sorted(base_result), sorted(result))

    def test_include_all2(self):
        base_dict = {
            "path": ".",
            "stringsearch": "sp_two",
            "output": "list",
            "all": True
        }
        base_result = [
            ['./__search_tests_dummy_folder__/test2/site-packages/site_inside1', 'file',
                './__search_tests_dummy_folder__/test2/site-packages', 'site_inside1', 'sp_two.csv', '.csv']
        ]
        result = go_search(base_dict)
        self.assertListEqual(sorted(base_result), sorted(result))

    def test_empty_dict(self):
        with self.assertRaises(NotValidArgumentError):
            base_dict = {}
            go_search(base_dict)

    def test_not_directory(self):
        with self.assertRaises(NotADirectoryError):
            base_dict = {
                "path": "?",
                "stringsearch": "whatever"
            }
            go_search(base_dict)

    def test_non_existent_dir(self):
        with self.assertRaises(NotADirectoryError):
            base_dict = {
                "path": "./dummy_folder/",
                "stringsearch": "whathever"
            }
            go_search(base_dict)


if __name__ == "__main__":
    with open('test_basic_results.txt', 'w') as f:
        main(f)

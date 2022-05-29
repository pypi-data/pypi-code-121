import sys
import unittest

from findhelp.finder import go_search
import findhelp.finder as fhp

from setup_files import setup_tests
from tear_down import tear_down_tests


def main(out=sys.stderr, verbosity=2):
    loader = unittest.TestLoader()

    suite = loader.loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(out, verbosity=verbosity).run(suite)


class BasicTests(unittest.TestCase):

    HEADER_RESULT = ["fullpath",
                     "type",
                     "folder_parent",
                     "folder_name",
                     "file_name",
                     "ext"]

    # sys.stdout = sys.__stdout__
    # print("Captured", capturedOutput.getvalue())
    @classmethod
    def setUpClass(cls):
        setup_tests()

    @classmethod
    def tearDownClass(cls):
        pass
        # reset to default
        fhp.set_ignore_folders()
        fhp.set_ignore_extensions()
        tear_down_tests()

    def test_set_ignore_folders(self):
        fhp.set_ignore_folders(["node_modules"])
        base_dict = {
            "path": "./__search_tests_dummy_folder__",
            "stringsearch": "one",
            "output": "list"
        }
        result = go_search(base_dict)
        fhp.set_ignore_folders()
        base_result = [['./__search_tests_dummy_folder__', 'folder', '.', 'one', None, None],
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

        self.assertListEqual(sorted(base_result), sorted(result))

    def test_reset_ignore_folders(self):
        fhp.set_ignore_folders(["site-packages"])
        fhp.set_ignore_folders()
        base_dict = {
            "path": "./__search_tests_dummy_folder__",
            "stringsearch": "one",
            "output": "list"
        }
        result = go_search(base_dict)

        base_result = [
            ['./__search_tests_dummy_folder__', 'folder', '.', 'one', None, None],
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

    def test_set_ignore_extensions(self):
        fhp.set_ignore_extensions([".md", ".txt"])
        base_dict = {
            "path": "./__search_tests_dummy_folder__",
            "stringsearch": "one",
            "output": "list"
        }
        result = go_search(base_dict)
        fhp.set_ignore_extensions()

        base_result = [
            ['./__search_tests_dummy_folder__', 'folder', '.', 'one', None, None],
            ['./__search_tests_dummy_folder__/test1', 'file',
                './__search_tests_dummy_folder__', 'test1', 'one.csv', '.csv'],
        ]

        self.assertListEqual(sorted(base_result), sorted(result))

    def test_reset_ignore_extensions(self):
        fhp.set_ignore_extensions(["md", "txt"])
        fhp.set_ignore_extensions()
        base_dict = {
            "path": "./__search_tests_dummy_folder__",
            "stringsearch": "one",
            "output": "list"
        }
        result = go_search(base_dict)

        base_result = [
            ['./__search_tests_dummy_folder__', 'folder', '.', 'one', None, None],
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


if __name__ == "__main__":
    with open('test_config_results.txt', 'w') as f:
        main(f)

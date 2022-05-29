import sys
import unittest
import json
import os
import pandas as pd
from pandas.util.testing import assert_frame_equal

from findhelp.finder import go_search
from setup_files import setup_tests
from tear_down import tear_down_tests


def join_key(dict):
    full_key = ""
    for key, value in dict.items():
        if value != None:
            full_key += value
    return full_key


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
        if os.path.exists("_test_result.json"):
            os.remove("_test_result.json")

        if os.path.exists("_test_result.csv"):
            os.remove("_test_result.csv")

        if os.path.exists("_test_result.txt"):
            os.remove("_test_result.txt")
        tear_down_tests()

    def test_data_frame(self):
        base_dict = {
            "path": "./__search_tests_dummy_folder__",
            "stringsearch": "one",
            "output": "df"
        }

        base_result = pd.DataFrame(
            [
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
            ],
            columns=self.HEADER_RESULT
        )
        result = go_search(base_dict)

        result = result.sort_values(
            by=result.columns.tolist()).reset_index(drop=True)
        base_result = base_result.sort_values(
            by=base_result.columns.tolist()).reset_index(drop=True)
        assert_frame_equal(result, base_result)

    def test_basic_json(self):
        base_dict = {
            "path": "./__search_tests_dummy_folder__",
            "stringsearch": "one",
            "output": "json",
            "outputfilename": "_test_result"
        }
        go_search(base_dict)
        base_result = [
            {
                "fullpath": "./__search_tests_dummy_folder__",
                "type": "folder",
                "folder_parent": ".",
                "folder_name": "one",
                "file_name": None,
                "ext": None
            },
            {
                "fullpath": "./__search_tests_dummy_folder__/test/dir1",
                "type": "file",
                "folder_parent": "./__search_tests_dummy_folder__/test",
                "folder_name": "dir1",
                "file_name": "one.txt",
                "ext": ".txt"
            },
            {
                "fullpath": "./__search_tests_dummy_folder__/test/dir2",
                "type": "file",
                "folder_parent": "./__search_tests_dummy_folder__/test",
                "folder_name": "dir2",
                "file_name": "one.md",
                "ext": ".md"
            },
            {
                "fullpath": "./__search_tests_dummy_folder__/test1",
                "type": "file",
                "folder_parent": "./__search_tests_dummy_folder__",
                "folder_name": "test1",
                "file_name": "one.csv",
                "ext": ".csv"
            },
            {
                "fullpath": "./__search_tests_dummy_folder__/test2/test01",
                "type": "file",
                "folder_parent": "./__search_tests_dummy_folder__/test2",
                "folder_name": "test01",
                "file_name": "one.md",
                "ext": ".md"
            }
        ]

        with open("_test_result.json") as f:
            result = json.load(f)

        self.assertListEqual(sorted(result["results"], key=lambda x: join_key(
            x)), sorted(base_result, key=lambda x: join_key(x)))

    def test_basic_txt(self):
        base_dict = {
            "path": "./__search_tests_dummy_folder__",
            "stringsearch": "one",
            "output": "txt",
            "outputfilename": "_test_result"
        }

        base_result = pd.DataFrame(
            [
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
            ],
            columns=self.HEADER_RESULT
        )
        go_search(base_dict)
        result = pd.read_csv("_test_result.txt", sep="\t")

        result = result.sort_values(
            by=result.columns.tolist()).reset_index(drop=True)
        base_result = base_result.sort_values(
            by=base_result.columns.tolist()).reset_index(drop=True)
        assert_frame_equal(result, base_result)

    def test_basic_csv(self):
        base_dict = {
            "path": "./__search_tests_dummy_folder__",
            "stringsearch": "one",
            "output": "csv",
            "outputfilename": "_test_result"
        }

        base_result = pd.DataFrame(
            [
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
            ],
            columns=self.HEADER_RESULT
        )
        go_search(base_dict)
        result = pd.read_csv("_test_result.csv", sep="\t")

        result = result.sort_values(
            by=result.columns.tolist()).reset_index(drop=True)
        base_result = base_result.sort_values(
            by=base_result.columns.tolist()).reset_index(drop=True)
        assert_frame_equal(result, base_result)

    def test_basic_obj(self):
        base_dict = {
            "path": "./__search_tests_dummy_folder__",
            "stringsearch": "one",
            "output": "obj_list"
        }
        base_result = [
            {
                "fullpath": "./__search_tests_dummy_folder__",
                "type": "folder",
                "folder_parent": ".",
                "folder_name": "one",
                "file_name": None,
                "ext": None
            },
            {
                "fullpath": "./__search_tests_dummy_folder__/test/dir1",
                "type": "file",
                "folder_parent": "./__search_tests_dummy_folder__/test",
                "folder_name": "dir1",
                "file_name": "one.txt",
                "ext": ".txt"
            },
            {
                "fullpath": "./__search_tests_dummy_folder__/test/dir2",
                "type": "file",
                "folder_parent": "./__search_tests_dummy_folder__/test",
                "folder_name": "dir2",
                "file_name": "one.md",
                "ext": ".md"
            },
            {
                "fullpath": "./__search_tests_dummy_folder__/test1",
                "type": "file",
                "folder_parent": "./__search_tests_dummy_folder__",
                "folder_name": "test1",
                "file_name": "one.csv",
                "ext": ".csv"
            },
            {
                "fullpath": "./__search_tests_dummy_folder__/test2/test01",
                "type": "file",
                "folder_parent": "./__search_tests_dummy_folder__/test2",
                "folder_name": "test01",
                "file_name": "one.md",
                "ext": ".md"
            }
        ]

        result = go_search(base_dict)
        self.assertListEqual(sorted(result, key=lambda x: join_key(
            x)), sorted(base_result, key=lambda x: join_key(x)))


if __name__ == "__main__":
    with open('test_output_results.txt', 'w') as f:
        main(f)

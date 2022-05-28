# -*- coding:utf-8 -*-
from __future__ import absolute_import

import os
import unittest

from pyxtools.basic_tools import get_pretty_float
from pyxtools.basic_tools.cache_tools import FileCache
from pyxtools.basic_tools.file_tools import get_base_name_of_file
from pyxtools.basic_tools.iterator_utils import random_choice, iter_list_with_size


class TestBasicTools(unittest.TestCase):
    def test_iter_list_with_size(self):
        src_list = [i for i in range(100)]
        raw_src_list = list(src_list)

        dst_list = []
        for part_list in iter_list_with_size(src_list, 20):
            dst_list.extend(part_list)

        self.assertEqual(len(raw_src_list), len(dst_list))
        self.assertEqual(sum(raw_src_list), sum(dst_list))
        self.assertEqual(len(src_list), 0)

    def test_cache(self):
        cache_file = "./cache.pkl"
        cache = FileCache(pickle_file=cache_file)
        test_dict = {"a": "b", "A": 0}

        # simple set
        for key, value in test_dict.items():
            cache.set(key, value)

        # test get
        self.assertEqual(cache.get("a"), test_dict.get("a"))
        self.assertEqual(cache.get("A"), test_dict.get("A"))
        self.assertEqual(cache.get("c"), test_dict.get("c"))

        # unsafe set
        cache.unsafe_set("X", "x")
        self.assertEqual(cache.get("X"), "x")

        # unsafe
        another = FileCache(pickle_file=cache_file)
        self.assertEqual(another.get("a"), test_dict.get("a"))
        self.assertEqual(another.get("A"), test_dict.get("A"))
        self.assertEqual(another.get("c"), test_dict.get("c"))
        self.assertEqual(another.get("X"), None)

        if os.path.exists(cache_file):
            os.remove(cache_file)

    def testGetBaseName(self):
        get_base_name_of_file("E:\\R\\a")
        self.assertEqual(get_base_name_of_file("./a"), "a")
        self.assertEqual(get_base_name_of_file("./a/"), "a")
        self.assertEqual(get_base_name_of_file("./a/c"), "c")
        self.assertEqual(get_base_name_of_file("./a//c"), "c")
        self.assertEqual(get_base_name_of_file("./a//b/c"), "c")
        self.assertEqual(get_base_name_of_file("./a//b/c/"), "c")

        self.assertEqual(get_base_name_of_file("E:\\R\\a"), "a")
        self.assertEqual(get_base_name_of_file("E:\\R\\a\\"), "a")
        self.assertEqual(get_base_name_of_file("E:\\R\\a\\c"), "c")
        self.assertEqual(get_base_name_of_file("E:\\R\\a\\c"), "c")
        self.assertEqual(get_base_name_of_file("E:\\R\\a\\b\\c"), "c")
        self.assertEqual(get_base_name_of_file("E:\\R\\a\\b\\c\\"), "c")

    def testPrettyFloat(self):
        self.assertEqual(get_pretty_float(1000.24575, count=1), "1E+3")
        self.assertEqual(get_pretty_float(1000.24575, count=2), "1.0E+3")
        self.assertEqual(get_pretty_float(1000.24575, count=3), "1.00E+3")
        self.assertEqual(get_pretty_float(1000.24575, count=4), "1000")
        self.assertEqual(get_pretty_float(1000.24575, count=5), "1000.2")
        self.assertEqual(get_pretty_float(1000.24575, count=6), "1000.25")
        self.assertEqual(get_pretty_float(1000.24575, count=7), "1000.246")
        self.assertEqual(get_pretty_float(1000.24575, count=8), "1000.2458")

    def testRandomChoice(self):
        rl = [i for i in range(10000)]

        x1 = random_choice(rl, k=100, unique=True)
        y1 = random_choice(rl, k=100, unique=True)

        self.assertTrue(len(set(x1)) == 100)
        self.assertTrue(len(set(y1)) == 100)
        self.assertFalse(";".join([str(i) for i in x1]) == ";".join([str(i) for i in y1]))

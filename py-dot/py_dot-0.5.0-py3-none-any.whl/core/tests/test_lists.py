import unittest

from py_dot.core.lists import safe_insert


class TestLists(unittest.TestCase):
    def test_safe_insert1(self):
        target = []
        self.assertListEqual(
            safe_insert(target, 1, 1),
            [None, 1]
        )

    def test_safe_insert2(self):
        target = []
        self.assertListEqual(
            safe_insert(target, 2, 1),
            [None, None, 1]
        )

    def test_safe_insert3(self):
        target = [1]
        self.assertListEqual(
            safe_insert(target, 2, 1),
            [1, None, 1]
        )
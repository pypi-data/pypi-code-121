import unittest

from py_dot.core.dicts import merge


class TestDicts(unittest.TestCase):

    def test_merge(self):
        self.assertListEqual(
            merge({'1': [1]}, {'1': [2]})['1'],
            [1, 2]
        )

    def test_merge_dict(self):
        self.assertDictEqual(
            merge({'1': {'a': 1}}, {'1': {'b': 2}}),
            {
                '1': {
                    'a': 1,
                    'b': 2
                }
            }
        )

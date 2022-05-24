import unittest

from py_dot.core.dicts import merge


class TestDicts(unittest.TestCase):

    def test_merge_list(self):
        self.assertListEqual(
            merge({'1': [1]}, {'1': [2]})['1'],
            [1, 2]
        )

    def test_merge_dict(self):
        self.assertDictEqual(
            merge(
                {
                    'a': {'a': 1},
                    'b': {'b': 2},
                    'd': {'d': 4}
                },
                {
                    'a': {'a': 'a'},
                    'c': {'c': 3},
                    'd': {'dd': 4}
                }
            ),
            {
                'a': {
                    'a': 'a'
                },
                'b': {
                    'b': 2
                },
                'c': {
                    'c': 3
                },
                'd': {
                    'd': 4,
                    'dd': 4
                }
            }
        )

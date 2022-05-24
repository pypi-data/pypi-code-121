import unittest
from dataclasses import dataclass

from allthethings.iterables import dedup, grouper


class IterablesTestCase(unittest.TestCase):
    def test_grouper(self):
        result = [*grouper([1, 2, 3, 4, 5, 6, 7], n=3)]
        self.assertEqual([[1, 2, 3], [4, 5, 6], [7]], result)

    def test_dedup(self):
        result = [*dedup([1, 2, 3, 2, 1])]
        self.assertEqual([1, 2, 3], result)

    def test_dedup_on(self):
        @dataclass
        class X:
            a: str
            b: str

        xs = [X("one", "foo"), X("one", "bar"), X("two", "baz"), X("one", "qux"), X("three", "baz")]
        self.assertEqual([X("one", "foo"), X("two", "baz"), X("three", "baz")], list(dedup(xs, on=lambda x: x.a)))


if __name__ == '__main__':
    unittest.main()

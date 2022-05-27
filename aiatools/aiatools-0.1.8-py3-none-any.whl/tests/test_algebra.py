import unittest
from aiatools.algebra import *


class AndTest(unittest.TestCase):
    def test_eval_true(self):
        x = and_(identity, True)
        self.assertTrue(x(True))

    def test_eval_false(self):
        x = and_(identity, True)
        self.assertFalse(x(False))

    def test_repr(self):
        x = and_(True, True)
        self.assertEqual('True & True', '%r' % x)


class OrTest(unittest.TestCase):
    def test_eval_true(self):
        x = or_(identity, False)
        self.assertTrue(x(True))

    def test_eval_false(self):
        x = or_(identity, False)
        self.assertFalse(x(False))

    def test_repr(self):
        x = or_(True, True)
        self.assertEqual('True | True', '%r' % x)


class NotTest(unittest.TestCase):
    def test_eval_true(self):
        x = not_(identity)
        self.assertTrue(x(False))

    def test_eval_false(self):
        x = not_(identity)
        self.assertFalse(x(True))

    def test_repr(self):
        x = not_(True)
        self.assertEqual('~True', '%r' % x)
        x = not_(not_(True) == False)
        self.assertEqual('~(~True == False)', '%r' % x)

    def test_invert(self):
        x = not_(True)
        self.assertTrue(~x)

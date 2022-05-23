import unittest
from lumipy.common.lockable import Lockable
from test.unit.utilities.test_utils import assert_locked_lockable


class TestClass(Lockable):

    def __init__(self, a, b, c):
        self.A = a
        self.B = b
        self.C = c
        super().__init__()


class TestLockable(unittest.TestCase):

    def test_lockable_base_class_immutability(self):

        lockable = TestClass(a=1, b=2, c=3)

        self.assertEqual(lockable.A, 1)
        self.assertEqual(lockable.B, 2)
        self.assertEqual(lockable.C, 3)

        assert_locked_lockable(self, lockable)

#!/usr/bin/env python3

import sys
import unittest
import math
from pyquats.quats import Quat


class TestQuat(unittest.TestCase):

    def setUp(self):
        self.zero = Quat()
        self.one = Quat(1)
        self.ii = Quat(0, 1, 0, 0)
        self.jj = Quat(0, 0, 1, 0)
        self.kk = Quat(0, 0, 0, 1)
        self.q1 = Quat(1, 2, 3, 4)
        self.q2 = Quat(1, 1, 1, 1)
        self.q3 = Quat(1.1, 2.2, 3.3, 4.4)
        self.q4 = Quat(-1.2, -2.3, -3.4, -4.5)
        self.c1 = 1J
        self.c2 = 1 + 2J

    def test_print(self):
        #self.assertEqual(str(self.zero),"0.0+0.0i+0.0j+0.0k")
        #self.assertEqual(str(self.q4),"-1.2-2.3i-3.4j-4.5k")
        self.assertEqual(repr(self.zero),"Quat(0.0, 0.0, 0.0, 0.0)")
        self.assertEqual(repr(self.q1),"Quat(1.0, 2.0, 3.0, 4.0)")
        self.assertEqual(repr(self.q4),"Quat(-1.2, -2.3, -3.4, -4.5)")
        #print ( sys.getsizeof(self.q1) ) # 72 in Py2.7, 56 in Py3.7

    def test_getitem(self):
        self.assertEqual(self.q1[0], 1)
        self.assertEqual(self.q1[1], 2)
        self.assertEqual(self.q1[2], 3)
        self.assertEqual(self.q1[3], 4)
        self.assertRaises(IndexError, self.q1.__getitem__, 5)

    def test_add(self):
        self.assertEqual(self.q1 + self.q2, Quat(2, 3, 4, 5))
        self.assertEqual(self.q1 + self.c1, Quat(1, 3, 3, 4))
        self.assertEqual(self.c2 + self.q2, Quat(2, 3, 1, 1))

    def test_sub(self):
        self.assertEqual(self.q1 - self.q2, Quat(0, 1, 2, 3))
        self.assertEqual(self.q1 - self.c2, Quat(0, 0, 3, 4))
        self.assertEqual(self.c2 - self.q2, Quat(0, 1, -1, -1))

    def test_mul(self):
        self.assertEqual(self.q1 * self.zero, self.zero)
        self.assertEqual(self.q1 * self.one, self.q1)
        # i*j=k, i*1=j*j=k*k=-1
        self.assertEqual(self.ii * self.jj, self.kk)
        self.assertEqual(self.jj * self.ii, Quat(0, 0, 0, -1))
        self.assertEqual(self.ii * self.ii, Quat(-1))
        self.assertEqual(self.jj * self.jj, Quat(-1))
        self.assertEqual(self.kk * self.kk, Quat(-1))
        # test complex
        self.assertEqual(self.c2 * Quat(3, 4), Quat(3, 4) * self.c2)
        self.assertEqual(self.q1 * self.c2, Quat(-3, 4, 11, -2))
        self.assertEqual(self.c2 * self.q1, Quat(-3, 4, -5, 10))

    def test_nonzero(self):
        self.assertTrue(bool(Quat(1)))
        self.assertFalse(bool(Quat()))
        self.assertEqual("a", "a" if Quat(1) else "b")
        self.assertEqual("b", "a" if Quat() else "b")

    def test_pos_neg(self):
        self.assertEqual(+self.q1, self.q1)
        self.assertEqual(-self.q1, Quat(-1, -2, -3, -4))
        self.assertEqual(self.jj * self.ii, -self.kk)
        self.assertEqual(self.ii * self.ii, -self.one)
        self.assertEqual(self.jj * self.jj, -self.one)
        self.assertEqual(self.kk * self.kk, -self.one)

    def test_is_unit(self):
        self.assertTrue(self.one.is_unit())
        self.assertTrue(self.ii.is_unit())
        self.assertTrue(self.jj.is_unit())
        self.assertTrue(self.kk.is_unit())
        self.assertTrue(Quat(0.5, 0.5, 0.5, 0.5).is_unit())
        self.assertFalse(self.q1.is_unit())
        self.assertFalse(self.q2.is_unit())

    def test_conjugate(self):
        self.assertEqual(self.q1.conjugate(), Quat(1, -2, -3, -4))
        self.assertEqual(self.one.conjugate(), self.one)

    def test_invert(self):
        self.assertEqual(~self.q2, Quat(0.25, -0.25, -0.25, -0.25))
        self.assertEqual(~self.one, self.one)

    def test_abs(self):
        self.assertEqual(abs(self.zero), 0)
        self.assertEqual(abs(self.one), 1)
        self.assertEqual(abs(self.ii), 1)
        self.assertEqual(abs(self.jj), 1)
        self.assertEqual(abs(self.kk), 1)
        self.assertEqual(abs(self.q2), 2)

    def test_pow(self):
        self.assertEqual(self.q1 ** 0, self.one)
        self.assertEqual(self.q1 ** 0, 1)
        self.assertEqual(self.q1 ** 1, self.q1)
        self.assertEqual(self.q1 ** 2, self.q1 * self.q1)
        self.assertEqual(self.ii ** 4, self.one)
        self.assertEqual(self.ii ** 400, self.one)

    def test_conversion(self):
        self.assertRaises(TypeError, int, self.one)
        #self.assertRaises(TypeError, long, self.one)   # Python 2 only
        self.assertRaises(TypeError, float, self.one)
        self.assertRaises(TypeError, complex, self.one)

    def test_hash(self):
        aset = set()
        aset.add(self.ii)
        aset.add(self.ii)  # ignored
        self.assertEqual(len(aset), 1)
        aset.add(self.jj)
        aset.add(self.kk)
        self.assertEqual(len(aset), 3)

    def test_from_rotations(self):
        self.assertAlmostEqual(Quat.from_x_rotation(math.pi), self.ii)
        self.assertAlmostEqual(Quat.from_y_rotation(math.pi), self.jj)
        self.assertAlmostEqual(Quat.from_z_rotation(math.pi), self.kk)

    def test_from_eulers(self):
        self.assertAlmostEqual(Quat.from_eulers(0, math.pi, 0), self.jj)
        self.assertAlmostEqual(Quat.from_eulers(math.pi, 0, 0), self.kk)
        self.assertAlmostEqual(Quat.from_eulers(0, 0, math.pi), self.kk)

    def test_random_quat(self):
        uniax = Quat.random_quat_uniax()
        biax = Quat.random_quat_biax()
        unit = Quat.random_unit_quat()
        move = Quat.random_move_quat(0.5)
        self.assertAlmostEqual(abs(uniax), 1)
        self.assertAlmostEqual(abs(biax), 1)
        self.assertAlmostEqual(abs(unit), 1)
        self.assertAlmostEqual(abs(move), 1)

    def tearDown(self): pass

if __name__== "__main__":

    unittest.main()

# EOF

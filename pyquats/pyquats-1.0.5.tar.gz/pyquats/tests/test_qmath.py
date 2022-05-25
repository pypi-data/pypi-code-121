#!/usr/bin/env python3

import unittest
import math
import cmath
import pyquats.qmath as qmath
from pyquats.quats import Quat


class TestQuatMath(unittest.TestCase):

    def setUp(self):
        self.f1 = 3.0
        self.f2 = 4.0
        self.c1 = 3J
        self.c2 = 1 + 2J

    def test_exp(self):
        self.assertAlmostEqual(qmath.exp(self.f1), math.exp(self.f1))
        self.assertAlmostEqual(qmath.exp(self.c1), cmath.exp(self.c1))
        self.assertAlmostEqual(qmath.exp(self.c2), cmath.exp(self.c2))
        self.assertAlmostEqual(qmath.exp(Quat(self.f1)), math.exp(self.f1))
        self.assertAlmostEqual(qmath.exp(Quat(0, 3)), cmath.exp(3J))
        self.assertAlmostEqual(qmath.exp(Quat(4, 5)), cmath.exp(4 + 5J))
        self.assertAlmostEqual(qmath.exp(Quat(0, math.pi)), -1.0)
        self.assertAlmostEqual(qmath.exp(Quat(0, 0, math.pi)), -1.0)
        self.assertAlmostEqual(qmath.exp(Quat(0, 0, 0, math.pi)), -1.0)
        self.assertAlmostEqual(qmath.exp(Quat(self.f1, 0, self.f2)),
            math.exp(self.f1) * Quat(math.cos(self.f2), 0, math.sin(self.f2)))
        self.assertAlmostEqual(qmath.exp(Quat(self.f1, 0, 0, self.f2)),
            math.exp(self.f1) * Quat(math.cos(self.f2), 0, 0, math.sin(self.f2)))

    def test_log(self):
        self.assertAlmostEqual(qmath.log(self.f1), math.log(self.f1))
        self.assertAlmostEqual(qmath.log(self.c1), cmath.log(self.c1))
        self.assertAlmostEqual(qmath.log(self.c2), cmath.log(self.c2))

    def test_sin(self):
        self.assertAlmostEqual(qmath.sin(self.f1), math.sin(self.f1))
        self.assertAlmostEqual(qmath.sin(self.c1), cmath.sin(self.c1))
        self.assertAlmostEqual(qmath.sin(self.c2), cmath.sin(self.c2))
        self.assertAlmostEqual(qmath.sin(Quat(self.f1)), math.sin(self.f1))
        self.assertAlmostEqual(qmath.sin(Quat(0, 3)), cmath.sin(3J))
        self.assertAlmostEqual(qmath.sin(Quat(4, 5)), cmath.sin(4 + 5J))
        self.assertAlmostEqual(qmath.sin(Quat(0, self.f1)), Quat(0, math.sinh(self.f1)))

    def test_cos(self):
        self.assertAlmostEqual(qmath.cos(self.f1), math.cos(self.f1))
        self.assertAlmostEqual(qmath.cos(self.c1), cmath.cos(self.c1))
        self.assertAlmostEqual(qmath.cos(self.c2), cmath.cos(self.c2))
        self.assertAlmostEqual(qmath.cos(Quat(self.f1)), math.cos(self.f1))
        self.assertAlmostEqual(qmath.cos(Quat(0, 3)), cmath.cos(3J))
        self.assertAlmostEqual(qmath.cos(Quat(4, 5)), cmath.cos(4 + 5J))
        self.assertAlmostEqual(qmath.cos(Quat(0, self.f1)), Quat(math.cosh(self.f1)))

    def test_sinh(self):
        self.assertAlmostEqual(qmath.sinh(self.f1), math.sinh(self.f1))
        self.assertAlmostEqual(qmath.sinh(self.c1), cmath.sinh(self.c1))
        self.assertAlmostEqual(qmath.sinh(self.c2), cmath.sinh(self.c2))
        self.assertAlmostEqual(qmath.sinh(Quat(self.f1)), math.sinh(self.f1))
        self.assertAlmostEqual(qmath.sinh(Quat(0, 3)), cmath.sinh(3J))
        self.assertAlmostEqual(qmath.sinh(Quat(4, 5)), cmath.sinh(4 + 5J))
        self.assertAlmostEqual(qmath.sinh(Quat(0, self.f1)), Quat(0, math.sin(self.f1)))

    def test_cosh(self):
        self.assertAlmostEqual(qmath.cosh(self.f1), math.cosh(self.f1))
        self.assertAlmostEqual(qmath.cosh(self.c1), cmath.cosh(self.c1))
        self.assertAlmostEqual(qmath.cosh(self.c2), cmath.cosh(self.c2))
        self.assertAlmostEqual(qmath.cosh(Quat(self.f1)), math.cosh(self.f1))
        self.assertAlmostEqual(qmath.cosh(Quat(0, 3)), cmath.cosh(3J))
        self.assertAlmostEqual(qmath.cosh(Quat(4, 5)), cmath.cosh(4 + 5J))
        self.assertAlmostEqual(qmath.cosh(Quat(0, self.f1)), Quat(math.cos(self.f1)))

    def tearDown(self): pass

if __name__== "__main__":

    unittest.main()

# EOF

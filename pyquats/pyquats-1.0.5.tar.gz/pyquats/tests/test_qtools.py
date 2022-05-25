#!/usr/bin/env python3

import unittest
import math
from pyquats.quats import Quat
from pyquats.qtools import rotate1
from pyquats.qtools import rotate2
from pyquats.qtools import rotate3
from pyquats.qtools import random_quat_uniax
from pyquats.qtools import random_quat_biax
from pyquats.qtools import random_unit_quat
from pyquats.qtools import random_move_quat
from pyquats.qtools import random_quat_Xwall
from pyquats.qtools import random_quat_Ywall
from pyquats.qtools import random_quat_Zwall
from pyquats.qtools import random_move_Xwall
from pyquats.qtools import random_move_Ywall
from pyquats.qtools import random_move_Zwall


class TestRotations(unittest.TestCase):

    def setUp(self):
        self.rotX180 = Quat(0, 1, 0, 0)
        self.rotY180 = Quat(0, 0, 1, 0)
        self.rotZ180 = Quat(0, 0, 0, 1)
        p2 = math.sqrt(0.5)
        p3 = math.sqrt(1.0 / 3.0)
        self.rotX90 = Quat(p2, p2, 0, 0)
        self.rotY90 = Quat(p2, 0, p2, 0)
        self.rotZ90 = Quat(p2, 0, 0, p2)
        # obrot o kat 120 stopni wokol [0,1,1,1]
        self.rot120 = Quat(0.5, 0.5, 0.5, 0.5)
        self.vec1 = [p3, p3, p3]

    def test_rot_quat(self):
        # obroty o 180 sa przemienne, ale daja inne quat
        self.assertAlmostEqual(self.rotX180 * self.rotY180, Quat(0, 0, 0, 1))
        self.assertAlmostEqual(self.rotY180 * self.rotX180, Quat(0, 0, 0, -1))
        # 90+90=180
        # assertAlmostEqual potrzebuje metody __abs__ do dzialania
        self.assertAlmostEqual(self.rotX90 * self.rotX90, self.rotX180)
        self.assertAlmostEqual(self.rotY90 * self.rotY90, self.rotY180)
        self.assertAlmostEqual(self.rotZ90 * self.rotZ90, self.rotZ180)
        # obroty o 90
        self.assertAlmostEqual(self.rotX90 * self.rotY90, self.rot120)
        self.assertAlmostEqual(self.rotY90 * self.rotZ90, self.rot120)
        self.assertAlmostEqual(self.rotZ90 * self.rotX90, self.rot120)
        self.assertAlmostEqual(self.rotY90 * self.rotX90, Quat(0.5, 0.5, 0.5, -0.5))
        self.assertAlmostEqual(self.rotZ90 * self.rotY90, Quat(0.5, -0.5, 0.5, 0.5))
        self.assertAlmostEqual(self.rotX90 * self.rotZ90, Quat(0.5, 0.5, -0.5, 0.5))
        self.assertAlmostEqual(self.rotX90, Quat.rot_quat([1, 0, 0], math.pi * 0.5))
        self.assertAlmostEqual(self.rotY90, Quat.rot_quat([0, 1, 0], math.pi * 0.5))
        self.assertAlmostEqual(self.rotZ90, Quat.rot_quat([0, 0, 1], math.pi * 0.5))
        self.assertAlmostEqual(self.rot120, Quat.rot_quat(self.vec1, math.pi * 2.0 / 3.0))

    def test_rot_vectors(self):
        # Listy nie mozna odejmowac i obliczac abs(L).
        # Potrzebna klasa Vector.
        pairs = []
        pairs.append((rotate1([10, 0, 0], self.rotZ90), [0, 10, 0]))
        pairs.append((rotate2([10, 0, 0], [0, 0, 1], math.pi * 0.5), [0, 10, 0]))
        pairs.append((rotate1([0,10, 0], self.rot120), [0, 0, 10]))
        pairs.append((rotate2([0, 10, 0], self.vec1, math.pi * 2.0 / 3.0), [0, 0, 10]))
        pairs.append((rotate3([0, 0, 10], 0, math.pi * 0.5, 0), [10, 0, 0]))
        pairs.append((rotate3([10, 0, 0], math.pi * 0.5, 0, 0), [0, 10, 0]))
        pairs.append((rotate3([10, 0, 0], math.pi * 0.5, 0, 0), [0, 10, 0]))
        # Po kolei porownuje wyniki po wspolrzednych.
        for left, right in pairs:
            self.assertAlmostEqual(left[0], right[0])
            self.assertAlmostEqual(left[1], right[1])
            self.assertAlmostEqual(left[2], right[2])

    def test_random_quat(self):
        uniax = random_quat_uniax()
        biax = random_quat_biax()
        unit = random_unit_quat()
        move = random_move_quat(0.5)
        self.assertAlmostEqual(abs(uniax), 1)
        self.assertAlmostEqual(abs(biax), 1)
        self.assertAlmostEqual(abs(unit), 1)
        self.assertAlmostEqual(abs(move), 1)

    def test_wall(self):
        biax = random_quat_Xwall()
        self.assertAlmostEqual(abs(biax), 1)
        #print(biax.q)
        biax = random_quat_Ywall()
        self.assertAlmostEqual(abs(biax), 1)
        #print(biax.q)
        biax = random_quat_Zwall()
        self.assertAlmostEqual(abs(biax), 1)
        #print(biax.q)
        biax = random_move_Xwall(0.25)
        self.assertEqual(biax.q[2], 0)
        self.assertEqual(biax.q[3], 0)
        self.assertAlmostEqual(abs(biax), 1)
        #print(biax.q)
        biax = random_move_Ywall(0.25)
        self.assertEqual(biax.q[1], 0)
        self.assertEqual(biax.q[3], 0)
        self.assertAlmostEqual(abs(biax), 1)
        #print(biax.q)
        biax = random_move_Zwall(0.25)
        self.assertEqual(biax.q[1], 0)
        self.assertEqual(biax.q[2], 0)
        self.assertAlmostEqual(abs(biax), 1)
        #print(biax.q)

    def tearDown(self): pass

if __name__== "__main__":

    unittest.main()

# EOF

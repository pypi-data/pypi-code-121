import logging
logging.disable(logging.CRITICAL)
import unittest
import numpy as np
from random import uniform
from dataUncert.variable import variable


class test(unittest.TestCase):

    def testSingleNumber(self):
        A = variable(1.3, 'm')
        B = variable(2.0, 'm', 0.01)
        C = variable([1.0, 1.3], 'L/min', np.array([20, 30]))
        D = variable(np.array([11, 1111]), 'L/min', [2.1, 3.9])
        self.assertEqual(A.value, 1.3)
        self.assertEqual(A.unit, 'm')
        self.assertEqual(A.uncert, 0)
        self.assertEqual(B.value, 2.0)
        self.assertEqual(B.unit, 'm')
        self.assertEqual(B.uncert, 0.01)
        np.testing.assert_equal(C.value, [1.0, 1.3])
        self.assertEqual(C.unit, 'L/min')
        np.testing.assert_equal(C.uncert, [20, 30])
        np.testing.assert_equal(D.value, [11.0, 1111.0])
        self.assertEqual(D.unit, 'L/min')
        np.testing.assert_equal(D.uncert, [2.1, 3.9])

        with self.assertRaises(Exception) as context:
            variable(1.3, 'm', 'hej')
        self.assertTrue("could not convert string to float: 'hej'" in str(context.exception))

        with self.assertRaises(Exception) as context:
            variable('med', 'm', 1.0)
        self.assertTrue("could not convert string to float: 'med'" in str(context.exception))

        with self.assertRaises(Exception) as context:
            variable(1.3, 'm', [1.0, 2.3])
        self.assertTrue("The value is a number but the uncertanty is a <class 'list'>" in str(context.exception))

        with self.assertRaises(Exception) as context:
            variable(1.3, 'm', np.array([1.0, 2.3]))
        self.assertTrue("The value is a number but the uncertanty is a <class 'numpy.ndarray'>" in str(context.exception))

        with self.assertRaises(Exception) as context:
            variable(np.array([1.0, 2.3]), 'm', 1.5)
        self.assertTrue("The value is a list-like object but the uncertanty is a number" in str(context.exception))

        with self.assertRaises(Exception) as context:
            variable([1.0, 2.3], 'm', 1.5)
        self.assertTrue("The value is a list-like object but the uncertanty is a number" in str(context.exception))

    def test_add(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'L/min', uncert=53.9)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'L/min', uncert=[53.9, 24.75, 6.4])

        C = A + B
        self.assertAlmostEqual(C.value, 12.3 + 745.1)
        self.assertEqual(C.unit, 'L/min')
        self.assertAlmostEqual(C.uncert, np.sqrt((1 * 2.6)**2 + (1 * 53.9)**2))

        C.convert('m3/s')
        self.assertAlmostEqual(C.value, (12.3 + 745.1) / 1000 / 60)
        self.assertEqual(C.unit, 'm3/s')
        self.assertAlmostEqual(C.uncert, np.sqrt((1 * 2.6 / 1000 / 60)**2 + (1 * 53.9 / 1000 / 60)**2))

        C_vec = A_vec + B_vec
        np.testing.assert_array_equal(C_vec.value, np.array([12.3 + 745.1, 54.3 + 496.13, 91.3 + 120.54]))
        self.assertEqual(C_vec.unit, 'L/min')
        np.testing.assert_array_equal(
            C_vec.uncert,
            np.array([
                np.sqrt((1 * 2.6)**2 + (1 * 53.9)**2),
                np.sqrt((1 * 5.4)**2 + (1 * 24.75)**2),
                np.sqrt((1 * 10.56)**2 + (1 * 6.4)**2),
            ]))

        C_vec.convert('mL/h')
        np.testing.assert_almost_equal(C_vec.value, np.array([(12.3 + 745.1) * 1000 * 60, (54.3 + 496.13) * 1000 * 60, (91.3 + 120.54) * 1000 * 60]))
        self.assertEqual(C_vec.unit, 'mL/h')
        np.testing.assert_almost_equal(
            C_vec.uncert,
            np.array([
                np.sqrt((1 * 2.6 * 1000 * 60)**2 + (1 * 53.9 * 1000 * 60)**2),
                np.sqrt((1 * 5.4 * 1000 * 60)**2 + (1 * 24.75 * 1000 * 60)**2),
                np.sqrt((1 * 10.56 * 1000 * 60)**2 + (1 * 6.4 * 1000 * 60)**2),
            ]))

    def test_sub(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'L/min', uncert=53.9)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'L/min', uncert=[53.9, 24.75, 6.4])

        C = A - B
        self.assertAlmostEqual(C.value, 12.3 - 745.1)
        self.assertEqual(C.unit, 'L/min')
        self.assertAlmostEqual(C.uncert, np.sqrt((1 * 2.6)**2 + (1 * 53.9)**2))

        C.convert('kL/s')
        self.assertAlmostEqual(C.value, (12.3 - 745.1) / 1000 / 60)
        self.assertEqual(C.unit, 'kL/s')
        self.assertAlmostEqual(C.uncert, np.sqrt((1 * 2.6 / 1000 / 60)**2 + (1 * 53.9 / 1000 / 60)**2))

        C_vec = A_vec - B_vec
        np.testing.assert_array_equal(C_vec.value, np.array([12.3 - 745.1, 54.3 - 496.13, 91.3 - 120.54]))
        self.assertEqual(C_vec.unit, 'L/min')
        np.testing.assert_array_equal(
            C_vec.uncert,
            np.array([
                np.sqrt((1 * 2.6)**2 + (1 * 53.9)**2),
                np.sqrt((1 * 5.4)**2 + (1 * 24.75)**2),
                np.sqrt((1 * 10.56)**2 + (1 * 6.4)**2),
            ]))

        C_vec.convert('mm3 / h')
        np.testing.assert_almost_equal(C_vec.value, np.array([12.3 - 745.1, 54.3 - 496.13, 91.3 - 120.54]) * 1000000 * 60, decimal=5)
        self.assertEqual(C_vec.unit, 'mm3/h')
        np.testing.assert_almost_equal(
            C_vec.uncert,
            np.array([
                np.sqrt((1 * 2.6 * 1000000 * 60)**2 + (1 * 53.9 * 1000000 * 60)**2),
                np.sqrt((1 * 5.4 * 1000000 * 60)**2 + (1 * 24.75 * 1000000 * 60)**2),
                np.sqrt((1 * 10.56 * 1000000 * 60)**2 + (1 * 6.4 * 1000000 * 60)**2),
            ]), decimal=5)

        with self.assertRaises(Exception) as context:
            A.convert('m')
        self.assertTrue('You cannot convert from [L/min] to [m]' in str(context.exception))

    def test_add_with_different_units(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'm', uncert=53.9)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm', uncert=[53.9, 24.75, 6.4])

        with self.assertRaises(Exception) as context:
            A + B
        self.assertTrue('You tried to add a variable in [L/min] to a variable in [m], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            A_vec + B_vec
        self.assertTrue('You tried to add a variable in [L/min] to a variable in [m], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            A.convert('m')
        self.assertTrue('You cannot convert from [L/min] to [m]' in str(context.exception))

    def test_sub_with_different_units(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'm', uncert=53.9)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm', uncert=[53.9, 24.75, 6.4])

        with self.assertRaises(Exception) as context:
            A - B
        self.assertTrue('You tried to subtract a variable in [m] from a variable in [L/min], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            A_vec - B_vec
        self.assertTrue('You tried to subtract a variable in [m] from a variable in [L/min], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            A.convert('m')
        self.assertTrue('You cannot convert from [L/min] to [m]' in str(context.exception))

    def test_multiply(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'm', uncert=53.9)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm', uncert=[53.9, 24.75, 6.4])

        C = A * B

        self.assertAlmostEqual(C.value, 12.3 * 745.1)
        self.assertEqual(C.unit, 'L-m/min')
        self.assertAlmostEqual(C.uncert, np.sqrt((745.1 * 2.6)**2 + (12.3 * 53.9)**2))

        C_vec = A_vec * B_vec
        np.testing.assert_array_equal(C_vec.value, np.array([12.3 * 745.1, 54.3 * 496.13, 91.3 * 120.54]))
        self.assertEqual(C_vec.unit, 'L-m/min')
        np.testing.assert_array_equal(
            C_vec.uncert,
            np.array([
                np.sqrt((745.1 * 2.6)**2 + (12.3 * 53.9)**2),
                np.sqrt((496.13 * 5.4)**2 + (54.3 * 24.75)**2),
                np.sqrt((120.54 * 10.56)**2 + (91.3 * 6.4)**2),
            ]))

        C_vec.convert('m3-km / s')
        np.testing.assert_array_equal(C_vec.value, np.array([12.3 * 745.1, 54.3 * 496.13, 91.3 * 120.54]) / 1000 / 1000 / 60)
        self.assertEqual(C_vec.unit, 'm3-km/s')
        np.testing.assert_almost_equal(
            C_vec.uncert,
            np.array([
                np.sqrt((745.1 / 1000 * 2.6 / 1000 / 60)**2 + (12.3 / 1000 / 60 * 53.9 / 1000)**2),
                np.sqrt((496.13 / 1000 * 5.4 / 1000 / 60)**2 + (54.3 / 1000 / 60 * 24.75 / 1000)**2),
                np.sqrt((120.54 / 1000 * 10.56 / 1000 / 60)**2 + (91.3 / 1000 / 60 * 6.4 / 1000)**2),
            ]), decimal=7)

    def test_divide(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'm', uncert=53.9)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm', uncert=[53.9, 24.75, 6.4])

        C = A / B
        self.assertAlmostEqual(C.value, 12.3 / 745.1)
        self.assertEqual(C.unit, 'L/min-m')
        self.assertAlmostEqual(C.uncert, np.sqrt((1 / 745.1 * 2.6)**2 + (12.3 / (745.1**2) * 53.9)**2))

        C.convert('m3/h-mm')
        self.assertAlmostEqual(C.value, 12.3 / 745.1 / 1000 * 60 / 1000)
        self.assertEqual(C.unit, 'm3/h-mm')
        self.assertAlmostEqual(C.uncert, np.sqrt((1 / (745.1 * 1000) * 2.6 / 1000 * 60)**2 + (12.3 / ((745.1)**2) * 53.9 / 1000 * 60 / 1000)**2))

        C_vec = A_vec / B_vec
        np.testing.assert_array_equal(C_vec.value, np.array([12.3 / 745.1, 54.3 / 496.13, 91.3 / 120.54]))
        self.assertEqual(C_vec.unit, 'L/min-m')
        np.testing.assert_array_equal(
            C_vec.uncert,
            np.array([
                np.sqrt((1 / 745.1 * 2.6)**2 + (12.3 / (745.1)**2 * 53.9)**2),
                np.sqrt((1 / 496.13 * 5.4)**2 + (54.3 / (496.13)**2 * 24.75)**2),
                np.sqrt((1 / 120.54 * 10.56)**2 + (91.3 / (120.54)**2 * 6.4)**2),
            ]))

        C_vec.convert('m3 / h -mm')
        np.testing.assert_almost_equal(C_vec.value, np.array([12.3 / 745.1, 54.3 / 496.13, 91.3 / 120.54]) / 1000 * 60 / 1000)
        self.assertEqual(C_vec.unit, 'm3/h-mm')
        np.testing.assert_almost_equal(
            C_vec.uncert,
            np.array([
                np.sqrt((1 / 745.1 * 2.6 / 1000 * 60 / 1000)**2 + (12.3 / (745.1)**2 * 53.9 / 1000 * 60 / 1000)**2),
                np.sqrt((1 / 496.13 * 5.4 / 1000 * 60 / 1000)**2 + (54.3 / (496.13)**2 * 24.75 / 1000 * 60 / 1000)**2),
                np.sqrt((1 / 120.54 * 10.56 / 1000 * 60 / 1000)**2 + (91.3 / (120.54)**2 * 6.4 / 1000 * 60 / 1000)**2),
            ]))

    def test_add_unit_order(self):
        A = variable(10, 'm-K')
        B = variable(3, 'K-m')
        A_vec = variable([12.3, 54.3, 91.3], 'K-m', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm-K', uncert=[53.9, 24.75, 6.4])
        C = A + B
        C_vec = A_vec + B_vec

    def test_sub_unit_order(self):
        A = variable(10, 'm-K')
        B = variable(3, 'K-m')
        A_vec = variable([12.3, 54.3, 91.3], 'K-m', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm-K', uncert=[53.9, 24.75, 6.4])
        C = A - B
        C_vec = A_vec - B_vec

    def test_pow(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'm', uncert=53.9)
        C = variable(745.1, '1', uncert=53.9)
        D = variable(0.34, '1', uncert=0.01)

        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm', uncert=[53.9, 24.75, 6.4])
        C_vec = variable([745.1, 496.13, 120.54], '1', uncert=[53.9, 24.75, 6.4])
        D_vec = variable([0.34, 0.64, 0.87], '1', uncert=[0.01, 0.084, 0.12])

        with self.assertRaises(Exception) as context:
            A ** B
        self.assertTrue('The exponent can not have a unit' in str(context.exception))

        with self.assertRaises(Exception) as context:
            A_vec ** B_vec
        self.assertTrue('The exponent can not have a unit' in str(context.exception))

        E = C**D
        self.assertAlmostEqual(E.value, 745.1**0.34)
        self.assertEqual(E.unit, '1')
        self.assertAlmostEqual(E.uncert, np.sqrt((0.34 * 745.1**(0.34 - 1) * 53.9)**2 + (745.1**0.34 * np.log(745.1) * 0.01)**2))

        E_vec = C_vec**D_vec
        np.testing.assert_array_equal(E_vec.value, np.array([745.1**0.34, 496.13**0.64, 120.54**0.87]))
        self.assertEqual(E_vec.unit, '1')
        np.testing.assert_array_equal(
            E_vec.uncert,
            np.array([
                np.sqrt((0.34 * 745.1**(0.34 - 1) * 53.9)**2 + (745.1**0.34 * np.log(745.1) * 0.01)**2),
                np.sqrt((0.64 * 496.13**(0.64 - 1) * 24.75)**2 + (496.13**0.64 * np.log(496.13) * 0.084)**2),
                np.sqrt((0.87 * 120.54**(0.87 - 1) * 6.4)**2 + (120.54**0.87 * np.log(120.54) * 0.12)**2)
            ]))

        F = A**2
        self.assertAlmostEqual(F.value, (12.3)**2)
        self.assertEqual(F.unit, 'L2/min2')
        self.assertAlmostEqual(F.uncert, np.sqrt((2 * 12.3**(2 - 1) * 2.6)**2))

        F.convert('m6/s2')
        self.assertAlmostEqual(F.value, (12.3 / 1000 / 60)**2)
        self.assertEqual(F.unit, 'm6/s2')
        self.assertAlmostEqual(F.uncert, np.sqrt((2 * (12.3 / 1000 / 60)**(2 - 1) * 2.6 / 1000 / 60)**2))

        F_vec = A_vec**2
        np.testing.assert_array_equal(F_vec.value, np.array([(12.3)**2, 54.3**2, 91.3**2]))
        self.assertEqual(F_vec.unit, 'L2/min2')
        np.testing.assert_array_equal(
            F_vec.uncert,
            np.array([
                np.sqrt((2 * 12.3**(2 - 1) * 2.6)**2),
                np.sqrt((2 * 54.3**(2 - 1) * 5.4)**2),
                np.sqrt((2 * 91.3**(2 - 1) * 10.56)**2)
            ]))

        F_vec.convert('m6 / s2')
        np.testing.assert_almost_equal(F_vec.value, np.array([(12.3 / 1000 / 60)**2, (54.3 / 1000 / 60)**2, (91.3 / 1000 / 60)**2]))
        self.assertEqual(F_vec.unit, 'm6/s2')
        np.testing.assert_almost_equal(
            F_vec.uncert,
            np.array([
                np.sqrt((2 * 12.3 / 1000 / 60**(2 - 1) * 2.6 / 1000 / 60)**2),
                np.sqrt((2 * 54.3 / 1000 / 60**(2 - 1) * 5.4 / 1000 / 60)**2),
                np.sqrt((2 * 91.3 / 1000 / 60**(2 - 1) * 10.56 / 1000 / 60)**2)
            ]))

        G = 2.54**D
        self.assertAlmostEqual(G.value, 2.54**0.34)
        self.assertEqual(G.unit, '1')
        self.assertAlmostEqual(G.uncert, np.sqrt((2.54**0.34 * np.log(2.54) * 0.01)**2))

        G_vec = 2.54**D_vec
        np.testing.assert_array_equal(G_vec.value, np.array([2.54**0.34, 2.54**0.64, 2.54**0.87]))
        self.assertEqual(G_vec.unit, '1')
        np.testing.assert_array_equal(
            G_vec.uncert,
            np.array([
                2.54**0.34 * np.log(2.54) * 0.01,
                2.54**0.64 * np.log(2.54) * 0.084,
                2.54**0.87 * np.log(2.54) * 0.12
            ]))

    def test_log(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        C = variable(745.1, '1', uncert=53.9)

        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        C_vec = variable([745.1, 496.13, 120.54], '1', uncert=[53.9, 24.75, 6.4])

        with self.assertRaises(Exception) as context:
            np.log(A)
        self.assertTrue('You can only take the natural log of a variable if it has no unit' in str(context.exception))

        with self.assertRaises(Exception) as context:
            np.log10(A)
        self.assertTrue('You can only take the base 10 log of a variable if it has no unit' in str(context.exception))

        with self.assertRaises(Exception) as context:
            np.log(A_vec)
        self.assertTrue('You can only take the natural log of a variable if it has no unit' in str(context.exception))

        with self.assertRaises(Exception) as context:
            np.log10(A_vec)
        self.assertTrue('You can only take the base 10 log of a variable if it has no unit' in str(context.exception))

        D = np.log(C)
        self.assertAlmostEqual(D.value, np.log(745.1))
        self.assertEqual(D.unit, '1')
        self.assertAlmostEqual(D.uncert, np.sqrt((1 / 745.1) * 53.9)**2)

        D_vec = np.log(C_vec)
        np.testing.assert_array_equal(D_vec.value, np.array([np.log(745.1), np.log(496.13), np.log(120.54)]))
        self.assertEqual(D_vec.unit, '1')
        np.testing.assert_array_equal(
            D_vec.uncert,
            np.array([
                np.sqrt(((1 / 745.1) * 53.9)**2),
                np.sqrt(((1 / 496.13) * 24.75)**2),
                np.sqrt(((1 / 120.54) * 6.4)**2)
            ]))

        E = np.log10(C)
        self.assertAlmostEqual(E.value, np.log10(745.1))
        self.assertEqual(E.unit, '1')
        self.assertAlmostEqual(E.uncert, np.sqrt((1 / (745.1 * np.log10(745.1))) * 53.9)**2)

        E_vec = np.log10(C_vec)
        np.testing.assert_array_equal(E_vec.value, np.array([np.log10(745.1), np.log10(496.13), np.log10(120.54)]))
        self.assertEqual(E_vec.unit, '1')
        np.testing.assert_array_equal(
            E_vec.uncert,
            np.array([
                np.sqrt(((1 / (745.1 * np.log10(745.1))) * 53.9)**2),
                np.sqrt(((1 / (496.13 * np.log10(496.13))) * 24.75)**2),
                np.sqrt(((1 / (120.54 * np.log10(120.54))) * 6.4)**2)
            ]))

    def test_exp(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        C = variable(12.3, '1', uncert=5.39)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        C_vec = variable([12.3, 54.3, 91.3], '1', uncert=[2.6, 5.4, 10.56])

        with self.assertRaises(Exception) as context:
            np.exp(A)
        self.assertTrue('The exponent can not have a unit' in str(context.exception))

        with self.assertRaises(Exception) as context:
            np.exp(A_vec)
        self.assertTrue('The exponent can not have a unit' in str(context.exception))

        D = np.exp(C)
        self.assertAlmostEqual(D.value, np.e**12.3)
        self.assertEqual(D.unit, '1')
        self.assertAlmostEqual(D.uncert, np.sqrt((np.e**12.3 * np.log(np.e) * 5.39)**2))

        D_vec = np.exp(C_vec)
        np.testing.assert_array_equal(D_vec.value, np.array([np.e**12.3, np.e**54.3, np.e**91.3]))
        self.assertEqual(D_vec.unit, '1')
        np.testing.assert_array_equal(
            D_vec.uncert,
            np.array([
                np.sqrt((np.e**12.3 * np.log(np.e) * 2.6)**2),
                np.sqrt((np.e**54.3 * np.log(np.e) * 5.4)**2),
                np.sqrt((np.e**91.3 * np.log(np.e) * 10.56)**2)
            ]))

    def testIndex(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])

        a = A[0]
        self.assertEqual(a.value, 12.3)
        self.assertEqual(a.unit, 'L/min')
        self.assertEqual(a.uncert, 2.6)

        a_vec = A_vec[0, 1]
        np.testing.assert_equal(a_vec.value, [12.3, 54.3])
        self.assertEqual(a_vec.unit, 'L/min')
        np.testing.assert_equal(a_vec.uncert, [2.6, 5.4])

        a_vec = A_vec[0, 2]
        np.testing.assert_equal(a_vec.value, [12.3, 91.3])
        self.assertEqual(a_vec.unit, 'L/min')
        np.testing.assert_equal(a_vec.uncert, [2.6, 10.56])

        a_vec = A_vec[2, 0]
        np.testing.assert_equal(a_vec.value, [91.3, 12.3])
        self.assertEqual(a_vec.unit, 'L/min')
        np.testing.assert_equal(a_vec.uncert, [10.56, 2.6])

        with self.assertRaises(Exception) as context:
            a = A[1]
        self.assertTrue('index 1 is out of bounds for axis 0 with size 1' in str(context.exception))

        with self.assertRaises(Exception) as context:
            a = A[23]
        self.assertTrue('index 23 is out of bounds for axis 0 with size 1' in str(context.exception))

    def testAddEqual(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'L/min', uncert=53.9)

        A += B
        self.assertEqual(A.value, 12.3 + 745.1)
        self.assertEqual(A.unit, 'L/min')
        self.assertEqual(A.uncert, np.sqrt((1 * 2.6)**2 + (1 * 53.9)**2))
        A = variable(12.3, 'L/min', uncert=2.6)

        A += 2
        self.assertEqual(A.value, 12.3 + 2)
        self.assertEqual(A.unit, 'L/min')
        self.assertEqual(A.uncert, np.sqrt((1 * 2.6)**2))

        A = variable(12.3, 'L/min', uncert=2.6)
        B = 2
        B += A
        self.assertEqual(B.value, 2 + 12.3)
        self.assertEqual(B.unit, 'L/min')
        self.assertEqual(B.uncert, np.sqrt((1 * 2.6)**2))

        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'L/min', uncert=[53.9, 24.75, 6.4])

        A_vec += B_vec
        np.testing.assert_array_equal(A_vec.value, np.array([12.3 + 745.1, 54.3 + 496.13, 91.3 + 120.54]))
        self.assertEqual(A_vec.unit, 'L/min')
        np.testing.assert_array_equal(
            A_vec.uncert,
            np.array([
                np.sqrt((1 * 2.6)**2 + (1 * 53.9)**2),
                np.sqrt((1 * 5.4)**2 + (1 * 24.75)**2),
                np.sqrt((1 * 10.56)**2 + (1 * 6.4)**2),
            ]))

        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        A = variable(12.3, 'L/min', uncert=2.6)
        A_vec += A
        np.testing.assert_array_equal(A_vec.value, np.array([12.3 + 12.3, 54.3 + 12.3, 91.3 + 12.3]))
        self.assertEqual(A_vec.unit, 'L/min')
        np.testing.assert_array_equal(
            A_vec.uncert,
            np.array([
                np.sqrt((1 * 2.6)**2 + (1 * 2.6)**2),
                np.sqrt((1 * 5.4)**2 + (1 * 2.6)**2),
                np.sqrt((1 * 10.56)**2 + (1 * 2.6)**2),
            ]))

        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'm', uncert=53.9)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm', uncert=[53.9, 24.75, 6.4])

        with self.assertRaises(Exception) as context:
            A += B
        self.assertTrue('You tried to add a variable in [L/min] to a variable in [m], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            B += A
        self.assertTrue('You tried to add a variable in [m] to a variable in [L/min], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            A_vec += B_vec
        self.assertTrue('You tried to add a variable in [L/min] to a variable in [m], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            B_vec += A_vec
        self.assertTrue('You tried to add a variable in [m] to a variable in [L/min], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            A_vec += B
        self.assertTrue('You tried to add a variable in [L/min] to a variable in [m], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            B_vec += A
        self.assertTrue('You tried to add a variable in [m] to a variable in [L/min], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            A += B_vec
        self.assertTrue('You tried to add a variable in [L/min] to a variable in [m], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            B += A_vec
        self.assertTrue('You tried to add a variable in [m] to a variable in [L/min], but the units does not match' in str(context.exception))

    def testSubEqual(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'L/min', uncert=53.9)

        A -= B
        self.assertEqual(A.value, 12.3 - 745.1)
        self.assertEqual(A.unit, 'L/min')
        self.assertEqual(A.uncert, np.sqrt((1 * 2.6)**2 + (1 * 53.9)**2))
        A = variable(12.3, 'L/min', uncert=2.6)

        A -= 2
        self.assertEqual(A.value, 12.3 - 2)
        self.assertEqual(A.unit, 'L/min')
        self.assertEqual(A.uncert, np.sqrt((1 * 2.6)**2))

        A = variable(12.3, 'L/min', uncert=2.6)
        B = 2
        B -= A
        self.assertEqual(B.value, 2 - 12.3)
        self.assertEqual(B.unit, 'L/min')
        self.assertEqual(B.uncert, np.sqrt((1 * 2.6)**2))

        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'L/min', uncert=[53.9, 24.75, 6.4])

        A_vec -= B_vec
        np.testing.assert_array_equal(A_vec.value, np.array([12.3 - 745.1, 54.3 - 496.13, 91.3 - 120.54]))
        self.assertEqual(A_vec.unit, 'L/min')
        np.testing.assert_array_equal(
            A_vec.uncert,
            np.array([
                np.sqrt((1 * 2.6)**2 + (1 * 53.9)**2),
                np.sqrt((1 * 5.4)**2 + (1 * 24.75)**2),
                np.sqrt((1 * 10.56)**2 + (1 * 6.4)**2),
            ]))

        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        A = variable(12.3, 'L/min', uncert=2.6)
        A_vec -= A
        np.testing.assert_array_equal(A_vec.value, np.array([12.3 - 12.3, 54.3 - 12.3, 91.3 - 12.3]))
        self.assertEqual(A_vec.unit, 'L/min')
        np.testing.assert_array_equal(
            A_vec.uncert,
            np.array([
                np.sqrt((1 * 2.6)**2 + (1 * 2.6)**2),
                np.sqrt((1 * 5.4)**2 + (1 * 2.6)**2),
                np.sqrt((1 * 10.56)**2 + (1 * 2.6)**2),
            ]))

        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'm', uncert=53.9)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm', uncert=[53.9, 24.75, 6.4])

        with self.assertRaises(Exception) as context:
            A -= B
        self.assertTrue('You tried to subtract a variable in [m] from a variable in [L/min], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            B -= A
        self.assertTrue('You tried to subtract a variable in [L/min] from a variable in [m], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            A_vec -= B_vec
        self.assertTrue('You tried to subtract a variable in [m] from a variable in [L/min], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            B_vec -= A_vec
        self.assertTrue('You tried to subtract a variable in [L/min] from a variable in [m], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            A_vec -= B
        self.assertTrue('You tried to subtract a variable in [m] from a variable in [L/min], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            B_vec -= A
        self.assertTrue('You tried to subtract a variable in [L/min] from a variable in [m], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            A -= B_vec
        self.assertTrue('You tried to subtract a variable in [m] from a variable in [L/min], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            B -= A_vec
        self.assertTrue('You tried to subtract a variable in [L/min] from a variable in [m], but the units does not match' in str(context.exception))

    def testMultiEqual(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'm', uncert=53.9)

        A *= B
        self.assertEqual(A.value, 12.3 * 745.1)
        self.assertEqual(A.unit, 'L-m/min')
        self.assertEqual(A.uncert, np.sqrt((745.1 * 2.6)**2 + (12.3 * 53.9)**2))

        A = variable(12.3, 'L/min', uncert=2.6)
        A *= 2
        self.assertEqual(A.value, 12.3 * 2)
        self.assertEqual(A.unit, 'L/min')
        self.assertEqual(A.uncert, np.sqrt((2 * 2.6)**2))

        A = variable(12.3, 'L/min', uncert=2.6)
        B = 2
        B *= A
        self.assertEqual(B.value, 12.3 * 2)
        self.assertEqual(B.unit, 'L/min')
        self.assertEqual(B.uncert, np.sqrt((2 * 2.6)**2))

        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm', uncert=[53.9, 24.75, 6.4])

        A_vec *= B_vec
        np.testing.assert_array_equal(A_vec.value, np.array([12.3 * 745.1, 54.3 * 496.13, 91.3 * 120.54]))
        self.assertEqual(A_vec.unit, 'L-m/min')
        np.testing.assert_array_equal(
            A_vec.uncert,
            np.array([
                np.sqrt((745.1 * 2.6)**2 + (12.3 * 53.9)**2),
                np.sqrt((496.13 * 5.4)**2 + (54.3 * 24.75)**2),
                np.sqrt((120.54 * 10.56)**2 + (91.3 * 6.4)**2),
            ]))

        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        A = variable(12.3, 'L/min', uncert=2.6)
        A_vec *= A
        np.testing.assert_array_equal(A_vec.value, np.array([12.3 * 12.3, 54.3 * 12.3, 91.3 * 12.3]))
        self.assertEqual(A_vec.unit, 'L2/min2')
        np.testing.assert_array_equal(
            A_vec.uncert,
            np.array([
                np.sqrt((12.3 * 2.6)**2 + (12.3 * 2.6)**2),
                np.sqrt((12.3 * 5.4)**2 + (54.3 * 2.6)**2),
                np.sqrt((12.3 * 10.56)**2 + (91.3 * 2.6)**2),
            ]))

    def testDivEqual(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'm', uncert=53.9)

        A /= B
        self.assertEqual(A.value, 12.3 / 745.1)
        self.assertEqual(A.unit, 'L/min-m')
        self.assertEqual(A.uncert, np.sqrt((1 / 745.1 * 2.6)**2 + (12.3 / (745.1**2) * 53.9)**2))

        A = variable(12.3, 'L/min', uncert=2.6)
        A /= 2
        self.assertEqual(A.value, 12.3 / 2)
        self.assertEqual(A.unit, 'L/min')
        self.assertEqual(A.uncert, np.sqrt((1 / 2 * 2.6)**2))

        A = variable(12.3, 'L/min', uncert=2.6)
        B = 2
        B /= A
        self.assertEqual(B.value, 2 / 12.3)
        self.assertEqual(B.unit, 'min/L')
        self.assertEqual(B.uncert, np.sqrt((2 / (12.3**2) * 2.6)**2))

        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm', uncert=[53.9, 24.75, 6.4])

        A_vec /= B_vec
        np.testing.assert_array_equal(A_vec.value, np.array([12.3 / 745.1, 54.3 / 496.13, 91.3 / 120.54]))
        self.assertEqual(A_vec.unit, 'L/min-m')
        np.testing.assert_array_equal(
            A_vec.uncert,
            np.array([
                np.sqrt((1 / 745.1 * 2.6)**2 + (12.3 / (745.1**2) * 53.9)**2),
                np.sqrt((1 / 496.13 * 5.4)**2 + (54.3 / (496.13**2) * 24.75)**2),
                np.sqrt((1 / 120.54 * 10.56)**2 + (91.3 / (120.54**2) * 6.4)**2),
            ]))

        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        A = variable(12.3, 'L/min', uncert=2.6)
        A_vec /= A
        np.testing.assert_array_equal(A_vec.value, np.array([12.3 / 12.3, 54.3 / 12.3, 91.3 / 12.3]))
        self.assertEqual(A_vec.unit, '1')
        np.testing.assert_array_equal(
            A_vec.uncert,
            np.array([
                np.sqrt((1 / 12.3 * 2.6)**2 + (12.3 / (12.3**2) * 2.6)**2),
                np.sqrt((1 / 12.3 * 5.4)**2 + (54.3 / (12.3**2) * 2.6)**2),
                np.sqrt((1 / 12.3 * 10.56)**2 + (91.3 / (12.3**2) * 2.6)**2),
            ]))

    def testPrintValueAndUncertScalar(self):
        A = variable(123456789 * 10**(0), 'm', uncert=123456789 * 10**(-2), nDigits=3)
        self.assertEqual(A.__str__(), '123000000 +/- 1000000 [m]')

        A = variable(123456789 * 10**(-2), 'm', uncert=123456789 * 10**(-4), nDigits=3)
        self.assertEqual(A.__str__(), '1230000 +/- 10000 [m]')

        A = variable(123456789 * 10**(-4), 'm', uncert=123456789 * 10**(-6), nDigits=3)
        self.assertEqual(A.__str__(), '12300 +/- 100 [m]')

        A = variable(123456789 * 10**(-6), 'm', uncert=123456789 * 10**(-8), nDigits=3)
        self.assertEqual(A.__str__(), '123 +/- 1 [m]')

        A = variable(123456789 * 10**(-7), 'm', uncert=123456789 * 10**(-9), nDigits=3)
        self.assertEqual(A.__str__(), '12.3 +/- 0.1 [m]')

        A = variable(123456789 * 10**(-8), 'm', uncert=123456789 * 10**(-10), nDigits=3)
        self.assertEqual(A.__str__(), '1.23 +/- 0.01 [m]')

        A = variable(123456789 * 10**(-9), 'm', uncert=123456789 * 10**(-11), nDigits=3)
        self.assertEqual(A.__str__(), '0.123 +/- 0.001 [m]')

        A = variable(123456789 * 10**(-10), 'm', uncert=123456789 * 10**(-12), nDigits=3)
        self.assertEqual(A.__str__(), '0.0123 +/- 0.0001 [m]')

        A = variable(123456789 * 10**(-12), 'm', uncert=123456789 * 10**(-14), nDigits=3)
        self.assertEqual(A.__str__(), '0.000123 +/- 1e-06 [m]')

        A = variable(123456789 * 10**(-14), 'm', uncert=123456789 * 10**(-16), nDigits=3)
        self.assertEqual(A.__str__(), '0.00000123 +/- 1e-08 [m]')

        A = variable(123456789 * 10**(-16), 'm', uncert=123456789 * 10**(-18), nDigits=3)
        self.assertEqual(A.__str__(), '0.0000000123 +/- 1e-10 [m]')

        A = variable(10.0, 'm', uncert=0.1)
        self.assertEqual(A.__str__(), '10.0 +/- 0.1 [m]')

    def testPrintValueScalar(self):
        A = variable(123456789 * 10**(0), 'm', nDigits=6)
        self.assertEqual(A.__str__(), '1.23457e+08 [m]')

        A = variable(123456789 * 10**(-2), 'm', nDigits=7)
        self.assertEqual(A.__str__(), '1234568 [m]')

        A = variable(123456789 * 10**(-4), 'm', nDigits=3)
        self.assertEqual(A.__str__(), '1.23e+04 [m]')

        A = variable(123456789 * 10**(-6), 'm', nDigits=3)
        self.assertEqual(A.__str__(), '123 [m]')

        A = variable(123456789 * 10**(-7), 'm', nDigits=3)
        self.assertEqual(A.__str__(), '12.3 [m]')

        A = variable(123456789 * 10**(-8), 'm', nDigits=3)
        self.assertEqual(A.__str__(), '1.23 [m]')

        A = variable(123456789 * 10**(-9), 'm', nDigits=2)
        self.assertEqual(A.__str__(), '0.12 [m]')

        A = variable(123456789 * 10**(-10), 'm', nDigits=3)
        self.assertEqual(A.__str__(), '0.0123 [m]')

        A = variable(123456789 * 10**(-12), 'm', nDigits=3)
        self.assertEqual(A.__str__(), '0.000123 [m]')

        A = variable(123456789 * 10**(-14), 'm', nDigits=5)
        self.assertEqual(A.__str__(), '1.2346e-06 [m]')

        A = variable(123456789 * 10**(-16), 'm', nDigits=3)
        self.assertEqual(A.__str__(), '1.23e-08 [m]')

    def testRoot(self):
        A = variable(10, 'L2/min2')
        a = np.sqrt(A)
        self.assertEqual(a.value, np.sqrt(10))
        self.assertEqual(a.unit, 'L/min')

        a = A**(1 / 2)
        self.assertEqual(a.value, 10**(1 / 2))
        self.assertEqual(a.unit, 'L/min')

        for i in range(1, 1000):
            u = f'L{i+1}/min{i+1}'
            A = variable(10, u)
            power = 1 / (i + 1)
            a = A**power
            self.assertEqual(a.value, 10**(1 / (i + 1)))
            self.assertEqual(a.unit, 'L/min')

            scale = uniform(0.5, 0.99)
            with self.assertRaises(Exception) as context:
                A ** (power * scale)
            self.assertTrue(f'You can not raise a variable with the unit {u} to the power of {power * scale}' in str(context.exception))

            scale = uniform(1.01, 1.5)
            with self.assertRaises(Exception) as context:
                A ** (power * scale)
            self.assertTrue(f'You can not raise a variable with the unit {u} to the power of {power * scale}' in str(context.exception))

        A = variable(10, 'L2/m')
        with self.assertRaises(Exception) as context:
            np.sqrt(A)
        self.assertTrue('You can not raise a variable with the unit L2/m to the power of 0.5' in str(context.exception))

    def testLargerUncertThenValue(self):

        A = variable(0.003, 'L/min', 0.2)
        self.assertEqual(A.__str__(), '0.0 +/- 0.2 [L/min]')

        A = variable(1, 'L/min', 10)
        self.assertEqual(A.__str__(), '0 +/- 10 [L/min]')

        A = variable(1, 'L/min', 2.3)
        self.assertEqual(A.__str__(), '1 +/- 2 [L/min]')

        A = variable(105, 'L/min', 135.653)
        self.assertEqual(A.__str__(), '100 +/- 100 [L/min]')

        A = variable(10.5, 'L/min', 135.653)
        self.assertEqual(A.__str__(), '0 +/- 100 [L/min]')

        A = variable(0.0543, 'L/min', 0.07)
        self.assertEqual(A.__str__(), '0.05 +/- 0.07 [L/min]')

        A = variable(0.0543, 'L/min', 0.7)
        self.assertEqual(A.__str__(), '0.0 +/- 0.7 [L/min]')

    def testUnitless(self):
        with self.assertRaises(Exception) as context:
            A = variable(10, 'P', 1)
        self.assertTrue('The unit (P) was not found. Therefore it was interpreted as a prefix and a unit. However the prefix (P) was not found' in str(context.exception))

        A = variable(10, '1', 1)
        self.assertEqual(A.value, 10)
        self.assertEqual(A.unit, '1')
        self.assertEqual(A.uncert, 1)

        A = variable(10, '', 1)
        self.assertEqual(A.value, 10)
        self.assertEqual(A.unit, '1')
        self.assertEqual(A.uncert, 1)

    def testPrettyPrint(self):
        a = variable(12.3, 'm')
        b = variable(12.3, 'm', 2.5)
        c = variable([12.3, 56.2], 'm')
        d = variable([12.3, 56.2], 'm', [2.5, 7.3])

        self.assertEqual(a.__str__(pretty=False), '12.3 [m]')
        self.assertEqual(b.__str__(pretty=False), '12 +/- 2 [m]')
        self.assertEqual(c.__str__(pretty=False), '[12.3, 56.2] [m]')
        self.assertEqual(d.__str__(pretty=False), '[12, 56] +/- [2, 7] [m]')

        self.assertEqual(a.__str__(pretty=True), '12.3\\ \\left [m\\right ]')
        self.assertEqual(b.__str__(pretty=True), '12 \pm 2\\ \\left [m\\right ]')
        self.assertEqual(c.__str__(pretty=True), '[12.3, 56.2]\\ \\left [m\\right ]')
        self.assertEqual(d.__str__(pretty=True), '[12, 56] \pm [2, 7]\\ \\left [m\\right ]')


if __name__ == '__main__':
    unittest.main()

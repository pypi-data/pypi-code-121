from decimal import Decimal
from fractions import Fraction
from math import isclose

import unittest

from numeric_methods.mathematics import compare, convert, widest_type


class TestCompare(unittest.TestCase):
    # Compare test equals to compare source body
    def test_no_raise(self):
        for value in (Decimal(0), 0.0, Fraction(0, 1)):
            for kind in ("<", "<=", "==", ">", ">="):
                compare(value, kind, value)


class TestConvert(unittest.TestCase):
    def test_convert_from_decimal(self):
        self.assertEqual(convert(Decimal(3.1415), Decimal), Decimal(3.1415))
        self.assertTrue(isclose(convert(Decimal(3.1415), float), 3.1415, abs_tol=1e-9))
        self.assertEqual(
            convert(Decimal(3.1415), Fraction),
            Fraction(7074029114692207, 2251799813685248)
        )

    def test_convert_from_float(self):
        self.assertTrue(isclose(convert(3.1415, float), Decimal(3.1415), abs_tol=1e-9))
        self.assertTrue(isclose(convert(3.1415, float), 3.1415, abs_tol=1e-9))
        self.assertEqual(
            convert(3.1415, Fraction),
            Fraction(7074029114692207, 2251799813685248)
        )

    def test_convert_from_fraction(self):
        self.assertEqual(convert(Fraction(22, 7), Decimal), Decimal(22) / Decimal(7))
        self.assertTrue(isclose(convert(Fraction(22, 7), float), 3.142857142857142, abs_tol=1e09))
        self.assertEqual(convert(Fraction(22, 7), Fraction), Fraction(22, 7))


class TestWidestType(unittest.TestCase):
    def test_expectation(self):
        self.assertEqual(widest_type(0.0), float)
        self.assertEqual(widest_type(0.0, Decimal(0)), Decimal)
        self.assertEqual(widest_type(0.0, Fraction(0, 1)), Fraction)
        self.assertEqual(widest_type(Decimal(0), Fraction(0, 1)), Fraction)
        self.assertEqual(widest_type(0.0, Decimal(0), Fraction(0, 1)), Fraction)


if __name__ == '__main__':
    unittest.main()

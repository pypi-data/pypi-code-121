from decimal import Decimal
from fractions import Fraction
from math import isclose

import unittest

from numeric_methods.one_variable import half_method

Number = Decimal | float | Fraction

HALF_METHOD_RESULT = tuple[int, Number, Number, Number, Number] | Number


class TestHalfMethod(unittest.TestCase):
    @staticmethod
    def all_is_close(lhs: list[HALF_METHOD_RESULT], rhs: list[HALF_METHOD_RESULT], epsilon: Number):
        if len(lhs) != len(rhs):
            raise ValueError("`lhs` and `rhs` lists must have the same length!")

        for lhs_line, rhs_line in zip(lhs, rhs):
            if isinstance(lhs_line, tuple) and isinstance(rhs_line, tuple):
                if len(lhs_line) != len(rhs_line):
                    raise ValueError("The line of `lhs` list and the line of `rhs` list must have the same length!")

                for lhs_line_value, rhs_line_value in zip(lhs_line, rhs_line):
                    if not isclose(lhs_line_value, rhs_line_value, abs_tol=epsilon):
                        return False
            else:
                # This line must be executed
                return isclose(lhs_line, rhs_line, abs_tol=epsilon)

    def setUp(self):
        self.float_evaluations = [
            (1, 1.0,      2.0,     1.5,        5.5937),
            (2, 1.0,      1.5,     1.25,       1.0517),
            (3, 1.0,      1.25,    1.125,     -0.1979),
            (4, 1.125,    1.25,    1.1875,     0.3613),
            (5, 1.125,    1.1875,  1.15625,    0.0666),
            (6, 1.125,    1.15625, 1.140625,  -0.0693),
            (7, 1.140625, 1.15625, 1.1484375, -0.0022),
            1.1484375
        ]
        self.decimal_evaluations = [
            (1, Decimal('1'),        Decimal('2'),       Decimal('1.5'),       Decimal('5.5937')),
            (2, Decimal('1'),        Decimal('1.5'),     Decimal('1.25'),      Decimal('1.0517')),
            (3, Decimal('1'),        Decimal('1.25'),    Decimal('1.125'),     Decimal('-0.1979')),
            (4, Decimal('1.125'),    Decimal('1.25'),    Decimal('1.1875'),    Decimal('0.3613')),
            (5, Decimal('1.125'),    Decimal('1.1875'),  Decimal('1.15625'),   Decimal('0.0666')),
            (6, Decimal('1.125'),    Decimal('1.15625'), Decimal('1.140625'),  Decimal('-0.0693')),
            (7, Decimal('1.140625'), Decimal('1.15625'), Decimal('1.1484375'), Decimal('-0.0022')),
            Decimal('1.1484375')
        ]
        # Fractions are the most accurate way to represent a number so we need to leave full values here
        self.fraction_evaluations = [
            (1, Fraction(1, 1),   Fraction(2, 1),   Fraction(3, 2),     Fraction(179, 32)),
            (2, Fraction(1, 1),   Fraction(3, 2),   Fraction(5, 4),     Fraction(1077, 1024)),
            (3, Fraction(1, 1),   Fraction(5, 4),   Fraction(9, 8),     Fraction(-6487, 32768)),
            (4, Fraction(9, 8),   Fraction(5, 4),   Fraction(19, 16),   Fraction(378947, 1048576)),
            (5, Fraction(9, 8),   Fraction(19, 16), Fraction(37, 32),   Fraction(2235093, 33554432)),
            (6, Fraction(9, 8),   Fraction(37, 32), Fraction(73, 64),   Fraction(-74412055, 1073741824)),
            (7, Fraction(73, 64), Fraction(37, 32), Fraction(147, 128), Fraction(-77991229, 34359738368)),
            Fraction(147, 128)
        ]

    def test_float_result(self):
        self.assertTrue(self.all_is_close(
            list(half_method(lambda x: x ** 5 - 2, 1, 2, 0.001)),
            self.float_evaluations,
            0.0001
        ))

    def test_decimal_result(self):
        self.assertTrue(self.all_is_close(
            list(half_method(lambda x: x ** Decimal(5) - Decimal(2), Decimal(1), Decimal(2), Decimal(0.001))),
            self.decimal_evaluations,
            Decimal(0.0001)
        ))

    def test_fractions_result(self):
        self.assertTrue(
            list(half_method(lambda x: x ** Fraction(5) - Fraction(2), Fraction(1), Fraction(2), Fraction(0.001)))
            ==
            self.fraction_evaluations
        )

    def test_automatic_condition(self):
        self.assertRaises(ArithmeticError, lambda: tuple(half_method(lambda x: x ** 5 - 2, 0, 1, 0.001)))
        self.assertRaises(ArithmeticError, lambda: tuple(half_method(lambda x: x ** Decimal(5) - Decimal(2), Decimal(0), Decimal(1), Decimal(0.001))))
        self.assertRaises(ArithmeticError, lambda: tuple(half_method(lambda x: x ** Fraction(5) - Fraction(2), Fraction(0), Fraction(1), Fraction(0.001))))


if __name__ == '__main__':
    unittest.main()

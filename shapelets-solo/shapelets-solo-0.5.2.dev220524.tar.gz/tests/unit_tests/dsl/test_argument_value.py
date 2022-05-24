# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest

from shapelets.dsl import (
    ArgumentType,
    ArgumentTypeEnum,
    ArgumentValue,
    serialize_lambda,
    deserialize_lambda
)


def fibonacci(fib_n):
    if fib_n < 0:
        raise ValueError("not defined for negative values")
    fib0, fib1 = 0, 1
    for _ in range(1, fib_n + 1):
        fib0, fib1 = fib1, fib0 + fib1
    return fib0


class ArgumentValueTest(unittest.TestCase):
    def test_serialize_lambda(self):
        b64_fib = serialize_lambda(fibonacci)
        fib = deserialize_lambda(b64_fib)
        self.assertEqual(fib(12), fibonacci(12))

    def test_argument_value_constructor_list_of_floats(self):
        arg_val = ArgumentValue(
            ArgumentType(ArgumentTypeEnum.LIST, ArgumentTypeEnum.FLOAT),
            [3.14, 2.71]
        )
        self.assertEqual(
            repr(arg_val),
            'ARGUMENT_LIST:FLOAT -> [FLOAT -> 3.14, FLOAT -> 2.71]'
        )

    def test_argument_value_eq_hash(self):
        arg_val1 = ArgumentValue(
            ArgumentType(ArgumentTypeEnum.LIST, ArgumentTypeEnum.FLOAT),
            [3.14, 2.71]
        )
        arg_val2 = ArgumentValue(
            ArgumentType(ArgumentTypeEnum.LIST, ArgumentTypeEnum.FLOAT),
            [3.14, 2.71]
        )
        self.assertEqual(arg_val1, arg_val2)
        self.assertEqual(hash(arg_val1), hash(arg_val2))
        my_dict = {
            arg_val1: 'nope',
            arg_val2: 'yup'
        }
        self.assertTrue(arg_val1 in my_dict)
        self.assertTrue(arg_val2 in my_dict)
        self.assertTrue(len(my_dict) == 1)
        self.assertEqual(my_dict[arg_val1], 'yup')

# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
import inspect
import typing
import unittest

import numpy as np
import pandas as pd

from shapelets import init_session
from shapelets.dsl import dsl_op, InputParameter
from shapelets.model import Sequence, SequenceAxis, FunctionDescription

from tests.util.test_util import (
    load_small_sequence1,
    load_small_sequence2,
    small_data_1,
    small_data_2
)

SequenceValuesType = typing.TypeVar("SequenceValuesType", typing.List, np.ndarray, pd.DataFrame)


def register_output(sequence_values: SequenceValuesType, axis: SequenceAxis) -> Sequence:
    return Sequence(None, None, None, None, None, None, None, None)


def add_sequences(seq1: Sequence, seq2: Sequence) -> Sequence:
    s1 = seq1.values
    s2 = seq2.values
    res = s1 + s2
    output = register_output(res, seq1.axis)
    return output


def my_flow(seq_a, seq_b):
    a = dsl_op.plus_ts_ts(seq_a, seq_b)
    b = dsl_op.times_ts_ts(a, seq_b)
    c = dsl_op.plus_ts_ts(a, b)
    return c


def list_input_function(max_value: int, values: typing.List[int]) -> int:
    return len([value for value in values if value < max_value])


def list_input_function_1(values: typing.List[int], max_value: int) -> int:
    return len([value for value in values if value < max_value])


def list_input_function_2(min_value: int, values: typing.List[int], max_value: int) -> int:
    return len([value for value in values if max_value > value > min_value])


def list_input_function_3(min_value: int, max_value: int, values: typing.List[int]) -> int:
    return len([value for value in values if max_value > value > min_value])


def list_input_function_4(values: typing.List[int], min_value: int, max_value: int) -> int:
    return len([value for value in values if max_value > value > min_value])


def abs_w(value: int) -> int:
    return abs(value)


def multi_output_array_flow(max_value: int, values: typing.List[int]):
    max_value = dsl_op.abs_w(max_value)
    return max_value, dsl_op.filter_greater_than_value_list(max_value, values), max_value


def multi_output_array_flow_2(max_value: int, values: typing.List[int]):
    max_value = dsl_op.abs_w(max_value)
    return dsl_op.filter_greater_than_value_list(max_value, values), max_value


def multi_output_array_flow_3(max_value: int, values: typing.List[int]):
    max_value = dsl_op.abs_w(max_value)
    return max_value, dsl_op.filter_greater_than_value_list(max_value, values)


def add_mul_w(a: int, b: int) -> typing.Tuple[int, int]:
    return (a + b), (a * b)


def multi_output_array_custom_function(max_value: int, values: typing.List[int]) -> typing.Tuple[int, typing.List[int]]:
    max_value_abs = abs(max_value)
    filtered = [x for x in values if x < max_value_abs]
    return max_value_abs, filtered


def max_from_multiple_lists(input_lhs: typing.List[int], input_rhs: typing.List[int]) -> typing.Tuple[int, int, int]:
    input_lhs = np.array(input_lhs)
    max_index_lhs = np.argmax(input_lhs)
    input_rhs = np.array(input_rhs)
    max_index_rhs = np.argmax(input_rhs)
    if input_lhs[max_index_lhs] > input_rhs[max_index_rhs]:
        return 0, max_index_lhs, input_lhs[max_index_lhs]
    else:
        return 1, max_index_rhs, input_rhs[max_index_rhs]


def join_lists(list_lhs: typing.List[int], list_rhs: typing.List[int]) -> typing.List[int]:
    return list_lhs + list_rhs


def multiple_lists_as_output(a: int, b: int, c: int) -> typing.Tuple[typing.List[int], typing.List[int]]:
    return [a, b, c], [c, b, a]


def split_reduce_multiple_lists_test(a, b, c):
    lhs, rhs = dsl_op.multiple_lists_as_output(a, b, c)
    return dsl_op.join_lists(lhs, rhs)


def add_multiply_two_numbers(a: int, b: int) -> typing.List[int]:
    """
    This function returns a list containing the add and multiplication of the input parameters.
    """
    result = list()
    result.append(a + b)
    result.append(a * b)

    return result


def add_multiply_two_numbers2(a: int, b: int) -> typing.List[int]:
    result = list()
    result.append(a + b)
    result.append(a * b)

    return result


def random_number(a: int, b: int) -> int:
    import random
    b = random.randint(a, b)
    return b


class UserFunctionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._client = init_session("admin", "admin", "https://127.0.0.1")
        cls._seq1 = load_small_sequence1(cls._client)
        cls._seq2 = load_small_sequence2(cls._client)

    def test_register_custom_function_without_caching(self):
        client = UserFunctionsTest._client
        client.register_custom_function(random_number, persist_results=False)
        node = dsl_op.random_number(1, 50)
        res1 = client.run(node)
        res2 = client.run(node)

        self.assertNotEqual(res1, res2)

    def test_register_custom_function_with_documentation(self):
        client = UserFunctionsTest._client
        client.register_custom_function(add_multiply_two_numbers)
        client.register_custom_function(add_multiply_two_numbers2)

        description1 = inspect.getdoc(dsl_op.add_multiply_two_numbers)
        description2 = inspect.getdoc(dsl_op.add_multiply_two_numbers2)

        self.assertEqual(description1,
                         "This function returns a list containing the add and multiplication of the input "
                         "parameters.\n:param a: INT\n:param b: INT\n:return output_0: LIST:INT")
        self.assertEqual(description2,
                         "Documentation not available for this function.\n:param a: INT\n:param b: INT\n:return "
                         "output_0: LIST:INT")

    def test_register_custom_function(self):
        seq0 = UserFunctionsTest._seq1
        seq1 = UserFunctionsTest._seq2
        client = UserFunctionsTest._client
        client.register_custom_function(add_sequences)
        res = dsl_op.add_sequences(seq0, seq1)
        seq_res = client.run(res)
        res_np = client.get_sequence_data(seq_res).values
        expected = np.array(small_data_1) + np.array(small_data_2)
        np.testing.assert_almost_equal(res_np, expected, 5)

    def test_flow_and_function(self):
        seq0 = UserFunctionsTest._seq1
        seq1 = UserFunctionsTest._seq2
        client = UserFunctionsTest._client
        flow_to_register = my_flow(InputParameter(0, "seq_a"), InputParameter(1, "seq_b"))
        client.register_flow("my_flow", flow_to_register)
        client.register_custom_function(add_sequences)
        res = dsl_op.my_flow(seq0, seq1)
        res = dsl_op.add_sequences(res, seq1)
        res = client.run(res)
        res_np = client.get_sequence_data(res).values
        sm1 = np.array(small_data_1)
        sm2 = np.array(small_data_2)
        sm1plusSm2 = sm1 + sm2
        expected_flow = sm1plusSm2 + (sm1plusSm2 * sm2)
        expected = expected_flow + sm2
        np.testing.assert_almost_equal(res_np, expected, 4)

    def test_flow_and_function_with_description(self):
        seq0 = UserFunctionsTest._seq1
        seq1 = UserFunctionsTest._seq2
        client = UserFunctionsTest._client
        flow_to_register = my_flow(InputParameter(0, "seq_a"), InputParameter(1, "seq_b"))
        client.register_flow("my_flow", flow_to_register)
        algo_description = FunctionDescription(
            algorithm_name="add_sequences",
            documentation="My description",
            implementation_file="add_sequences_worker.py",
            function_name="add_sequences",
            cpu_activation="PYTHON")
        client.register_custom_function(add_sequences, algo_description)
        res = dsl_op.my_flow(seq0, seq1)
        res = dsl_op.add_sequences(res, seq1)
        res = client.run(res)
        res_np = client.get_sequence_data(res).values
        sm1 = np.array(small_data_1)
        sm2 = np.array(small_data_2)
        sm1plusSm2 = sm1 + sm2
        expected_flow = sm1plusSm2 + (sm1plusSm2 * sm2)
        expected = expected_flow + sm2
        np.testing.assert_almost_equal(res_np, expected, 4)

    def test_input_list_as_parameter(self):
        client = UserFunctionsTest._client
        client.register_custom_function(list_input_function)
        res = client.run(dsl_op.list_input_function(26, [1, 3, 34, 4, 56, 25]))
        self.assertEqual(res, 4)

    def test_input_list_as_parameter_1(self):
        client = UserFunctionsTest._client
        client.register_custom_function(list_input_function_1)
        res = client.run(dsl_op.list_input_function_1([1, 3, 34, 4, 56, 25], 26))
        self.assertEqual(res, 4)

    def test_input_list_as_parameter_2(self):
        client = UserFunctionsTest._client
        client.register_custom_function(list_input_function_2)
        res = client.run(dsl_op.list_input_function_2(3, [1, 3, 34, 4, 56, 25], 26))
        self.assertEqual(res, 2)

    def test_input_list_as_parameter_3(self):
        client = UserFunctionsTest._client
        client.register_custom_function(list_input_function_3)
        res = client.run(dsl_op.list_input_function_3(3, 26, [1, 3, 34, 4, 56, 25]))
        self.assertEqual(res, 2)

    def test_input_list_as_parameter_4(self):
        client = UserFunctionsTest._client
        client.register_custom_function(list_input_function_4)
        res = client.run(dsl_op.list_input_function_4([1, 3, 34, 4, 56, 25], 3, 26))
        self.assertEqual(res, 2)

    def test_input_output_list(self):
        client = UserFunctionsTest._client
        np_array = np.array([1, 3, 34, 4, 56, 25])
        nd_array = client.create_nd_array(np_array, "Luison", "Gordo")
        res = client.run(dsl_op.filter_greater_than_value(26, nd_array))
        np_array_filtered = client.get_nd_array_data(res)
        np.testing.assert_almost_equal(np.array([1.0, 3.0, 4.0, 25.0]), np_array_filtered)

    def test_input_output_list_2(self):
        client = UserFunctionsTest._client
        res = client.run(dsl_op.filter_greater_than_value_list(26, [1, 3, 34, 4, 56, 25]))
        self.assertEqual([1, 3, 4, 25], res)

    def test_multiple_output(self):
        client = UserFunctionsTest._client
        client.register_custom_function(abs_w)
        client.register_flow(
            "multi_output_array_flow_1",
            multi_output_array_flow(
                InputParameter(0, "max_value"),
                InputParameter(1, "values")),
            ["max_value", "values", "max_value"])
        res = client.run(dsl_op.multi_output_array_flow_1(-27, [1, 3, 34, 4, 56, 25]))
        self.assertEqual([27, [1, 3, 4, 25], 27], res)
        client.register_flow(
            "multi_output_array_flow_2",
            multi_output_array_flow_2(
                InputParameter(0, "max_value"),
                InputParameter(1, "values")),
            ["values", "max_value"])
        res = client.run(dsl_op.multi_output_array_flow_2(-27, [1, 3, 34, 4, 56, 25]))
        self.assertEqual([[1, 3, 4, 25], 27], res)
        client.register_flow(
            "multi_output_array_flow_3",
            multi_output_array_flow_3(
                InputParameter(0, "max_value"),
                InputParameter(1, "values")),
            ["max_value", "values"])
        res = client.run(dsl_op.multi_output_array_flow_3(-27, [1, 3, 34, 4, 56, 25]))
        self.assertEqual([27, [1, 3, 4, 25]], res)

    def test_custom_function_multiple_outputs(self):
        client = UserFunctionsTest._client
        client.register_custom_function(add_mul_w)
        res = client.run(dsl_op.add_mul_w(2, 3))
        self.assertEqual([5, 6], res)

    def test_custom_function_multiple_outputs_with_list(self):
        client = UserFunctionsTest._client
        client.register_custom_function(multi_output_array_custom_function)
        res = client.run(dsl_op.multi_output_array_custom_function(-27, [1, 3, 34, 4, 56, 25]))
        self.assertEqual([27, [1, 3, 4, 25]], res)

    def test_multiple_lists(self):
        client = UserFunctionsTest._client
        client.register_custom_function(max_from_multiple_lists)
        input1 = [1, 3, 5]
        input2 = [2, 4, 32]
        res = client.run(dsl_op.max_from_multiple_lists(input1, input2))
        self.assertEqual([1, 2, 32], res)

    def test_split_reduce_multiple_lists(self):
        client = UserFunctionsTest._client
        client.register_custom_function(join_lists)
        client.register_custom_function(multiple_lists_as_output)
        client.register_flow(
            "test_split_reduce_multiple_lists",
            split_reduce_multiple_lists_test(
                InputParameter(0, "a"),
                InputParameter(1, "b"),
                InputParameter(2, "c")))
        res = client.run(dsl_op.test_split_reduce_multiple_lists(1, 5, 9))
        self.assertEqual([1, 5, 9, 9, 5, 1], res)

    def test_get_function_parameters(self):
        client = UserFunctionsTest._client
        function = client.get_function_parameters(name="abs")
        self.assertEqual("abs", function.name)

    def test_get_all_function_parameters(self):
        client = UserFunctionsTest._client
        functions = client.get_function_parameters()
        self.assertGreater(len(functions), 90)

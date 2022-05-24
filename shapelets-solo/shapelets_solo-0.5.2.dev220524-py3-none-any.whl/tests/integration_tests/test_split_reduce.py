# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import typing
import unittest
import numpy as np

from shapelets import init_session
from shapelets.dsl import dsl_op, InputParameter
from shapelets.model import ReplicatedParam, NDArray
from tests.util.test_util import (
    load_small_sequence1,
    load_small_sequence2
)


########## test_split_reduce_list_of_ints ##########


def splitter_ints(values: typing.Sequence[int]) -> typing.Tuple[int, ReplicatedParam[int]]:
    return len(values), ReplicatedParam(values)


def reducer_ints(_: int, inputs: ReplicatedParam[int]) -> typing.List[int]:
    return inputs.values


def add_one(value: int) -> int:
    return value + 1


########## test_split_reduce_list_of_arrays ##########


def splitter_arrays(values: typing.List[NDArray]) -> typing.Tuple[int, ReplicatedParam[NDArray]]:
    return len(values), ReplicatedParam(values)


def add_one_to_array(value: NDArray) -> NDArray:
    return NDArray(value.values + 1)


def reducer_arrays(_: int, inputs: ReplicatedParam[NDArray]) -> typing.List[NDArray]:
    return inputs.values


########## test_split_reduce_two_dim_array ##########


def splitter_two_dim_array(values: NDArray) -> typing.Tuple[int, ReplicatedParam[NDArray]]:
    if len(values.values.shape) != 2:
        raise Exception("Bad shape. Two dims expected")
    num_outputs = values.values.shape[0]
    return num_outputs, ReplicatedParam([NDArray(values.values[i]) for i in range(num_outputs)])


def reducer_two_dim_array(_: int, inputs: ReplicatedParam[NDArray]) -> NDArray:
    return NDArray(np.array([nd_array.values for nd_array in inputs.values]))


########## test_split_array_into_chunks ##########


def splitter_array_chunks(chunk_size: int, values: NDArray) -> typing.Tuple[NDArray, ReplicatedParam[NDArray]]:
    if len(values.values.shape) != 1:
        raise Exception("Bad shape. One dimension expected")
    num_chunks = np.ceil(values.values.shape[0] / chunk_size).astype(int)
    chunked = [NDArray(values.values[i * chunk_size:(i + 1) * chunk_size]) for i in range(num_chunks)]
    indices = NDArray(np.array([i * chunk_size for i, _ in enumerate(chunked)]))
    return indices, ReplicatedParam(chunked)


def reducer_array_chunks(_: NDArray, chunks: ReplicatedParam[NDArray]) -> NDArray:
    joined = np.concatenate([nd_array.values for nd_array in chunks.values])
    return NDArray(joined)


########## test_split_two_arrays_into_chunks ##########


def splitter_two_arrays_into_chunks(chunk_size: int, lhs: NDArray, rhs: NDArray) -> typing.Tuple[
    NDArray, ReplicatedParam[NDArray], ReplicatedParam[NDArray]]:
    if len(lhs.values.shape) != 1 or len(rhs.values.shape) != 1:
        raise Exception("Bad shape. One dimension expected")
    if lhs.values.shape[0] != rhs.values.shape[0]:
        raise Exception("The size of the arrays doesn't match")

    num_chunks = np.ceil(lhs.values.shape[0] / chunk_size).astype(int)
    chunked_lhs = [NDArray(lhs.values[i * chunk_size:(i + 1) * chunk_size]) for i in range(num_chunks)]
    chunked_rhs = [NDArray(rhs.values[i * chunk_size:(i + 1) * chunk_size]) for i in range(num_chunks)]
    indices = NDArray(np.array([i * chunk_size for i, _ in enumerate(lhs.values)]))
    return indices, ReplicatedParam(chunked_lhs), ReplicatedParam(chunked_rhs)


def sum_two_arrays(lhs: NDArray, rhs: NDArray) -> NDArray:
    return NDArray(lhs.values + rhs.values)


########## test_split_with_lists ##########


def splitter_output_list(values: typing.List[int]) -> typing.Tuple[int, ReplicatedParam[typing.List[int]]]:
    if len(values) % 2 != 0:
        raise Exception("Bad shape. Just even number of ")

    chunks = int(len(values) / 2)

    chunked = [values[i * 2:i * 2 + 2] for i in range(chunks)]

    return chunks, ReplicatedParam(chunked)


def operation_list(values: typing.List[int]) -> typing.List[int]:
    return values + [values[-1]]


def reducer_input_list(_: int, repl: ReplicatedParam[typing.List[int]]) -> typing.List[int]:
    return [item for inner_list in repl.values for item in inner_list]


class SplitReduceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls._client = init_session("admin", "admin", "https://127.0.0.1")
        cls._client.register_custom_splitter(splitter_two_arrays_into_chunks)
        cls._client.register_custom_function(sum_two_arrays)
        cls._client.register_custom_reducer(reducer_array_chunks)
        cls._client.register_custom_splitter(splitter_array_chunks)
        cls._client.register_custom_splitter(splitter_two_dim_array)
        cls._client.register_custom_splitter(splitter_arrays)
        cls._client.register_custom_function(add_one_to_array)
        cls._client.register_custom_reducer(reducer_arrays)
        cls._client.register_custom_reducer(reducer_two_dim_array)
        cls._seq1 = load_small_sequence1(cls._client)
        cls._seq2 = load_small_sequence2(cls._client)


    def test_split_reduce_list_of_ints(self):
        SplitReduceTest._client.register_custom_splitter(splitter_ints)
        SplitReduceTest._client.register_custom_function(add_one)
        SplitReduceTest._client.register_custom_reducer(reducer_ints)
        num_outputs, chunk = dsl_op.splitter_ints([1, 2, -1, 12])
        added = dsl_op.add_one(chunk)
        res = dsl_op.reducer_ints(num_outputs, added)
        res = SplitReduceTest._client.run(res)
        self.assertEqual([2, 3, 0, 13], res)

    def test_split_reduce_list_of_arrays(self):
        client = SplitReduceTest._client
        input_values = [
            np.array([1, 2, -1, 12]),
            np.array([2]),
            np.array([-1, -2, -3]),
            np.array([])
        ]
        input_value_array = [client.create_nd_array(input_val) for input_val in input_values]
        num_outputs, chunk = dsl_op.splitter_arrays(input_value_array)
        added = dsl_op.add_one_to_array(chunk)
        res = dsl_op.reducer_arrays(num_outputs, added)
        multi_res = SplitReduceTest._client.run(res)
        multi_res_nd_array = [client.get_nd_array_data(res) for res in multi_res]
        for i, value in enumerate(input_values):
            np.testing.assert_array_equal(value + 1, multi_res_nd_array[i])

    def test_split_reduce_two_dim_array(self):
        client = SplitReduceTest._client
        input_values = np.array([
            [1, 2, -1, 12],
            [2, 4, 56, -123],
            [-1, -2, -3, 345],
            [1, 32, 31, 23]
        ])
        input_value_array = client.create_nd_array(input_values)
        num_outputs, chunk = dsl_op.splitter_two_dim_array(input_value_array)
        added = dsl_op.add_one_to_array(chunk)
        res = dsl_op.reducer_two_dim_array(num_outputs, added)
        res = SplitReduceTest._client.run(res)
        res_nd_array = client.get_nd_array_data(res)
        np.testing.assert_array_equal(input_values + 1, res_nd_array)

    def test_exception_is_forwarded(self):
        client = SplitReduceTest._client
        input_values = np.array([1, 2, -1, 12])
        input_value_array = client.create_nd_array(input_values)
        num_outputs, chunk = dsl_op.splitter_two_dim_array(input_value_array)
        added = dsl_op.add_one_to_array(chunk)
        res = dsl_op.reducer_two_dim_array(num_outputs, added)
        with self.assertRaisesRegex(Exception, "Bad shape. Two dims expected"):
            SplitReduceTest._client.run(res)

    def test_split_array_into_chunks(self):
        client = SplitReduceTest._client
        input_value = np.array([1, 2, -1, 12])
        input_value_array = client.create_nd_array(input_value)
        indices, chunk = dsl_op.splitter_array_chunks(3, input_value_array)
        added = dsl_op.add_one_to_array(chunk)
        res = dsl_op.reducer_array_chunks(indices, added)
        res = SplitReduceTest._client.run(res)
        res_nd_array = client.get_nd_array_data(res)
        np.testing.assert_array_equal(input_value + 1, res_nd_array)

    def test_nested_split_reduce(self):
        client = SplitReduceTest._client
        input_value = np.array([
            [1, 2, -1, 12],
            [2, 4, 56, -123],
            [-10, -2, -3, 345],
            [1, 32, 31, 23]
        ])
        input_value_array = client.create_nd_array(input_value)
        num_outputs, one_dim_array_in = dsl_op.splitter_two_dim_array(input_value_array)
        indices, chunk = dsl_op.splitter_array_chunks(2, one_dim_array_in)
        added = dsl_op.add_one_to_array(chunk)
        one_dim_added = dsl_op.reducer_array_chunks(indices, added)
        res = dsl_op.reducer_two_dim_array(num_outputs, one_dim_added)
        res = SplitReduceTest._client.run(res)
        res_nd_array = client.get_nd_array_data(res)
        np.testing.assert_array_equal(input_value + 1, res_nd_array)

    def test_split_two_arrays_into_chunks(self):
        client = SplitReduceTest._client
        lhs = np.array([1, 2, 3, 4, 5])
        lhs_nd_array = client.create_nd_array(lhs)
        rhs = np.array([6, 7, 8, 9, 10])
        rhs_nd_array = client.create_nd_array(rhs)
        indices, lhs_chunked, rhs_chunked = dsl_op.splitter_two_arrays_into_chunks(2, lhs_nd_array, rhs_nd_array)
        added = dsl_op.sum_two_arrays(lhs_chunked, rhs_chunked)
        res = dsl_op.reducer_array_chunks(indices, added)
        res = SplitReduceTest._client.run(res)
        res_nd_array = client.get_nd_array_data(res)
        np.testing.assert_array_equal(lhs + rhs, res_nd_array)

    def test_split_same_array_into_chunks(self):
        client = SplitReduceTest._client
        lhs = np.array([1, 2, 3, 4, 5])
        lhs_nd_array = client.create_nd_array(lhs)
        indices, lhs_chunked, rhs_chunked = dsl_op.splitter_two_arrays_into_chunks(2, lhs_nd_array, lhs_nd_array)
        added = dsl_op.sum_two_arrays(lhs_chunked, rhs_chunked)
        res = dsl_op.reducer_array_chunks(indices, added)
        res = SplitReduceTest._client.run(res)
        res_nd_array = client.get_nd_array_data(res)
        np.testing.assert_array_equal(lhs + lhs, res_nd_array)

    def test_split_reduce_with_lists(self):
        SplitReduceTest._client.register_custom_splitter(splitter_output_list)
        SplitReduceTest._client.register_custom_function(operation_list)
        SplitReduceTest._client.register_custom_reducer(reducer_input_list)

        def flow_graph(input_value):
            n, chunk = dsl_op.splitter_output_list(input_value)
            intermediate_res = dsl_op.operation_list(chunk)
            return dsl_op.reducer_input_list(n, intermediate_res)

        SplitReduceTest._client.register_flow("split_reduce_op", flow_graph(InputParameter(0, "input")))
        data = [1, 2, 3, 4, 5, 6, 7, 8]
        res = SplitReduceTest._client.run(dsl_op.split_reduce_op(data))
        self.assertEqual([1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 8, 8], res)

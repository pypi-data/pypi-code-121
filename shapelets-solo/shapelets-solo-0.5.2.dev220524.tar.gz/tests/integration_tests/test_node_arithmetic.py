# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest
import pandas as pd

from shapelets import init_session
from shapelets.dsl import (
    dsl_op,
    Node,
    ConnectorNotFound,
    NodeOperationNotSupported
)


class NodeArithmeticTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls._client = init_session("admin", "admin", "https://127.0.0.1")
        cls._data = [0, 1, 1, 2, 3, 5, 8, 13, 21]
        data_len = len(cls._data)
        every_second = pd.tseries.offsets.DateOffset(microseconds=1e6)
        cls._index = pd.date_range("2021-04-14 10:00", periods=data_len, freq=every_second)
        cls._seq = cls._client.create_sequence(
            pd.DataFrame(cls._data, index=cls._index),
            "fibonacci_seq")

    def test_node_active_output_connector_type(self):
        node = Node("A node")
        with self.assertRaises(ConnectorNotFound):
            connector = node.active_out_connector()
            print(connector)

    def test_add_numeric_plus_numeric(self):
        client = NodeArithmeticTest._client
        self.assertEqual(client.run([dsl_op.abs(-2.0) + dsl_op.abs(2.0)]), 4.0)
        self.assertEqual(client.run([dsl_op.abs(-2.0) + 2.0]), 4.0)
        self.assertEqual(client.run([2.0 + dsl_op.abs(-2.0)]), 4.0)

    def test_add_sequence_plus_numeric(self):
        client = NodeArithmeticTest._client
        data = NodeArithmeticTest._data
        index = NodeArithmeticTest._index
        seq = NodeArithmeticTest._seq # sequenc
        result_seq0 = client.get_sequence_data(client.run([dsl_op.times_ts(seq, 1.0) + dsl_op.abs(2.0)]))
        result_seq1 = client.get_sequence_data(client.run([dsl_op.times_ts(seq, 1.0) + 2.0]))
        result_seq2 = client.get_sequence_data(client.run([seq + dsl_op.abs(2.0)]))
        result_seq3 = client.get_sequence_data(client.run([dsl_op.abs(2.0) + dsl_op.times_ts(seq, 1.0)]))
        result_seq4 = client.get_sequence_data(client.run([dsl_op.abs(2.0) + seq]))
        result_seq5 = client.get_sequence_data(client.run([2.0 + dsl_op.times_ts(seq, 1.0)]))
        expected_seq = pd.DataFrame([x + 2.0 for x in data], index=index).iloc[:, 0]
        pd.testing.assert_series_equal(result_seq0, expected_seq, check_names=False)
        pd.testing.assert_series_equal(result_seq1, expected_seq, check_names=False)
        pd.testing.assert_series_equal(result_seq2, expected_seq, check_names=False)
        pd.testing.assert_series_equal(result_seq3, expected_seq, check_names=False)
        pd.testing.assert_series_equal(result_seq4, expected_seq, check_names=False)
        pd.testing.assert_series_equal(result_seq5, expected_seq, check_names=False)

    def test_add_sequence_plus_sequence(self):
        client = NodeArithmeticTest._client
        data = NodeArithmeticTest._data
        index = NodeArithmeticTest._index
        seq = NodeArithmeticTest._seq
        result_seq0 = client.get_sequence_data(client.run([dsl_op.times_ts(seq, 1.0) + dsl_op.times_ts(seq, 1.0)]))
        result_seq1 = client.get_sequence_data(client.run([dsl_op.times_ts(seq, 1.0) + seq]))
        result_seq2 = client.get_sequence_data(client.run([seq + dsl_op.times_ts(seq, 1.0)]))
        expected_seq = pd.DataFrame([x * 2.0 for x in data], index=index).iloc[:, 0]
        pd.testing.assert_series_equal(result_seq0, expected_seq, check_names=False)
        pd.testing.assert_series_equal(result_seq1, expected_seq, check_names=False)
        pd.testing.assert_series_equal(result_seq2, expected_seq, check_names=False)

    def test_add_unsupported_operand_type(self):
        client = NodeArithmeticTest._client
        seq = NodeArithmeticTest._seq
        with self.assertRaises(NodeOperationNotSupported):
            client.run([dsl_op.times_ts(seq, 1.0) + dsl_op.adfuller_test(seq)])

    def test_mul_numeric_times_numeric(self):
        client = NodeArithmeticTest._client
        self.assertEqual(client.run([dsl_op.abs(-2.0) * dsl_op.abs(2.0)]), 4.0)
        self.assertEqual(client.run([dsl_op.abs(-2.0) * 2.0]), 4.0)
        self.assertEqual(client.run([2.0 * dsl_op.abs(-2.0)]), 4.0)

    def test_mul_sequence_times_numeric(self):
        client = NodeArithmeticTest._client
        data = NodeArithmeticTest._data
        index = NodeArithmeticTest._index
        seq = NodeArithmeticTest._seq
        result_seq0 = client.get_sequence_data(client.run([dsl_op.times_ts(seq, 1.0) * dsl_op.abs(2.0)]))
        result_seq1 = client.get_sequence_data(client.run([dsl_op.times_ts(seq, 1.0) * 2.0]))
        result_seq2 = client.get_sequence_data(client.run([seq * dsl_op.abs(2.0)]))
        result_seq3 = client.get_sequence_data(client.run([dsl_op.abs(2.0) * dsl_op.times_ts(seq, 1.0)]))
        result_seq4 = client.get_sequence_data(client.run([dsl_op.abs(2.0) * seq]))
        result_seq5 = client.get_sequence_data(client.run([2.0 * dsl_op.times_ts(seq, 1.0)]))
        expected_seq = pd.DataFrame([x * 2.0 for x in data], index=index).iloc[:, 0]
        pd.testing.assert_series_equal(result_seq0, expected_seq, check_names=False)
        pd.testing.assert_series_equal(result_seq1, expected_seq, check_names=False)
        pd.testing.assert_series_equal(result_seq2, expected_seq, check_names=False)
        pd.testing.assert_series_equal(result_seq3, expected_seq, check_names=False)
        pd.testing.assert_series_equal(result_seq4, expected_seq, check_names=False)
        pd.testing.assert_series_equal(result_seq5, expected_seq, check_names=False)

    def test_mul_sequence_times_sequence(self):
        client = NodeArithmeticTest._client
        data = NodeArithmeticTest._data
        index = NodeArithmeticTest._index
        seq = NodeArithmeticTest._seq
        result_seq0 = client.get_sequence_data(client.run([dsl_op.times_ts(seq, 1.0) * dsl_op.times_ts(seq, 1.0)]))
        result_seq1 = client.get_sequence_data(client.run([dsl_op.times_ts(seq, 1.0) * seq]))
        result_seq2 = client.get_sequence_data(client.run([seq * dsl_op.times_ts(seq, 1.0)]))
        expected_seq = pd.DataFrame([x ** 2.0 for x in data], index=index).iloc[:, 0]
        pd.testing.assert_series_equal(result_seq0, expected_seq, check_names=False)
        pd.testing.assert_series_equal(result_seq1, expected_seq, check_names=False)
        pd.testing.assert_series_equal(result_seq2, expected_seq, check_names=False)

    def test_mul_unsupported_operand_type(self):
        client = NodeArithmeticTest._client
        seq = NodeArithmeticTest._seq
        with self.assertRaises(NodeOperationNotSupported):
            client.run([dsl_op.times_ts(seq, 1.0) * dsl_op.adfuller_test(seq)])

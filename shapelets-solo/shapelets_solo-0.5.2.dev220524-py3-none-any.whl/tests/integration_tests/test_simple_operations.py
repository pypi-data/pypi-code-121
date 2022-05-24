# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest
import pandas as pd

from shapelets import init_session
from shapelets.dsl import dsl_op

from tests.util.test_util import (
    load_small_sequence1,
    load_small_sequence2,
    create_small_df
)


class SimpleOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._client = init_session("admin", "admin", "https://127.0.0.1")
        cls._seq1 = load_small_sequence1(cls._client)
        cls._seq2 = load_small_sequence2(cls._client)

    def test_single_addition(self):
        seq1 = SimpleOperations._seq1
        client = SimpleOperations._client
        res = dsl_op.plus_ts_ts(seq1, seq1)
        res = client.run(res)
        res = client.get_sequence_data(res)
        data = [1.1, 2.2, 8.8, 2.2, 5.5]
        expected = create_small_df(data).apply(lambda value: value + value).iloc[:, 0]
        pd.testing.assert_series_equal(expected, res, check_names=False)

    def test_single_addition_async(self):
        seq1 = SimpleOperations._seq1
        client = SimpleOperations._client
        res = dsl_op.plus_ts_ts(seq1, seq1)
        job_id = client.run_async(res)
        res = client.wait_for_result(job_id)
        res = client.get_sequence_data(res)
        data = [1.1, 2.2, 8.8, 2.2, 5.5]
        expected = create_small_df(data).apply(lambda value: value + value).iloc[:, 0]
        pd.testing.assert_series_equal(expected, res, check_names=False)

    def test_execute_task(self):
        seq1 = SimpleOperations._seq1
        seq2 = SimpleOperations._seq2
        client = SimpleOperations._client
        seq11 = dsl_op.plus_ts_ts(seq1, seq1)
        seq22 = dsl_op.plus_ts_ts(seq2, seq2)
        res = dsl_op.times_ts_ts(seq11, seq22)
        results = client.run(res)
        result_expected = create_small_df([9.24, 36.96, 380.16, 195.36, -121.0]).iloc[:, 0]
        data_res = client.get_sequence_data(results)
        pd.testing.assert_series_equal(data_res, result_expected, check_names=False)

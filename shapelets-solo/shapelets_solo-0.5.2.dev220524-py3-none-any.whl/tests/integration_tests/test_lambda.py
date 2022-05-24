# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest
import pandas as pd

from shapelets import init_session
from shapelets.dsl import dsl_op
from shapelets.model import NDArray

from tests.util.test_util import load_small_sequence1


class LambdaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._client = init_session("admin", "admin", "https://127.0.0.1")
        cls._sequence = load_small_sequence1(cls._client)
        cls._sequence_data = cls._client.get_sequence_data(cls._sequence)

    def test_map(self):
        res = dsl_op.map_ts(lambda x: x + 100, LambdaTest._sequence)
        res = LambdaTest._client.run(res)
        data = LambdaTest._client.get_sequence_data(res)
        local = LambdaTest._sequence_data.apply(lambda x: x + 100)
        pd.testing.assert_series_equal(local, data, check_names=False)

    def test_map_global(self):
        res = dsl_op.map_ts(lambda x: x + 100, LambdaTest._sequence)
        res = LambdaTest._client.run(res)
        data = LambdaTest._client.get_sequence_data(res)
        local = LambdaTest._sequence_data.apply(lambda x: x + 100)
        pd.testing.assert_series_equal(local, data, check_names=False)

    def test_filter(self):
        seq1 = LambdaTest._sequence
        res = dsl_op.filter_ts(lambda x: x > 5, seq1)
        res = LambdaTest._client.run(res)
        data = LambdaTest._client.get_sequence_data(res)
        self.assertIsInstance(data, pd.Series)
        self.assertEqual(data.size, 2)

    def test_filter_global(self):
        seq1 = LambdaTest._sequence
        threshold = 5
        res = dsl_op.filter_ts(lambda x: x > threshold, seq1)
        res = LambdaTest._client.run(res)
        data = LambdaTest._client.get_sequence_data(res)
        self.assertIsInstance(data, pd.Series)
        self.assertEqual(data.size, 2)

    def test_reduce(self):
        client = LambdaTest._client
        seq1 = LambdaTest._sequence
        res = dsl_op.reduce_ts(lambda x, y: max(x, y), seq1)
        res = LambdaTest._client.run(res)
        self.assertIsInstance(res, float)
        self.assertAlmostEqual(8.8, res, places=5)

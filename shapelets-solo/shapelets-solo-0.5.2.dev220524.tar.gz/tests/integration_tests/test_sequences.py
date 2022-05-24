# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest
import numpy as np
import pandas as pd

from shapelets import init_session


class SequenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._client = init_session("admin", "admin", "https://127.0.0.1")

    def test_create_indexed_sequence(self):
        seq_len = 10000
        data = np.random.randn(seq_len)
        freq = pd.tseries.offsets.DateOffset(microseconds=1000000)
        index = pd.date_range("2019-01-10 20:08", periods=seq_len, freq=freq)
        df = pd.DataFrame(data, index=index)
        test_series = df.iloc[:, 0]
        seq = SequenceTest._client.create_sequence(df, name="Test Sequence Indexed")
        res = SequenceTest._client.get_sequence_data(seq)
        pd.testing.assert_series_equal(test_series, res, check_names=False)

    def test_create_non_indexed_sequence(self):
        data_len = 10000
        data = np.random.randn(data_len)
        test = pd.DataFrame(data)
        s = np.datetime64("2021-03-15 10:00")
        starts = s + np.timedelta64(0, 'ms')
        seq = SequenceTest._client.create_sequence(test,
                                                   name="Test Sequence",
                                                   starts=starts,
                                                   every=1000)
        res = SequenceTest._client.get_sequence_data(seq)
        freq = pd.tseries.offsets.DateOffset(microseconds=1000000)
        index = pd.date_range("2021-03-15 10:00", periods=data_len, freq=freq)
        expected = pd.Series(data, index=index)
        pd.testing.assert_series_equal(expected, res, check_names=False)

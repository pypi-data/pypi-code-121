# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import datetime
import numpy as np
import pandas as pd
import unittest

from shapelets.services.collections_service import (
    extract_starts_and_every_from_index,
    create_axis
)


class SequencesTest(unittest.TestCase):
    def setUp(self) -> None:
        np.random.seed(101)  # so tests are repeatable
        data_len = 10
        data = np.random.randn(data_len)
        index = pd.date_range("2021-03-15 10:00", periods=len(data), freq="S")
        self.df = pd.DataFrame(data, index=index)

    def test_get_start_end_and_every_from_index(self):
        starts, every = extract_starts_and_every_from_index(self.df)
        self.assertEqual(starts, 1615802400000)
        self.assertEqual(every, 1000)

    def test_create_axis(self):
        axis = create_axis(self.df)
        self.assertEqual(axis.starts, 1615802400000)
        self.assertEqual(axis.every, 1000)

    def test_create_axis_no_index(self):
        data_len = 10
        data = np.random.randn(data_len)
        df = pd.DataFrame(data)
        every = 1000
        starts = np.datetime64("2021-03-15 10:00") + np.timedelta64(0, 'ms')
        axis = create_axis(df, starts=starts, every=every)
        self.assertEqual(axis.starts, 1615802400000)
        self.assertEqual(axis.every, 1000)

    def test_epoch_conversion(self):
        ts = 1615802400000
        freq = pd.tseries.offsets.DateOffset(microseconds=1000000)
        starts = datetime.datetime.utcfromtimestamp(ts / 1e3).strftime('%c')
        index = pd.date_range(start=starts, periods=10, freq=freq)
        self.assertEqual(index[0], pd.date_range("2021-03-15 10:00", periods=10, freq=freq)[0])

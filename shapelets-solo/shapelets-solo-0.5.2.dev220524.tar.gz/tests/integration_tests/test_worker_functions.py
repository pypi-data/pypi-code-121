# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import numpy as np
import pandas as pd
import unittest
from functools import reduce

from shapelets import init_session
from shapelets.dsl import dsl_op
from shapelets.model import Match, Sequence, View
from tests.util.test_util import load_random_series


class FunctionsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._client = init_session("admin", "admin", "https://127.0.0.1", 443)
        cls._sequences = load_random_series(cls._client)
        cls._default_data = [10.30, 10.90, 12.75, 12.95, 15.50, 15.70, 17.65, 17.95,
                             20.20, 25.00, 25.10, 25.20, 25.30, 27.05, 27.25, 27.45]
        cls._initial_date = "2019-01-10 20:08"
        cls._freq = pd.tseries.offsets.DateOffset(microseconds=1000000)
        cls._expected_index = pd.date_range(cls._initial_date, periods=len(cls._default_data), freq=cls._freq)
        cls._delta = 1e-6
        cls._sequence = cls.create_sequence()

    @classmethod
    def create_sequence(cls, data: list = None) -> Sequence:
        if data is None:
            data = cls._default_data
        np_array = np.array(data, dtype=np.dtype("double"))
        freq = pd.tseries.offsets.DateOffset(microseconds=1000000)
        index = pd.date_range(cls._initial_date, periods=len(data), freq=freq)
        dataframe = pd.DataFrame(np_array, index=index)
        sequence = FunctionsTest._client.create_sequence(dataframe, name="Test Sequence Indexed")
        return sequence

    def test_functions_uniques_ts(self):
        client = FunctionsTest._client
        data = [1.0, 2.0, 3.14, 3.14285714, 3.14, 3.14285714, 9]
        sequence = self.create_sequence(data)
        nd_array = client.run(dsl_op.uniques_ts(sequence, False))
        nd_array_data = client.get_nd_array_data(nd_array)
        np.testing.assert_array_almost_equal(nd_array_data.flatten(), np.array([1, 2, 3.14, 3.142857, 9]))

    def test_auto_correlation(self):
        data = [1., 2, 3, 4]
        sequence = self.create_sequence(data)
        nd_array = FunctionsTest._client.run(dsl_op.auto_correlation_ts(sequence, 7, "noscale"))
        nd_array_data = FunctionsTest._client.get_nd_array_data(nd_array)
        expected_data = [4.0, 11.0, 20.0, 30.0, 20.0, 11.0, 4.0]
        np.testing.assert_array_almost_equal(nd_array_data.flatten(), np.array(expected_data))

    def test_ad_fuller(self):
        sequence = [sequence for sequence in self._sequences if sequence.name == '11FI0106'][0]
        self.assertTrue(FunctionsTest._client.run(dsl_op.adfuller_test(sequence)))

    def test_ergodicity(self):
        # Creates a sequence to fail Ergodicity test
        data_1 = [2.1, 4.2, 10.8, 22.2, -5.5, 2.1, 4.2, 13.8, 2.2, -0.5, 2.1, 4.2, 11.8, 22.2, -5.5]
        sequence_1 = self.create_sequence(data_1)
        self.assertFalse(FunctionsTest._client.run(dsl_op.ergodicity_test(sequence_1)))
        # Creates a second sequence to pass Ergodicity test
        sequence_2 = self._sequence
        self.assertTrue(FunctionsTest._client.run(dsl_op.ergodicity_test(sequence_2)))

    @unittest.skip("Sometimes fails")
    def test_periodicity(self):
        sequence = [sequence for sequence in self._sequences if sequence.name == '73FC001C'][0]
        nd_array = self._client.run(dsl_op.periodicity_test(sequence))
        nd_array_data = FunctionsTest._client.get_nd_array_data(nd_array)
        np.testing.assert_array_almost_equal(nd_array_data, np.array([1]))

    def test_seasonality(self):
        sequence = self._sequences[0]
        self.assertTrue(self._client.run(dsl_op.seasonality_test(sequence)))

    def test_trend(self):
        # Creates a sequence to fail Trend test
        sequence = [sequence for sequence in self._sequences if sequence.name == '71F00AZU'][0]
        self.assertFalse(FunctionsTest._client.run(dsl_op.trend_test(sequence)))
        # Creates a second sequence to pass Trend test
        data_2 = [-0.33856, -0.88048, 2.28131, 0.83755, 2.25138, -0.62463, -0.23920, -0.98709,
                  -0.10944, 0.62291, -1.37038, -0.05842, -0.33272, 2.50684, -0.4409, -0.33558,
                  1.55625, 0.32453, -0.4629, -0.97526, 0.36586, -1.19767, -0.61186, 1.67318]
        sequence_2 = self.create_sequence(data_2)
        self.assertTrue(FunctionsTest._client.run(dsl_op.trend_test(sequence_2)))

    def test_div(self):
        self.assertEqual(self._client.run(dsl_op.div(10, 2)), 5.0)
        self.assertEqual(self._client.run(dsl_op.div(10.25, 2.5)), 4.1)
        self.assertEqual(self._client.run(dsl_op.div(10, -2)), -5.0)

    def test_fft(self):
        res = self._client.run(dsl_op.fft(self._sequence))
        data = self._client.get_sequence_data(res)
        expected_data = [316.25, -16.438804586943505, -10.017157287525379, -8.88430856135625, -11.450000000000003,
                         -7.026604142117737, -10.582842712474616, -7.250282709582505, -8.149999999999977,
                         -7.250282709582505, -10.582842712474616, -7.026604142117737, -11.450000000000003,
                         -8.88430856135625, -10.017157287525379, -16.438804586943505]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(data, expected_seq, check_names=False)

    @unittest.skip("Function Not Available")
    def test_inverse_fft(self):
        data = [316.25, -16.438804586943505, -10.017157287525379, -8.88430856135625, -11.450000000000003,
                -7.026604142117737, -10.582842712474616, -7.250282709582505, -8.149999999999977,
                -7.250282709582505, -10.582842712474616, -7.026604142117737, -11.450000000000003,
                -8.88430856135625, -10.017157287525379, -16.438804586943505]
        sequence = self.create_sequence(data)
        res = self._client.run(dsl_op.inverse_fft(sequence))
        data = self._client.get_sequence_data(res)
        expected_seq = pd.DataFrame(self._default_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(data, expected_seq, check_names=False)

    def test_max(self):
        self.assertEqual(self._client.run(dsl_op.max(10, 2)), 10.0)
        self.assertEqual(self._client.run(dsl_op.max(10.25, 2.5)), 10.25)
        self.assertEqual(self._client.run(dsl_op.max(-10, 2)), 2.0)
        self.assertEqual(self._client.run(dsl_op.max(-10, -2)), -2.0)

    def test_min(self):
        self.assertEqual(self._client.run(dsl_op.min(10, 2)), 2.0)
        self.assertEqual(self._client.run(dsl_op.min(10.25, 2.5)), 2.5)
        self.assertEqual(self._client.run(dsl_op.min(-10, 2)), -10)
        self.assertEqual(self._client.run(dsl_op.min(-10, -2)), -10)

    def test_paa(self):
        res = self._client.run(dsl_op.paa(self._sequence, 2))
        data = self._client.get_sequence_data(res)
        index = self._expected_index[0:len(data)]
        expected_seq = pd.DataFrame([1547150883500.0, 1547150891500.0, 14.2125, 25.31875], index=index).iloc[:, 0]
        pd.testing.assert_series_equal(data, expected_seq, check_names=False)

    def test_pow(self):
        self.assertEqual(self._client.run(dsl_op.pow(10, 2)), 100.0)
        self.assertEqual(self._client.run(dsl_op.pow(10.25, 2.5)), 336.36412009764433)
        self.assertEqual(self._client.run(dsl_op.pow(-10, 2)), 100)

    def test_rem(self):
        self.assertEqual(self._client.run(dsl_op.remainder(10.0, 10.0)), 0)
        self.assertEqual(self._client.run(dsl_op.remainder(10.25, 2.5)), 0.25)
        self.assertEqual(self._client.run(dsl_op.remainder(100.50, 50.0)), 0.5)

    def test_div_ts(self):
        res = self._client.run(dsl_op.div_ts(self._sequence, 2.0))
        data = self._client.get_sequence_data(res)
        expected_data = [5.15, 5.45, 6.375, 6.475, 7.75, 7.85, 8.825, 8.975,
                         10.1, 12.5, 12.55, 12.6, 12.65, 13.525, 13.625, 13.725]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(data, expected_seq, check_names=False)

    def test_div_ts_ts(self):
        sequence_1 = self._sequence
        sequence_2 = self.create_sequence([2] * 16)
        res = self._client.run(dsl_op.div_ts_ts(sequence_1, sequence_2))
        data = self._client.get_sequence_data(res)
        expected_data = [5.15, 5.45, 6.375, 6.475, 7.75, 7.85, 8.825, 8.975,
                         10.1, 12.5, 12.55, 12.6, 12.65, 13.525, 13.625, 13.725]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(data, expected_seq, check_names=False)

    def test_minus(self):
        self.assertEqual(self._client.run(dsl_op.minus(10, 2)), 8.0)
        self.assertEqual(self._client.run(dsl_op.minus(10.25, 2.5)), 7.75)
        self.assertEqual(self._client.run(dsl_op.minus(-10, 2)), -12)
        self.assertEqual(self._client.run(dsl_op.minus(-10, -2)), -8)

    def test_pow_ts(self):
        res = self._client.run(dsl_op.pow_ts(self._sequence, 2.0))
        data = self._client.get_sequence_data(res)
        expected_data = [106.09000000000002, 118.81, 162.5625, 167.70249999999996, 240.25, 246.48999999999998,
                         311.5224999999999, 322.2025, 408.03999999999996, 625.0, 630.0100000000001, 635.0399999999998,
                         640.09, 731.7025, 742.5625, 753.5024999999999]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(data, expected_seq, check_names=False)

    def test_z_norm(self):
        res = self._client.run(dsl_op.z_norm(self._sequence))
        data = self._client.get_sequence_data(res)
        expected_data = [-1.5578524364608857, -1.4591044444501593, -1.1546314690837531, -1.1217154717468445,
                         -0.7020365057012575, -0.6691205083643489, -0.3481895343294884, -0.2988155383241251,
                         0.07148943171609863, 0.8614733678019094, 0.8779313664703641, 0.8943893651388181,
                         0.9108473638072727, 1.1988623405052246, 1.2317783378421332, 1.2646943351790418]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(data, expected_seq, check_names=False)

    def test_z_norm_multiple_ts(self):
        data_1 = [10.30, -10.90, 12.75, -12.95, 15.50, -15.70, 17.65, -17.95]
        data_2 = [20.20, -25.00, 25.10, -25.20, 25.30, -27.05, 27.25, -27.45]
        data_3 = [2.20, -5, 10, 20, -25.30, -27.05, -7.25, -2.45]
        index = self._expected_index[0:len(data_1)]
        sequence_1 = self.create_sequence(data_1)
        sequence_2 = self.create_sequence(data_2)
        sequence_3 = self.create_sequence(data_3)
        res = self._client.run(dsl_op.z_norm_multiple_ts([sequence_1, sequence_2, sequence_3]))
        seq_data_1 = self._client.get_sequence_data(res[0])
        seq_data_2 = self._client.get_sequence_data(res[1])
        seq_data_3 = self._client.get_sequence_data(res[2])
        expected_data_1 = [0.722967506920711, -0.74197023709067, 0.8922645575257998, -0.8836269529030912,
                           1.0822918592253894, -1.0736542546026806, 1.2308586587359776, -1.2291311378114358]
        expected_data_2 = [0.8290824313856742, -0.9506516570029265, 1.02201820645435, -0.9585265865975664,
                           1.0298931360489898, -1.0313696853479848, 1.1066736995967281, -1.0471195445372645]
        expected_data_3 = [0.43606917552815533, -0.04281708777826507, 0.9548626274434441, 1.6199824375912502,
                           -1.3930103023783116, -1.5094062691541776, -0.19246904506152143, 0.1267884638094255]
        expected_seq_1 = pd.DataFrame(expected_data_1, index=index).iloc[:, 0]
        expected_seq_2 = pd.DataFrame(expected_data_2, index=index).iloc[:, 0]
        expected_seq_3 = pd.DataFrame(expected_data_3, index=index).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data_1, expected_seq_1, check_names=False)
        pd.testing.assert_series_equal(seq_data_2, expected_seq_2, check_names=False)
        pd.testing.assert_series_equal(seq_data_3, expected_seq_3, check_names=False)

    def test_equals(self):
        self.assertTrue(self._client.run(dsl_op.equals(10, 10)))
        self.assertTrue(self._client.run(dsl_op.equals(10.52353636345, 10.52353636345)))
        self.assertTrue(self._client.run(dsl_op.equals(-10.5, -10.5)))
        self.assertFalse(self._client.run(dsl_op.equals(10.5, 10)))
        self.assertFalse(self._client.run(dsl_op.equals(-10.5, 10.5)))

    def test_length(self):
        res = self._client.run(dsl_op.length(self._sequence))
        self.assertEqual(res, 16)

    def test_to_view(self):
        res = self._client.run(dsl_op.to_view(self._sequence.sequence_id, 12, 12))
        data = self._client.get_sequence_data(res.sequence)
        expected_data = [10.3, 10.9, 12.75, 12.95, 15.5, 15.7, 17.65, 17.95,
                         20.2, 25., 25.1, 25.2, 25.3, 27.05, 27.25, 27.45]
        np.testing.assert_array_almost_equal(data.values, np.array(expected_data))
        expected_view = View(self._sequence, 12, 24)
        self.assertEqual(res, expected_view)

    def test_range_ts(self):
        res = self._client.run(dsl_op.range_ts(23))
        seq_data = self._client.get_sequence_data(res)
        expected_data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
        np.testing.assert_array_almost_equal(seq_data.values, expected_data)

    def test_minus_ts(self):
        res = self._client.run(dsl_op.minus_ts(self._sequence, 5.0))
        seq_data = self._client.get_sequence_data(res)
        expected_data = [5.300000000000001, 5.9, 7.75, 7.949999999999999, 10.5, 10.7, 12.649999999999999,
                         12.95, 15.2, 20.0, 20.1, 20.2, 20.3, 22.05, 22.25, 22.45]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data, expected_seq, check_names=False)

    def test_minus_ts_ts(self):
        sequence_1 = self._sequence
        sequence_2 = self.create_sequence([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
        res = self._client.run(dsl_op.minus_ts_ts(sequence_1, sequence_2))
        seq_data = self._client.get_sequence_data(res)
        expected_data = [9.3, 8.9, 9.75, 8.95, 10.5, 9.7, 10.649999999999999, 9.95, 11.2,
                         15.0, 14.100000000000001, 13.2, 12.3, 13.05, 12.25, 11.45]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data, expected_seq, check_names=False)

    def test_to_match(self):
        res = self._client.run(dsl_op.to_match(self._sequence.sequence_id, 12, 12, 2.0))
        data = self._client.get_sequence_data(res.view.sequence)
        expected_data = [10.3, 10.9, 12.75, 12.95, 15.5, 15.7, 17.65, 17.95,
                         20.2, 25., 25.1, 25.2, 25.3, 27.05, 27.25, 27.45]
        np.testing.assert_array_almost_equal(data.values, np.array(expected_data))
        expected_view = View(self._sequence, 12, 24)
        self.assertEqual(res.view, expected_view)
        expected_match = Match(2.0, expected_view)
        self.assertEqual(res, expected_match)

    def test_lessThan(self):
        self.assertTrue(self._client.run(dsl_op.less_than(1, 2)))
        self.assertTrue(self._client.run(dsl_op.less_than(1.124235245, 2.3465)))
        self.assertTrue(self._client.run(dsl_op.less_than(-9.1, -2.3465)))
        self.assertFalse(self._client.run(dsl_op.less_than(2, 1)))
        self.assertFalse(self._client.run(dsl_op.less_than(9.1, -2.3465)))

    def test_mean_normalization_ts(self):
        res = self._client.run(dsl_op.mean_normalization_ts(self._sequence))
        seq_data = self._client.get_sequence_data(res)
        expected_data = [-0.5519314868804664, -0.5169460641399417, -0.40907434402332365, -0.3974125364431488,
                         -0.24872448979591838, -0.2370626822157435, -0.123360058309038, -0.10586734693877556,
                         0.02532798833819238, 0.3052113702623907, 0.31104227405247825, 0.3168731778425656,
                         0.32270408163265313, 0.42474489795918374, 0.4364067055393586, 0.4480685131195335]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data, expected_seq, check_names=False)

    def test_mean_normalization_multiple_ts(self):
        data_1 = [10.30, -10.90, 12.75, -12.95, 15.50, -15.70, 17.65, -17.95]
        data_2 = [20.20, -25.00, 25.10, -25.20, 25.30, -27.05, 27.25, -27.45]
        data_3 = [2.20, -5, 10, 20, -25.30, -27.05, -7.25, -2.45]
        index = pd.date_range(self._initial_date, periods=len(data_1), freq=self._freq)
        sequence_1 = self.create_sequence(data_1)
        sequence_2 = self.create_sequence(data_2)
        sequence_3 = self.create_sequence(data_3)
        res = self._client.run(dsl_op.mean_normalization_multiple_ts([sequence_1, sequence_2, sequence_3]))
        seq_data_1 = self._client.get_sequence_data(res[0])
        seq_data_2 = self._client.get_sequence_data(res[1])
        seq_data_3 = self._client.get_sequence_data(res[2])
        expected_data_1 = [0.2938904494382023, -0.3016151685393259, 0.3627106741573034, -0.35919943820224726,
                           0.4399578651685394, -0.4364466292134832, 0.5003511235955057, -0.4996488764044945]
        expected_data_2 = [0.38494058500914075, -0.4413848263254113, 0.4745201096892139, -0.44504113345521024,
                           0.4781764168190128, -0.4788619744058501, 0.5138254113345521, -0.4861745886654479]
        expected_data_3 = [0.13934643995749202, -0.01368225292242297, 0.3051275239107333, 0.5176673751328374,
                           -0.44513815090329445, -0.48233262486716266, -0.0615037194473964, 0.04051540913921359]
        expected_seq_1 = pd.DataFrame(expected_data_1, index=index).iloc[:, 0]
        expected_seq_2 = pd.DataFrame(expected_data_2, index=index).iloc[:, 0]
        expected_seq_3 = pd.DataFrame(expected_data_3, index=index).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data_1, expected_seq_1, check_names=False)
        pd.testing.assert_series_equal(seq_data_2, expected_seq_2, check_names=False)
        pd.testing.assert_series_equal(seq_data_3, expected_seq_3, check_names=False)

    def test_concat_ts(self):
        sequence_1 = self.create_sequence([1, 2, 3, 4])
        sequence_2 = self.create_sequence([5, 6, 7, 8])
        res = self._client.run(dsl_op.concat_ts(sequence_1, sequence_2))
        seq_data = self._client.get_sequence_data(res)
        expected_data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
        index = pd.date_range(self._initial_date, periods=len(expected_data), freq=self._freq)
        expected_seq = pd.DataFrame(expected_data, index=index).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data, expected_seq, check_names=False)

    def test_reverse_ts(self):
        res = self._client.run(dsl_op.reverse_ts(self._sequence))
        seq_data = self._client.get_sequence_data(res)
        expected_data = [27.45, 27.25, 27.05, 25.3, 25.2, 25.1, 25.0, 20.2,
                         17.95, 17.65, 15.7, 15.5, 12.95, 12.75, 10.9, 10.3]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data, expected_seq, check_names=False)

    def test_not_equals(self):
        self.assertFalse(self._client.run(dsl_op.not_equals(2, 2)))
        self.assertFalse(self._client.run(dsl_op.not_equals(1.124235245, 1.124235245)))
        self.assertFalse(self._client.run(dsl_op.not_equals(-2.3465, -2.3465)))
        self.assertTrue(self._client.run(dsl_op.not_equals(2, 1)))
        self.assertTrue(self._client.run(dsl_op.not_equals(9.1, -2.3465)))

    def test_to_double(self):
        self.assertEqual(self._client.run(dsl_op.to_double(10.0)), 10.0)
        self.assertEqual(self._client.run(dsl_op.to_double(-10.25)), -10.25)
        self.assertEqual(self._client.run(dsl_op.to_double(1)), 1)

    def test_max_min_normalization(self):
        res = self._client.run(dsl_op.max_min_normalization(self._sequence, 10.0, 2.0))
        seq_data = self._client.get_sequence_data(res)
        expected_data = [2.0, 2.279883381924198, 3.1428571428571423, 3.236151603498542, 4.425655976676385,
                         4.518950437317784, 5.428571428571428, 5.568513119533527, 6.618075801749271, 8.857142857142858,
                         8.903790087463559, 8.950437317784257, 8.997084548104958, 9.813411078717202, 9.906705539358601,
                         10.0]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data, expected_seq, check_names=False)

    def test_max_min_normalization_multiple_ts(self):
        data_1 = [10.30, -10.90, 12.75, -12.95, 15.50, -15.70, 17.65, -17.95]
        data_2 = [20.20, -25.00, 25.10, -25.20, 25.30, -27.05, 27.25, -27.45]
        data_3 = [2.20, -5, 10, 20, -25.30, -27.05, -7.25, -2.45]
        expected_index = pd.date_range(self._initial_date, periods=len(data_1), freq=self._freq)
        sequence_1 = self.create_sequence(data_1)
        sequence_2 = self.create_sequence(data_2)
        sequence_3 = self.create_sequence(data_3)
        res = self._client.run(dsl_op.max_min_normalization_multiple_ts([sequence_1, sequence_2, sequence_3], 2.0, 1.0))
        seq_data_1 = self._client.get_sequence_data(res[0])
        seq_data_2 = self._client.get_sequence_data(res[1])
        seq_data_3 = self._client.get_sequence_data(res[2])
        expected_data_1 = [1.7935393258426968, 1.1980337078651686, 1.862359550561798, 1.1404494382022472,
                           1.939606741573034, 1.0632022471910112, 2.0, 1.0]
        expected_data_2 = [1.8711151736745886, 1.0447897623400366, 1.9606946983546618, 1.0411334552102376,
                           1.9643510054844606, 1.0073126142595978, 2.0, 1.0]
        expected_data_3 = [1.6216790648246546, 1.4686503719447397, 1.7874601487778958, 2.0, 1.0371944739638683,
                           1.0, 1.4208289054197663, 1.5228480340063761]
        expected_seq_1 = pd.DataFrame(expected_data_1, index=expected_index).iloc[:, 0]
        expected_seq_2 = pd.DataFrame(expected_data_2, index=expected_index).iloc[:, 0]
        expected_seq_3 = pd.DataFrame(expected_data_3, index=expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data_1, expected_seq_1, check_names=False)
        pd.testing.assert_series_equal(seq_data_2, expected_seq_2, check_names=False)
        pd.testing.assert_series_equal(seq_data_3, expected_seq_3, check_names=False)

    def test_visvalingam_ts(self):
        res = self._client.run(dsl_op.visvalingam_ts(self._sequence, 4))
        data = self._client.get_sequence_data(res)
        expected_data = [10.3, 15.7, 25., 27.450001]
        np.testing.assert_array_almost_equal(data.values, np.array(expected_data))

    def test_visvalingam_multiple_ts(self):
        data_2 = [20.20, -25.00, 25.10, -25.20, 25.30, -27.05, 27.25, -27.45]
        data_3 = [2.20, -5, 10, 20, -25.30, -27.05, -7.25, -2.45]
        sequence_1 = self._sequence
        sequence_2 = self.create_sequence(data_2)
        sequence_3 = self.create_sequence(data_3)
        res = self._client.run(dsl_op.visvalingam_multiple_ts([sequence_1, sequence_2, sequence_3], 4))
        seq_data_1 = self._client.get_sequence_data(res[0])
        seq_data_2 = self._client.get_sequence_data(res[1])
        seq_data_3 = self._client.get_sequence_data(res[2])
        expected_data_1 = [10.3, 15.7, 25., 27.450001]
        expected_data_2 = [20.200001, -27.049999, 27.25, -27.450001]
        expected_data_3 = [2.2, -25.299999, -27.049999, -2.45]
        np.testing.assert_array_almost_equal(seq_data_1.values, np.array(expected_data_1))
        np.testing.assert_array_almost_equal(seq_data_2.values, np.array(expected_data_2))
        np.testing.assert_array_almost_equal(seq_data_3.values, np.array(expected_data_3))

    def test_greater_than(self):
        self.assertTrue(self._client.run(dsl_op.greater_than(11, 10)))
        self.assertTrue(self._client.run(dsl_op.greater_than(10.52353636345, 10.52353636300)))
        self.assertTrue(self._client.run(dsl_op.greater_than(-2.5, -10.5)))
        self.assertFalse(self._client.run(dsl_op.greater_than(10.5, 11)))
        self.assertFalse(self._client.run(dsl_op.greater_than(-10.5, 10.5)))

    def test_split_every_n(self):
        res = self._client.run(dsl_op.split_every_n(self._sequence, 4))
        seq_data_1 = self._client.get_sequence_data(res[0])
        seq_data_2 = self._client.get_sequence_data(res[1])
        seq_data_3 = self._client.get_sequence_data(res[2])
        seq_data_4 = self._client.get_sequence_data(res[3])
        expected_data_1 = [10.3, 10.9, 12.75, 12.95]
        expected_data_2 = [15.50, 15.70, 17.65, 17.95]
        expected_data_3 = [20.20, 25.00, 25.10, 25.20]
        expected_data_4 = [25.30, 27.05, 27.25, 27.45]
        expected_seq_1 = pd.DataFrame(expected_data_1, index=self._expected_index[0:4]).iloc[:, 0]
        expected_seq_2 = pd.DataFrame(expected_data_2, index=self._expected_index[4:8]).iloc[:, 0]
        expected_seq_3 = pd.DataFrame(expected_data_3, index=self._expected_index[8:12]).iloc[:, 0]
        expected_seq_4 = pd.DataFrame(expected_data_4, index=self._expected_index[12:16]).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data_1, expected_seq_1, check_names=False)
        pd.testing.assert_series_equal(seq_data_2, expected_seq_2, check_names=False)
        pd.testing.assert_series_equal(seq_data_3, expected_seq_3, check_names=False)
        pd.testing.assert_series_equal(seq_data_4, expected_seq_4, check_names=False)

    def test_get_row_single(self):
        self.assertEqual(self._client.run(dsl_op.get_row_single(self._sequence, 6)), 17.65)
        self.assertEqual(self._client.run(dsl_op.get_row_single(self._sequence, 9)), 25)

    def test_decompose_view(self):
        view = View(self._sequence, 2, 10)
        res = self._client.run(dsl_op.decompose_view(view))
        self.assertEqual(res[0], self._sequence.sequence_id)
        self.assertEqual(res[1], 2)
        self.assertEqual(res[2], 10)

    @unittest.skip("Function Not Available")
    def test_contains_value(self):
        self.assertTrue(self._client.run(dsl_op.contains_value(self._sequence, 10.3)))
        self.assertTrue(self._client.run(dsl_op.contains_value(self._sequence, 27.45)))
        self.assertFalse(self._client.run(dsl_op.contains_value(self._sequence, 28.05)))

    @unittest.skip("Function Not Available")
    def test_contains_value_multiple_ts(self):
        sequence_1 = self.create_sequence([1, 2, 3, 4, 5])
        sequence_2 = self.create_sequence([11, 12, 13, 14, 5])
        sequence_3 = self.create_sequence([21, 12, 23, 24, 5])
        res_1 = self._client.run(dsl_op.contains_value_multiple_ts([sequence_1, sequence_2, sequence_3], 1))
        res_2 = self._client.run(dsl_op.contains_value_multiple_ts([sequence_1, sequence_2, sequence_3], 12))
        res_3 = self._client.run(dsl_op.contains_value_multiple_ts([sequence_1, sequence_2, sequence_3], 5))
        res_4 = self._client.run(dsl_op.contains_value_multiple_ts([sequence_1, sequence_2, sequence_3], 45))
        self.assertEqual([True, False, False], res_1)
        self.assertEqual([False, True, True], res_2)
        self.assertEqual([True, True, True], res_3)
        self.assertEqual([False, False, False], res_4)

    def test_to_dense_regular(self):
        # DENSE_REGULAR
        sequence_1 = self._sequence
        res_1 = self._client.run(dsl_op.to_dense_regular(sequence_1))
        res_data_1 = self._client.get_sequence_data(res_1)
        expected_data_1 = [10.3, 10.9, 12.75, 12.95, 15.5, 15.7, 17.65, 17.95,
                           20.2, 25.0, 25.1, 25.2, 25.3, 27.05, 27.25, 27.45]
        expected_seq = pd.DataFrame(expected_data_1, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(res_data_1, expected_seq, check_names=False)

    def test_less_than_or_equals(self):
        self.assertTrue(self._client.run(dsl_op.less_than_or_equals(10, 10)))
        self.assertTrue(self._client.run(dsl_op.less_than_or_equals(10.5235363600, 10.52353636345)))
        self.assertTrue(self._client.run(dsl_op.less_than_or_equals(-12.5, -10.5)))
        self.assertFalse(self._client.run(dsl_op.less_than_or_equals(11.5, 11)))
        self.assertFalse(self._client.run(dsl_op.less_than_or_equals(10.5, -10.5)))

    def test_decimal_scaling_norm(self):
        res = self._client.run(dsl_op.decimal_scaling_normalization(self._sequence))
        seq_data = self._client.get_sequence_data(res)
        expected_data = [0.10300000000000001, 0.109, 0.1275, 0.1295, 0.155, 0.157, 0.1765, 0.1795,
                         0.20199999999999999, 0.25, 0.251, 0.252, 0.253, 0.2705, 0.2725, 0.27449999999999997]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data, expected_seq, check_names=False)

    def test_isax_representation(self):
        res = self._client.run(dsl_op.isax_representation(self._sequence, 0))
        seq_data = self._client.get_sequence_data(res)
        expected_data = [19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index, dtype=int).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data, expected_seq, check_names=False)

    def test_greater_than_or_equals(self):
        self.assertTrue(self._client.run(dsl_op.greater_than_or_equals(10, 10)))
        self.assertTrue(self._client.run(dsl_op.greater_than_or_equals(10.52353636345, 10.52353636000)))
        self.assertTrue(self._client.run(dsl_op.greater_than_or_equals(-9.5, -10.5)))
        self.assertFalse(self._client.run(dsl_op.greater_than_or_equals(11.5, 21)))
        self.assertFalse(self._client.run(dsl_op.greater_than_or_equals(-10.5, 10.5)))

    @unittest.skip("Function Not Available")
    def test_matrix_profile_self_join(self):
        res = self._client.run(dsl_op.matrix_profile_self_join(self._sequence, 10))
        nd_array_data = self._client.get_nd_array_data(res)
        expected_nd_array_data = np.array([[1.217153, 1.32924, 1.217153, 1.32924, 1.353018, 1.397301, 1.560606],
                                           [2, 3, 0, 1, 2, 3, 4]])
        np.testing.assert_array_almost_equal(nd_array_data, expected_nd_array_data)

    def test_decimal_scaling_normalization_multiple_ts(self):
        data_1 = [10.30, -10.90, 12.75, -12.95, 15.50, -15.70, 17.65, -17.95]
        data_2 = [20.20, -25.00, 25.10, -25.20, 25.30, -27.05, 27.25, -27.45]
        data_3 = [2.20, -5, 10, 20, -25.30, -27.05, -7.25, -2.45]
        sequence_1 = self.create_sequence(data_1)
        sequence_2 = self.create_sequence(data_2)
        sequence_3 = self.create_sequence(data_3)
        res = self._client.run(dsl_op.decimal_scaling_normalization_multiple_ts([sequence_1, sequence_2, sequence_3]))
        seq_data_1 = self._client.get_sequence_data(res[0])
        seq_data_2 = self._client.get_sequence_data(res[1])
        seq_data_3 = self._client.get_sequence_data(res[2])
        expected_data_1 = [0.10300000000000001, -0.109, 0.1275, -0.1295, 0.155, -0.157, 0.1765, -0.1795]
        expected_data_2 = [0.20199999999999999, -0.25, 0.251, -0.252, 0.253, -0.2705, 0.2725, -0.27449999999999997]
        expected_data_3 = [0.022000000000000002, -0.05, 0.1, 0.2, -0.253, -0.2705, -0.0725, -0.0245]
        expected_seq_1 = pd.DataFrame(expected_data_1, index=self._expected_index[0:8]).iloc[:, 0]
        expected_seq_2 = pd.DataFrame(expected_data_2, index=self._expected_index[0:8]).iloc[:, 0]
        expected_seq_3 = pd.DataFrame(expected_data_3, index=self._expected_index[0:8]).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data_1, expected_seq_1, check_names=False)
        pd.testing.assert_series_equal(seq_data_2, expected_seq_2, check_names=False)
        pd.testing.assert_series_equal(seq_data_3, expected_seq_3, check_names=False)

    def test_abs(self):
        self.assertEqual(self._client.run(dsl_op.abs(2)), 2)
        self.assertEqual(self._client.run(dsl_op.abs(-2)), 2)
        self.assertEqual(self._client.run(dsl_op.abs(-2.1234)), 2.1234)

    def test_plus(self):
        self.assertEqual(self._client.run(dsl_op.plus(2, 2)), 4)
        self.assertEqual(self._client.run(dsl_op.plus(-2, 2)), 0)
        self.assertEqual(self._client.run(dsl_op.plus(2.12, 1.30)), 3.42)
        self.assertEqual(self._client.run(dsl_op.plus(-2.12, -1.30)), -3.42)

    def test_times(self):
        self.assertEqual(self._client.run(dsl_op.times(2, 2)), 4)
        self.assertEqual(self._client.run(dsl_op.times(-2, 2)), -4)
        self.assertEqual(self._client.run(dsl_op.times(2.12, 1.30)), 2.7560000000000002)
        self.assertEqual(self._client.run(dsl_op.times(-2.12, -1.30)), 2.7560000000000002)

    def test_plus_ts(self):
        res = self._client.run(dsl_op.plus_ts(self._sequence, 2))
        seq_data = self._client.get_sequence_data(res)
        expected_data = [12.3, 12.9, 14.75, 14.95, 17.5, 17.7, 19.65, 19.95,
                         22.2, 27.0, 27.1, 27.2, 27.3, 29.05, 29.25, 29.45]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data, expected_seq, check_names=False)

    def test_plus_ts_ts(self):
        sequence_1 = self._sequence
        sequence_2 = self.create_sequence([12, 12, 14, 14, 17, 17, 19, 19, 22, 27, 27, 27, 27, 29, 29, 29])
        res = self._client.run(dsl_op.plus_ts_ts(sequence_1, sequence_2))
        seq_data = self._client.get_sequence_data(res)
        expected_data = [22.3, 22.9, 26.75, 26.95, 32.5, 32.7, 36.65, 36.95,
                         42.2, 52.0, 52.1, 52.2, 52.3, 56.05, 56.25, 56.45]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data, expected_seq, check_names=False)

    def test_times_ts(self):
        res = self._client.run(dsl_op.times_ts(self._sequence, 2))
        seq_data = self._client.get_sequence_data(res)
        expected_data = [20.6, 21.8, 25.5, 25.9, 31.0, 31.4, 35.3, 35.9, 40.4, 50.0, 50.2, 50.4, 50.6, 54.1, 54.5, 54.9]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data, expected_seq, check_names=False)

    def test_times_ts_ts(self):
        sequence_1 = self._sequence
        sequence_2 = self.create_sequence([2, 2, 1, 4, 1, 7, 9, 1, 2, 7, 2, 6, 3, 5, 2, 4])
        res = self._client.run(dsl_op.times_ts_ts(sequence_1, sequence_2))
        seq_data = self._client.get_sequence_data(res)
        expected_data = [20.6, 21.8, 12.75, 51.8, 15.5, 109.89999999999999, 158.85,
                         17.95, 40.4, 175.0, 50.2, 151.2, 75.9, 135.25, 54.5, 109.8]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data, expected_seq, check_names=False)

    @unittest.skip("Function Not Available")
    def test_abs_energy(self):
        res = self._client.run(dsl_op.abs_energy(self._sequence))
        multiplied_list = [element ** 2 for element in self._default_data]
        expected_res = round(reduce(lambda x, y: x + y, multiplied_list), 4)
        self.assertEqual(res, expected_res)

    def test_abs_ts(self):
        data = [10.30, -10.90, 12.75, -12.95, 15.50, -15.70, 17.65, -17.95,
                20.20, -25.00, 25.10, -25.20, 25.30, -27.05, 27.25, -27.45]
        sequence = self.create_sequence(data)
        res = self._client.run(dsl_op.abs_ts(sequence))
        seq_data = self._client.get_sequence_data(res)
        expected_seq = pd.DataFrame(self._default_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data, expected_seq, check_names=False)

    def test_abs_multiple_ts(self):
        data_1 = [10.30, -10.90, 12.75, -12.95, 15.50, -15.70, 17.65, -17.95]
        data_2 = [20.20, -25.00, 25.10, -25.20, 25.30, -27.05, 27.25, -27.45]
        data_3 = [2.20, -5, 10, 20, -25.30, -27.05, -7.25, -2.45]
        sequence_1 = self.create_sequence(data_1)
        sequence_2 = self.create_sequence(data_2)
        sequence_3 = self.create_sequence(data_3)
        res = self._client.run(dsl_op.abs_multiple_ts([sequence_1, sequence_2, sequence_3]))
        seq_data_1 = self._client.get_sequence_data(res[0])
        seq_data_2 = self._client.get_sequence_data(res[1])
        seq_data_3 = self._client.get_sequence_data(res[2])
        expected_data_1 = [10.3, 10.9, 12.75, 12.95, 15.5, 15.7, 17.65, 17.95]
        expected_data_2 = [20.2, 25.0, 25.1, 25.2, 25.3, 27.05, 27.25, 27.45]
        expected_data_3 = [2.20, 5, 10, 20, 25.30, 27.05, 7.25, 2.45]
        expected_seq_1 = pd.DataFrame(expected_data_1, index=self._expected_index[0:8]).iloc[:, 0]
        expected_seq_2 = pd.DataFrame(expected_data_2, index=self._expected_index[0:8]).iloc[:, 0]
        expected_seq_3 = pd.DataFrame(expected_data_3, index=self._expected_index[0:8]).iloc[:, 0]
        pd.testing.assert_series_equal(seq_data_1, expected_seq_1, check_names=False)
        pd.testing.assert_series_equal(seq_data_2, expected_seq_2, check_names=False)
        pd.testing.assert_series_equal(seq_data_3, expected_seq_3, check_names=False)

    @unittest.skip("Function Not Available")
    def test_approximated_entropy(self):
        res = self._client.run(dsl_op.approximated_entropy(self._sequence, 4, 0.5))
        data = self._client.get_nd_array_data(res)
        np.testing.assert_array_almost_equal(data, np.array([0.15348456]))

    @unittest.skip("Function Not Available")
    def test_longest_strike_above_mean(self):
        sequence_1 = self.create_sequence([20, 20, 20, 1, 1, 1, 20, 20, 20, 20, 1, 1, 1, 1, 1, 1, 1, 1, 20, 20])
        sequence_2 = self.create_sequence([20, 20, 20, 1, 1, 1, 20, 20, 20, 1, 1, 1, 1, 1, 1, 1, 1, 1, 20, 20])
        res_1 = self._client.run(dsl_op.longest_strike_above_mean(sequence_1))
        res_2 = self._client.run(dsl_op.longest_strike_above_mean(sequence_2))
        self.assertEqual(res_1, 4)
        self.assertEqual(res_2, 3)

    @unittest.skip("Function Not Available")
    def test_longest_strike_below_mean(self):
        sequence_1 = self.create_sequence([20, 20, 20, 1, 1, 1, 20, 20, 20, 20, 1, 1, 1, 1, 1, 1, 1, 1, 20, 20])
        sequence_2 = self.create_sequence([20, 20, 20, 1, 1, 1, 20, 20, 20, 1, 1, 1, 1, 1, 1, 1, 1, 1, 20, 20])
        res_1 = self._client.run(dsl_op.longest_strike_below_mean(sequence_1))
        res_2 = self._client.run(dsl_op.longest_strike_below_mean(sequence_2))
        self.assertEqual(res_1, 8)
        self.assertEqual(res_2, 9)

    def test_auto_covariance_ts(self):
        sequence = self.create_sequence([2., -1, 3, -2])
        res = self._client.run(dsl_op.auto_covariance_ts(sequence, 7, "noscale"))
        data = self._client.get_nd_array_data(res)
        expected_data = [-3.75, 7.5, -12.25, 17, -12.25, 7.5, -3.75]
        np.testing.assert_array_almost_equal(data.flatten(), np.array(expected_data))

    @unittest.skip("Function Not Available")
    def test_binned_entropy(self):
        sequence = self.create_sequence([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
        res = self._client.run(dsl_op.binned_entropy(sequence, 5))
        self.assertAlmostEqual(res, 1.6094379124341005, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_c3(self):
        res = self._client.run(dsl_op.c3(self._sequence, 2))
        self.assertAlmostEqual(res, 9175.290833333333)

    @unittest.skip("Function Not Available")
    def test_cid_ce_ts(self):
        res_1 = self._client.run(dsl_op.cid_ce_ts(self._sequence, True))
        res_2 = self._client.run(dsl_op.cid_ce_ts(self._sequence, False))
        self.assertAlmostEqual(res_1, 1.1105491165940868, delta=self._delta)
        self.assertAlmostEqual(res_2, 6.7477774118594045, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_count_above_mean(self):
        res = self._client.run(dsl_op.count_above_mean(self._sequence))
        self.assertAlmostEqual(res, 8, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_count_below_mean(self):
        res = self._client.run(dsl_op.count_below_mean(self._sequence))
        self.assertAlmostEqual(res, 8, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_count_equals_ts(self):
        sequence = self.create_sequence([20, 20, 20, 18, 25, 19, 20, 20, 20, 20, 40, 30, 1, 50, 1, 1, 5, 1, 20, 20])
        res_1 = self._client.run(dsl_op.count_equals_ts(sequence, 20))
        res_2 = self._client.run(dsl_op.count_equals_ts(sequence, 1))
        self.assertEqual(res_1, 9)
        self.assertEqual(res_2, 4)

    def test_cross_correlation_ts(self):
        sequence_1 = self.create_sequence([1., 2, 3, 4])
        sequence_2 = self.create_sequence([3., 4, 5, 6])
        res = self._client.run(dsl_op.cross_correlation_ts(sequence_1, sequence_2, 3, 'coeff'))
        data_lags = self._client.get_nd_array_data(res[0])
        data_values = self._client.get_nd_array_data(res[1])
        expected_lags = [-3., -2., -1., 0, 1, 2, 3]
        expected_values = [0.11812488, 0.33468717, 0.62999938, 0.98437404, 0.74812427, 0.49218702, 0.23624977]
        np.testing.assert_array_almost_equal(data_lags.flatten(), np.array(expected_lags))
        np.testing.assert_array_almost_equal(data_values.flatten(), np.array(expected_values))

    def test_cross_covariance_ts(self):
        sequence_1 = self.create_sequence([1., 2, 3, 4])
        sequence_2 = self.create_sequence([3., 4, 5, 6])
        res = self._client.run(dsl_op.cross_covariance_ts(sequence_1, sequence_2, 3, 'coeff'))
        data_lags = self._client.get_nd_array_data(res[0])
        data_values = self._client.get_nd_array_data(res[1])
        expected_lags = [-3., -2., -1., 0, 1, 2, 3]
        expected_values = [-0.45, -0.3, 0.25, 1., 0.25, -0.3, -0.45]
        np.testing.assert_array_almost_equal(data_lags.flatten(), np.array(expected_lags))
        np.testing.assert_array_almost_equal(data_values.flatten(), np.array(expected_values))

    def test_dynamic_time_warping_distance(self):
        sequence_1 = self.create_sequence([3, 3, 3, 3, 3])
        sequence_2 = self.create_sequence([4, 4, 4, 4, 4])
        res = self._client.run(dsl_op.dynamic_time_warping_distance(sequence_1, sequence_2))
        data = self._client.get_nd_array_data(res)
        expected_data = np.array(5.0)
        np.testing.assert_array_almost_equal(data, expected_data)

    @unittest.skip("Function Not Available")
    def test_energy_ratio_by_chunks(self):
        sequence = self.create_sequence([0, 1, 2, 3, 4, 5])
        res = self._client.run(dsl_op.energy_ratio_by_chunks(sequence, 2, 0))
        self.assertAlmostEqual(res, 0.090909091, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_fft_aggregated(self):
        sequence = self.create_sequence([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        res = self._client.run(dsl_op.fft_aggregated(sequence))
        data = self._client.get_nd_array_data(res)
        self.assertAlmostEqual(data[0], 1.135143, delta=1e-4)
        self.assertAlmostEqual(data[1], 2.368324, delta=1e-4)
        self.assertAlmostEqual(data[2], 1.248777, delta=1e-4)
        self.assertAlmostEqual(data[3], 3.642666, delta=1e-4)

    @unittest.skip("Function Not Available")
    def test_fft_coefficient(self):
        sequence_1 = self.create_sequence([0, 1, 2, 3, 4, 5])
        sequence_2 = self.create_sequence([6, 7, 8, 9, 10, 11])
        res_1 = self._client.run(dsl_op.fft_coefficient(sequence_1, 0))
        res_2 = self._client.run(dsl_op.fft_coefficient(sequence_2, 0))
        data_1 = self._client.get_nd_array_data(res_1)
        data_2 = self._client.get_nd_array_data(res_2)
        self.assertEqual(data_1[0], 15)
        self.assertEqual(data_1[1], 0)
        self.assertEqual(data_1[2], 15)
        self.assertEqual(data_1[3], 0)
        self.assertEqual(data_2[0], 51)
        self.assertEqual(data_2[1], 0)
        self.assertEqual(data_2[2], 51)
        self.assertEqual(data_2[3], 0)

    def test_first_location_of_maximum(self):
        sequence_1 = self.create_sequence([5, 4, 3, 5, 0, 1, 5, 3, 2, 1])
        sequence_2 = self.create_sequence([2, 4, 3, 6, 2, 5, 4, 3, 5, 2])
        indices_1, values_1 = self._client.run(dsl_op.first_location_of_maximum(sequence_1))
        indices_2, values_2 = self._client.run(dsl_op.first_location_of_maximum(sequence_2))
        self.assertAlmostEqual(indices_1, 0.0, delta=self._delta)
        self.assertAlmostEqual(values_1, 5.0, delta=self._delta)
        self.assertAlmostEqual(indices_2, 3, delta=self._delta)
        self.assertAlmostEqual(values_2, 6, delta=self._delta)

    def test_first_location_of_minimum(self):
        sequence_1 = self.create_sequence([5, 4, 3, 0, 0, 1])
        sequence_2 = self.create_sequence([5, 4, 3, 2, 2, 1])
        indices_1, values_1 = self._client.run(dsl_op.first_location_of_minimum(sequence_1))
        indices_2, values_2 = self._client.run(dsl_op.first_location_of_minimum(sequence_2))
        self.assertAlmostEqual(indices_1, 4.0, delta=self._delta)
        self.assertAlmostEqual(values_1, 0.0, delta=self._delta)
        self.assertAlmostEqual(indices_2, 5, delta=self._delta)
        self.assertAlmostEqual(values_2, 1, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_friedrich_coefficients(self):
        res = self._client.run(dsl_op.friedrich_coefficients(self._sequence, 4, 2))
        data = self._client.get_nd_array_data(res)
        expected_data = [-1.061324e-06, -1.334746e-05, 2.073770e-04, 2.343703e-02, 9.441349e-01]
        np.testing.assert_array_almost_equal(data, np.array(expected_data))

    def test_euclidean_ts(self):
        sequence_1 = self.create_sequence([3, 3, 3, 3, 3])
        sequence_2 = self.create_sequence([4, 4, 4, 4, 4])
        res = self._client.run(dsl_op.euclidean_ts(sequence_1, sequence_2))
        data = self._client.get_nd_array_data(res)
        expected_data = np.array(2.236068)
        np.testing.assert_array_almost_equal(data, expected_data)

    def test_greater_than_ts(self):
        sequence_1 = self.create_sequence([1, 2, 3, 4])
        sequence_2 = self.create_sequence([2, 2, 2, 2])
        res = self._client.run(dsl_op.greater_than_ts(sequence_1, sequence_2))
        data = self._client.get_nd_array_data(res)
        np.testing.assert_array_equal(data.flatten(), np.array([False, False, True, True]))

    def test_hamming_distances(self):
        sequence_1 = self.create_sequence([3, 3, 3, 3, 3])
        sequence_2 = self.create_sequence([4, 4, 4, 4, 4])
        res = self._client.run(dsl_op.hamming_distances(sequence_1, sequence_2))
        data = self._client.get_nd_array_data(res)
        expected_data = np.array(5)
        np.testing.assert_array_almost_equal(data, expected_data)

    @unittest.skip("Function Not Available")
    def test_has_duplicates_ts(self):
        sequence_1 = self.create_sequence([5, 4, 3, 0, 5, 1])
        sequence_2 = self.create_sequence([5, 4, 3, 0, 2, 1])
        res_1 = self._client.run(dsl_op.has_duplicates_ts(sequence_1))
        res_2 = self._client.run(dsl_op.has_duplicates_ts(sequence_2))
        self.assertTrue(res_1)
        self.assertFalse(res_2)

    @unittest.skip("Function Not Available")
    def test_has_duplicates_max(self):
        sequence_1 = self.create_sequence([5, 4, 3, 0, 5, 1])
        sequence_2 = self.create_sequence([5, 4, 3, 0, 2, 1])
        res_1 = self._client.run(dsl_op.has_duplicates_max(sequence_1))
        res_2 = self._client.run(dsl_op.has_duplicates_max(sequence_2))
        self.assertTrue(res_1)
        self.assertFalse(res_2)

    @unittest.skip("Function Not Available")
    def test_has_duplicates_min(self):
        sequence_1 = self.create_sequence([5, 4, 3, 0, 0, 1])
        sequence_2 = self.create_sequence([5, 4, 3, 0, 2, 1])
        res_1 = self._client.run(dsl_op.has_duplicates_min(sequence_1))
        res_2 = self._client.run(dsl_op.has_duplicates_min(sequence_2))
        self.assertTrue(res_1)
        self.assertFalse(res_2)

    @unittest.skip("Function Not Available")
    def test_index_mass_quantile(self):
        sequence_1 = self.create_sequence([5, 4, 3, 0, 0, 1])
        sequence_2 = self.create_sequence([5, 4, 0, 0, 2, 1])
        res_1 = self._client.run(dsl_op.index_mass_quantile(sequence_1, 0.5))
        res_2 = self._client.run(dsl_op.index_mass_quantile(sequence_2, 0.5))
        self.assertAlmostEqual(res_1, 0.333333333, delta=self._delta)
        self.assertAlmostEqual(res_2, 0.333333333, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_k_means(self):
        sequence_1 = self.create_sequence([2.0, -2.0, 4.0, -4.0])
        sequence_2 = self.create_sequence([8.0, 5.0, 3.0, 1.0])
        sequence_3 = self.create_sequence([15.0, 10.0, 5.0, 0.0])
        sequence_4 = self.create_sequence([7.0, -7.0, 1.0, -1.0])
        res = self._client.run(
            dsl_op.k_means([sequence_1, sequence_2, sequence_3, sequence_4], k=3, tolerance=1e-10, max_iterations=100))
        centroids_data = self._client.get_nd_array_data(res[0])
        labels_data = self._client.get_nd_array_data(res[1])
        expected_centroids = np.array(
            [[0., 0., 0., 0.], [0.5, - 0.16666667, 0.83333333, - 0.5], [5.66666667, 2., 2.16666667, 0.66666667]])
        expected_labels = np.array(
            [[0., 0., 0., 0.], [0.5, - 0.16666667, 0.83333333, - 0.5], [5.66666667, 2., 2.16666667, 0.66666667]])
        for i in range(0, 4):
            self.assertAlmostEqual(centroids_data[0, i] + centroids_data[1, i] +
                                   centroids_data[2, i],
                                   expected_centroids[0, i] +
                                   expected_centroids[1, i] +
                                   expected_centroids[2, i], delta=self._delta)
        np.testing.assert_array_almost_equal(centroids_data, expected_centroids)
        np.testing.assert_array_almost_equal(labels_data, expected_labels)

    def test_k_shape(self):
        sequence = self.create_sequence([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])
        res = self._client.run(dsl_op.k_shape(sequence, k=3, max_iterations=100))
        centroids_data = self._client.get_nd_array_data(res[0])
        labels_data = self._client.get_nd_array_data(res[1])
        expected_centroids = np.array([-1.38873, 0, 0, -0.92582, 0, 0, -0.46291, 0, 0, -0.00000,
                                       0, 0, 0.46291, 0, 0, 0.92582, 0, 0, 1.38873, 0, 0])
        expected_labels = np.array(0)
        np.testing.assert_array_almost_equal(centroids_data.flatten(), expected_centroids, decimal=3)
        np.testing.assert_array_almost_equal(labels_data.flatten(), expected_labels, decimal=3)

    def test_kurtosis(self):
        sequence_1 = self.create_sequence([0, 1, 2, 3, 4, 5])
        sequence_2 = self.create_sequence([2, 2, 2, 20, 30, 25])
        res_1 = self._client.run(dsl_op.kurtosis(sequence_1))
        res_2 = self._client.run(dsl_op.kurtosis(sequence_2))
        self.assertAlmostEqual(res_1, 1.022, delta=self._delta)
        self.assertAlmostEqual(res_2, -1.083664808, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_large_standard_deviation(self):
        sequence_1 = self.create_sequence([-1, -1, -1, 1, 1, 1])
        sequence_2 = self.create_sequence([4, 6, 8, 4, 5, 4])
        res_1 = self._client.run(dsl_op.large_standard_deviation(sequence_1, 0.4))
        res_2 = self._client.run(dsl_op.large_standard_deviation(sequence_2, 0.4))
        self.assertTrue(res_1)
        self.assertFalse(res_2)

    @unittest.skip("Function Not Available")
    def test_last_location_of_maximum(self):
        sequence_1 = self.create_sequence([0, 4, 3, 5, 5, 1])
        sequence_2 = self.create_sequence([3, 2, 5, 1, 4, 5, 1, 2])
        res_1 = self._client.run(dsl_op.last_location_of_maximum(sequence_1))
        res_2 = self._client.run(dsl_op.last_location_of_maximum(sequence_2))
        self.assertAlmostEqual(res_1, 0.8333333333333334, delta=self._delta)
        self.assertAlmostEqual(res_2, 0.75, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_last_location_of_minimum(self):
        sequence_1 = self.create_sequence([0, 4, 3, 5, 5, 1, 0, 4])
        sequence_2 = self.create_sequence([3, 2, 5, 1, 4, 5, 1, 2])
        res_1 = self._client.run(dsl_op.last_location_of_minimum(sequence_1))
        res_2 = self._client.run(dsl_op.last_location_of_minimum(sequence_2))
        self.assertAlmostEqual(res_1, 0.875, delta=self._delta)
        self.assertAlmostEqual(res_2, 0.875, delta=self._delta)

    def test_less_than_ts(self):
        sequence_1 = self.create_sequence([1, 2, 3, 4])
        sequence_2 = self.create_sequence([2, 2, 2, 2])
        res = self._client.run(dsl_op.less_than_ts(sequence_1, sequence_2))
        res_data = self._client.get_nd_array_data(res)
        np.testing.assert_array_equal(res_data.flatten(), np.array([True, False, False, False]))

    @unittest.skip("Function Not Available")
    def test_local_maximals(self):
        sequence = self.create_sequence([0.0, 4.0, 3.0, 5.0, 4.0, 1.0, 0.0, 4.0])
        res = self._client.run(dsl_op.local_maximals(sequence))
        res_data = self._client.get_nd_array_data(res)
        np.testing.assert_array_equal(res_data, np.array([0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]))

    @unittest.skip("Function Not Available")
    def test_local_maximal_multiple_ts(self):
        sequence_1 = self.create_sequence([0.0, 4.0, 3.0, 5.0, 4.0, 1.0, 0.0, 4.0])
        sequence_2 = self.create_sequence([9.0, 7.0, 9.0, 1.0, 2.0, 1.0, 7.0, 9.0])
        res = self._client.run(dsl_op.local_maximal_multiple_ts([sequence_1, sequence_2]))
        res_data_1 = self._client.get_nd_array_data(res[0])
        res_data_2 = self._client.get_nd_array_data(res[1])
        np.testing.assert_array_equal(res_data_1, np.array([0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]))
        np.testing.assert_array_equal(res_data_2, np.array([1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0]))

    def test_manhattan_ts(self):
        sequence_1 = self.create_sequence([3, 3, 3, 3, 3])
        sequence_2 = self.create_sequence([4, 4, 4, 4, 4])
        res = self._client.run(dsl_op.manhattan_ts(sequence_1, sequence_2))
        data = self._client.get_nd_array_data(res)
        np.testing.assert_array_almost_equal(data, 5)

    def test_max_value_ts(self):
        sequence_1 = self.create_sequence([20, 20, 20, 18, 25, 19, 20, 20, 20, 20, 40, 30, 1, 50, 1, 1, 5, 1, 20, 20])
        sequence_2 = self.create_sequence([20, 20, 20, 2, 19, 1, 20, 20, 20, 1, 15, 1, 30, 1, 1, 18, 4, 1, 20, 20])
        res_1 = self._client.run(dsl_op.max_value_ts(sequence_1))
        res_2 = self._client.run(dsl_op.max_value_ts(sequence_2))
        self.assertEqual(res_1, 50)
        self.assertEqual(res_2, 30)

    @unittest.skip("Function Not Available")
    def test_max_langevin_fixed_point(self):
        sequence_1 = self.create_sequence([0, 1, 2, 3, 4, 5])
        sequence_2 = self.create_sequence([6, 7, 8, 9, 10, 11])
        res_1 = self._client.run(dsl_op.max_langevin_fixed_point(sequence_1, 7, 2))
        res_2 = self._client.run(dsl_op.max_langevin_fixed_point(sequence_2, 7, 2))
        self.assertAlmostEqual(res_1, 4.562972545623779, delta=self._delta)
        self.assertAlmostEqual(res_2, 12.02055549621582, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_mean_absolute_change(self):
        sequence_1 = self.create_sequence([0, 1, 2, 3, 4, 5])
        sequence_2 = self.create_sequence([8, 10, 12, 14, 16, 18])
        res_1 = self._client.run(dsl_op.mean_absolute_change(sequence_1))
        res_2 = self._client.run(dsl_op.mean_absolute_change(sequence_2))
        r = 5.0 / 6.0
        self.assertAlmostEqual(res_1, r, delta=self._delta)
        self.assertAlmostEqual(res_2, r * 2, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_mean_change(self):
        sequence_1 = self.create_sequence([0, 1, 2, 3, 4, 5])
        sequence_2 = self.create_sequence([8, 10, 12, 14, 16, 18])
        res_1 = self._client.run(dsl_op.mean_change(sequence_1))
        res_2 = self._client.run(dsl_op.mean_change(sequence_2))
        self.assertAlmostEqual(res_1, 5.0 / 6.0, delta=self._delta)
        self.assertAlmostEqual(res_2, 10.0 / 6.0, delta=self._delta)

    def test_mean_ts(self):
        sequence_1 = self.create_sequence([20, 20, 20, 18, 25, 19, 20, 20, 20, 20, 40, 30, 1, 50, 1, 1, 5, 1, 20, 20])
        sequence_2 = self.create_sequence([20, 20, 20, 2, 19, 1, 20, 20, 20, 1, 15, 1, 30, 1, 1, 18, 4, 1, 20, 20])
        res_1 = self._client.run(dsl_op.mean_ts(sequence_1))
        res_2 = self._client.run(dsl_op.mean_ts(sequence_2))
        self.assertAlmostEqual(res_1, 18.55, delta=self._delta)
        self.assertAlmostEqual(res_2, 12.7, delta=self._delta)

    def test_median_ts(self):
        sequence_1 = self.create_sequence([20, 20, 20, 18, 25, 19, 20, 20, 20, 20, 40, 30, 1, 50, 1, 1, 5, 1, 20, 20])
        sequence_2 = self.create_sequence([20, 20, 20, 2, 19, 1, 20, 20, 20, 1, 15, 1, 30, 1, 1, 18, 4, 1, 20, 20])
        res_1 = self._client.run(dsl_op.median_ts(sequence_1))
        res_2 = self._client.run(dsl_op.median_ts(sequence_2))
        self.assertAlmostEqual(res_1, 20, delta=self._delta)
        self.assertAlmostEqual(res_2, 18.5, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_mean_second_derivative_central(self):
        sequence_1 = self.create_sequence([1, 3, 7, 4, 8])
        sequence_2 = self.create_sequence([2, 5, 1, 7, 4])
        res_1 = self._client.run(dsl_op.mean_second_derivative_central(sequence_1))
        res_2 = self._client.run(dsl_op.mean_second_derivative_central(sequence_2))
        self.assertAlmostEqual(res_1, 1.0 / 5.0, delta=self._delta)
        self.assertAlmostEqual(res_2, -3.0 / 5.0, delta=self._delta)

    def test_min_value_ts(self):
        sequence_1 = self.create_sequence(
            [20, 20, 20, 18, 25, 19, 20, 20, 20, 20, 40, 30, 1, 50, 13, 15, 5, 16, 20, 20])
        sequence_2 = self.create_sequence([20, 20, 20, 2, 19, 4, 20, 20, 20, 4, 15, 6, 30, 7, 9, 18, 4, 10, 20, 20])
        res_1 = self._client.run(dsl_op.min_value_ts(sequence_1))
        res_2 = self._client.run(dsl_op.min_value_ts(sequence_2))
        self.assertEqual(res_1, 1)
        self.assertEqual(res_2, 2)

    def test_moment_ts(self):
        sequence = self.create_sequence([0, 1, 2, 3, 4, 5])
        res_1 = self._client.run(dsl_op.moment_ts(sequence, 2))
        res_2 = self._client.run(dsl_op.moment_ts(sequence, 4))
        self.assertAlmostEqual(res_1, 9.166666666, delta=self._delta)
        self.assertAlmostEqual(res_2, 163.1666666666, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_number_crossing_m(self):
        sequence = self.create_sequence([1, 2, 1, 1, -3, -4, 7, 8, 9, 10, -2, 1, -3, 5, 6, 7, -10])
        res_1 = self._client.run(dsl_op.number_crossing_m(sequence, 0))
        res_2 = self._client.run(dsl_op.number_crossing_m(sequence, 2))
        self.assertAlmostEqual(res_1, 7, delta=self._delta)
        self.assertAlmostEqual(res_2, 4, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_ratio_value_number_to_time_series_length(self):
        sequence_1 = self.create_sequence([3, 0, 0, 4, 0, 0, 13])
        sequence_2 = self.create_sequence([3, 5, 0, 4, 6, 0, 13])
        res_1 = self._client.run(dsl_op.ratio_value_number_to_time_series_length(sequence_1))
        res_2 = self._client.run(dsl_op.ratio_value_number_to_time_series_length(sequence_2))
        self.assertAlmostEqual(res_1, 4.0 / 7.0, delta=self._delta)
        self.assertAlmostEqual(res_2, 6.0 / 7.0, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_sample_stdev(self):
        sequence_1 = self.create_sequence([0, 1, 2, 3, 4, 5])
        sequence_2 = self.create_sequence([2, 2, 2, 20, 30, 25])
        res_1 = self._client.run(dsl_op.sample_stdev(sequence_1))
        res_2 = self._client.run(dsl_op.sample_stdev(sequence_2))
        self.assertAlmostEqual(res_1, 1.870828693, delta=self._delta)
        self.assertAlmostEqual(res_2, 12.988456413, delta=self._delta)

    def test_sbd_ts(self):
        sequence_1 = self.create_sequence([1, 2, 3, 4, 5])
        sequence_2 = self.create_sequence([1, 1, 0, 1, 1])
        res = self._client.run(dsl_op.sbd_ts(sequence_1, sequence_2))
        data = self._client.get_nd_array_data(res)
        expected_data = np.array(0)
        np.testing.assert_array_almost_equal(data, expected_data)

    def test_skewness_ts(self):
        sequence_1 = self.create_sequence([3, 0, 0, 4, 0, 0, 13])
        sequence_2 = self.create_sequence([2, 2, 2, 20, 30, 25])
        res_1 = self._client.run(dsl_op.skewness_ts(sequence_1))
        res_2 = self._client.run(dsl_op.skewness_ts(sequence_2))
        self.assertAlmostEqual(res_1, 2.5686835471, delta=self._delta)
        self.assertAlmostEqual(res_2, 0.3104628209, delta=self._delta)

    def test_squared_euclidean_ts(self):
        sequence_1 = self.create_sequence([4, 5, 6, 7])
        sequence_2 = self.create_sequence([8, 9, 10, 11])
        res = self._client.run(dsl_op.squared_euclidean_ts(sequence_1, sequence_2))
        data = self._client.get_nd_array_data(res)
        expected_data = np.array(0)
        np.testing.assert_array_almost_equal(data, expected_data)

    def test_standard_deviation_ts(self):
        sequence_1 = self.create_sequence([20, 20, 20, 18, 25, 19, 20, 20, 20, 20, 40, 30, 1, 50, 1, 1, 5, 1, 20, 20])
        sequence_2 = self.create_sequence([20, 20, 20, 2, 19, 1, 20, 20, 20, 1, 15, 1, 30, 1, 1, 18, 4, 1, 20, 20])
        res_1 = self._client.run(dsl_op.standard_deviation_ts(sequence_1))
        res_2 = self._client.run(dsl_op.standard_deviation_ts(sequence_2))
        self.assertAlmostEqual(res_1, 12.6843251796521, delta=self._delta)
        self.assertAlmostEqual(res_2, 9.76082395141549, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_sum_of_reoccurring_data_points_ts(self):
        sequence_1 = self.create_sequence([3, 3, 0, 4, 0, 13, 13])
        sequence_2 = self.create_sequence([1, 1, 0, 4, 0, 4, 13])
        res_1 = self._client.run(dsl_op.sum_of_reoccurring_data_points_ts(sequence_1, False))
        res_2 = self._client.run(dsl_op.sum_of_reoccurring_data_points_ts(sequence_2, True))
        self.assertEqual(res_1, 32)
        self.assertEqual(res_2, 18)

    @unittest.skip("Function Not Available")
    def test_sum_of_reoccurring_values_ts(self):
        sequence_1 = self.create_sequence([4, 4, 6, 6, 7])
        sequence_2 = self.create_sequence([4, 7, 7, 8, 8])
        res_1 = self._client.run(dsl_op.sum_of_reoccurring_values_ts(sequence_1, False))
        res_2 = self._client.run(dsl_op.sum_of_reoccurring_values_ts(sequence_2, True))
        self.assertEqual(res_1, 10)
        self.assertEqual(res_2, 15)

    def test_sum_values_ts(self):
        sequence_1 = self.create_sequence([1, 2, 3, 4.1])
        sequence_2 = self.create_sequence([-1.2, -2, -3, -4])
        res_1 = self._client.run(dsl_op.sum_values_ts(sequence_1))
        res_2 = self._client.run(dsl_op.sum_values_ts(sequence_2))
        self.assertEqual(res_1, 10.1)
        self.assertEqual(res_2, -10.2)

    @unittest.skip("Function Not Available")
    def test_symmetry_looking_ts(self):
        sequence_1 = self.create_sequence([20, 20, 20, 18, 25, 19, 20, 20, 20, 20, 40, 30, 1, 50, 1, 1, 5, 1, 20, 20])
        sequence_2 = self.create_sequence([20, 20, 20, 2, 19, 1, 20, 20, 20, 1, 15, 1, 30, 1, 1, 18, 4, 1, 20, 20])
        res_1 = self._client.run(dsl_op.symmetry_looking_ts(sequence_1, 0.1))
        res_2 = self._client.run(dsl_op.symmetry_looking_ts(sequence_2, 0.1))
        self.assertTrue(res_1)
        self.assertFalse(res_2)

    @unittest.skip("Function Not Available")
    def test_time_reversal_asymmetry_statistic_ts(self):
        sequence_1 = self.create_sequence([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
        sequence_2 = self.create_sequence([20, 20, 20, 2, 19, 1, 20, 20, 20, 1, 15, 1, 30, 1, 1, 18, 4, 1, 20, 20])
        res_1 = self._client.run(dsl_op.time_reversal_asymmetry_statistic_ts(sequence_1, 2))
        res_2 = self._client.run(dsl_op.time_reversal_asymmetry_statistic_ts(sequence_2, 2))
        self.assertEqual(res_1, 1052)
        self.assertEqual(res_2, -150.625)

    @unittest.skip("Function Not Available")
    def test_variance_larger_than_standard_deviation(self):
        sequence_1 = self.create_sequence([20, 20, 20, 18, 25, 19, 20, 20, 20, 20, 40, 30, 1, 50, 1, 1, 5, 1, 20, 20])
        sequence_2 = self.create_sequence([20, 20, 20, 2, 19, 1, 20, 20, 20, 1, 15, 1, 30, 1, 1, 18, 4, 1, 20, 20])
        res_1 = self._client.run(dsl_op.variance_larger_than_standard_deviation(sequence_1))
        res_2 = self._client.run(dsl_op.variance_larger_than_standard_deviation(sequence_2))
        self.assertTrue(res_1)
        self.assertTrue(res_2)

    def test_variance_ts(self):
        sequence_1 = self.create_sequence([1, 1, -1, -1])
        sequence_2 = self.create_sequence([1, 2, -2, -1])
        res_1 = self._client.run(dsl_op.variance_ts(sequence_1))
        res_2 = self._client.run(dsl_op.variance_ts(sequence_2))
        self.assertAlmostEqual(res_1, 1.333333, delta=self._delta)
        self.assertAlmostEqual(res_2, 3.333333, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_conjugate_ts(self):
        res = self._client.run(dsl_op.conjugate_ts(self._sequence))
        data = self._client.get_sequence_data(res)
        expected_data = [10.3, 10.9, 12.75, 12.95, 15.5, 15.7, 17.65, 17.95, 20.2, 25.0, 25.1, 25.2, 25.3, 27.05, 27.25,
                         27.45]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(data, expected_seq, check_names=False)

    @unittest.skip("Function Not Available")
    def test_cwt_coefficients(self):
        sequence = self.create_sequence([0.1, 0.2, 0.3])
        array = self._client.create_nd_array(np.array([1, 2, 3]))
        res = self._client.run(dsl_op.cwt_coefficients(sequence, array, 2, 2))
        self.assertAlmostEqual(res, 0.26517161726951599, delta=self._delta)

    def test_convolve_ts(self):
        sequence_1 = self.create_sequence(
            [0.0000, 0.1315, 0.7556, 0.4587, 0.5328, 0.2190, 0.0470, 0.6789, 0.6793, 0.9347])
        sequence_2 = self.create_sequence([0.3835, 0.5194, 0.8310, 0.0346])
        res = self._client.run(dsl_op.convolve_ts(sequence_1, sequence_2))
        data = self._client.get_sequence_data(res)
        expected_data = [0.35807370000000005, 0.67764659, 1.07503108, 0.76804628, 0.59040092,
                         0.48519383, 0.6597666099999999, 1.27707797, 1.07347142, 0.8002394799999999]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index[:10]).iloc[:, 0]
        pd.testing.assert_series_equal(data, expected_seq, check_names=False)

    def test_hann_window_ts(self):
        res = self._client.run(dsl_op.hann_window_ts(12, 1547150880000, 1000))
        data = self._client.get_sequence_data(res)
        expected_data = [0., 0.07937323, 0.29229249, 0.57115742, 0.82743037, 0.97974649,
                         0.97974649, 0.82743037, 0.57115742, 0.29229249, 0.07937323, 0.]
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index[:12]).iloc[:, 0]
        pd.testing.assert_series_equal(data, expected_seq, check_names=False)

    def test_max_inter(self):
        nd_array = np.array([[1, 0, 3, 14, 15, 6, 7, 28, 59, 10], [10, 20, 1, 4, 50, 4, 3, 8, 9, 19]])
        sh_array = self._client.create_nd_array(nd_array)
        res = self._client.run(dsl_op.max_inter(sh_array))
        data = self._client.get_nd_array_data(res)
        expected_data = np.array([10, 20, 3, 14, 50, 6, 7, 28, 59, 19])
        np.testing.assert_array_almost_equal(data.flatten(), expected_data)

    def test_min_inter(self):
        nd_array = np.array([[1, 0, 3, 14, 15, 6, 7, 28, 59, 10], [10, 20, 1, 4, 50, 4, 3, 8, 9, 19]])
        sh_array = self._client.create_nd_array(nd_array)
        res = self._client.run(dsl_op.min_inter(sh_array))
        data = self._client.get_nd_array_data(res)
        expected_data = [1, 0, 1, 4, 15, 4, 3, 8, 9, 10]
        np.testing.assert_array_almost_equal(data.flatten(), expected_data)

    @unittest.skip("Function Not Available")
    def test_mean_inter(self):
        nd_array = np.array([[1, 0, 3, 14, 15, 6, 7, 28, 59, 10], [10, 20, 1, 4, 50, 4, 3, 8, 9, 19]])
        sh_array = self._client.create_nd_array(nd_array)
        res = self._client.run(dsl_op.mean_inter(sh_array))
        data = self._client.get_nd_array_data(res)
        expected_data = [[5.5, 10, 2, 9, 32.5, 5, 5, 18, 34, 14.5]]
        np.testing.assert_array_almost_equal(data, np.array(expected_data))

    @unittest.skip("Function Not Available")
    def test_absolute_sum_of_changes(self):
        res = self._client.run(dsl_op.absolute_sum_of_changes(self._sequence))
        self.assertEqual(res, 17.15)

    def test_matrix_profile(self):
        sequence = self.create_sequence([-0.9247, 0.1808, 2.5441, 0.3516, -0.3452, 0.2191, -0.7687, 0.2413])
        res = self._client.run(dsl_op.matrix_profile(sequence, 3))
        data_profile = self._client.get_nd_array_data(res[0])
        data_index = self._client.get_nd_array_data(res[1])
        expected_profile = [0., 0., 0., 0., 0., 0.]
        expected_index = [0., 1., 2., 3., 4., 5.]
        np.testing.assert_array_almost_equal(data_profile.flatten(), expected_profile)
        np.testing.assert_array_almost_equal(data_index.flatten(), expected_index)

    def test_matrix_profile_left_right(self):
        sequence = self.create_sequence([-0.9247, 0.1808, 2.5441, 0.3516, -0.3452, 0.2191, -0.7687, 0.2413])
        res = self._client.run(dsl_op.matrix_profile_left_right(sequence, 3))
        data_left_index = self._client.get_nd_array_data(res[0])
        data_left_profile = self._client.get_nd_array_data(res[1])
        data_right_index = self._client.get_nd_array_data(res[2])
        data_right_profile = self._client.get_nd_array_data(res[3])
        expected_left_index = [0., 1., 2., 3., 4., 5.]
        expected_left_profile = [0., 0., 0., 0., 0., 0.]
        expected_right_index = [0., 1., 2., 3., 4., 5.]
        expected_right_profile = [0., 0., 0., 0., 0., 0.]
        np.testing.assert_array_almost_equal(data_left_index.flatten(), expected_left_index)
        np.testing.assert_array_almost_equal(data_left_profile.flatten(), expected_left_profile)
        np.testing.assert_array_almost_equal(data_right_index.flatten(), expected_right_index)
        np.testing.assert_array_almost_equal(data_right_profile.flatten(), expected_right_profile)

    def test_constant_ts(self):
        res = self._client.run(dsl_op.constant_ts(100, 16, 1547150880000, 1000))
        data = self._client.get_sequence_data(res)
        expected_data = [100.0] * 16
        expected_seq = pd.DataFrame(expected_data, index=self._expected_index).iloc[:, 0]
        pd.testing.assert_series_equal(data, expected_seq, check_names=False)

    @unittest.skip("Function Not Available")
    def test_pattern_in_data(self):
        sequence_1 = self.create_sequence([10, 11, 11, 12])
        sequence_2 = self.create_sequence([11, 10, 10, 11, 10, 11, 11, 10, 11, 11, 14, 10, 11, 10])
        res = self._client.run(dsl_op.pattern_in_data(sequence_1, sequence_2))
        data = self._client.get_nd_array_data(res)
        expected_data = [0.942809, 7]
        np.testing.assert_array_almost_equal(data.flatten(), expected_data)

    @unittest.skip("Function Not Available")
    def test_pattern_self_match(self):
        begin = 4
        end = 12
        res = self._client.run(dsl_op.pattern_self_match(self._sequence, begin, end))
        self.assertEqual(res[0], 4)
        self.assertEqual(res[1], 8)
        self.assertAlmostEqual(res[2], 0.999999999, delta=self._delta)

    @unittest.skip("Function Not Available")
    def test_stomp_ts(self):
        sequence_1 = self._sequence
        sequence_2 = self.create_sequence([11, 10, 10, 11, 10, 11, 11, 10, 11, 11, 14, 10, 11, 10])
        res = self._client.run(dsl_op.stomp_ts(3, sequence_1, sequence_2))
        data = self._client.get_nd_array_data(res)
        expected_data = [[11, 11, 8, 11, 8, 8, 11, 8, 11, 8, 11, 8],
                         [3.04076388, 0.0832611, 1.75876288, 1.80365666, 0.03092414, 3.01534253,
                          1.80365666, 0.03092414, 0.0832611, 2.10691298, 2.81765994, 1.75876288]]
        np.testing.assert_array_almost_equal(data, expected_data)

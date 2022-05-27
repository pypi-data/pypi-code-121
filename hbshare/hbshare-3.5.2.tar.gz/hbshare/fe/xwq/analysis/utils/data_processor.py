# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.utils.logger_utils import LoggerUtils
from statsmodels.tsa.filters.hp_filter import hpfilter
from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd


class DataProcessor(object):
    def __init__(self):
        self.freq_map = {
            'day': 'D',
            'week': 'W',
            'month': 'M',
            'season': 'Q',
            'annual': 'A'
        }

    def _sample_data(self, signal_series, frequency, method='last'):
        """
        method = 'last' 默认sample每期的最后一个点，
        method = 'first' sample每期的初始点
        method = 'mean' sample平均值。
        :param signal_series:
        :param frequency:
        :param method:
        :return:
        """
        if frequency not in self.freq_map:
            raise ValueError('frequency not in {}'.format(self.freq_map.keys()))

        if method is None:
            method = 'last'

        reindex_freq = self.freq_map[frequency]

        signal_series.index = pd.to_datetime(signal_series.index).to_period(reindex_freq)

        if method == 'last':
            signal_series = signal_series.groupby(signal_series.index).last()
        elif method == 'first':
            signal_series = signal_series.groupby(signal_series.index).first()
        elif method == 'mean':
            signal_series = signal_series.groupby(signal_series.index).mean()
        elif method == 'sum':
            signal_series = signal_series.groupby(signal_series.index).sum()
        else:
            raise ValueError("method unknown {}".format(method))

        begin_date = str(signal_series.index.min())
        end_date = str(signal_series.index.max())
        period_list = pd.period_range(begin_date, end_date, freq=reindex_freq)
        signal_series = signal_series.reindex(period_list)

        signal_series.index = signal_series.index.strftime('%Y%m%d')

        signal_series.index = pd.to_datetime(signal_series.index)
        return signal_series

    def _moving_arerage(self, signal_series, window):
        return signal_series.rolling(window).mean().dropna()

    def _time_index_month_unique(self,signal_series):
        signal_series.index = pd.to_datetime(signal_series.index).to_period('M')
        return signal_series

    def _reindex_and_interpolate(self, signal_series,frequency):

        signal_series = self._sample_data(signal_series. frequency)

        ori_index = signal_series.index

        signal_series.index = [i for i in range(len(signal_series))]

        signal_series = signal_series.interpolate(mothed='pchip')

        signal_series.index = ori_index

        return signal_series.dropna()

    def _make_trend_cycle(self, signal_series, freq=12):
        # se-idx: contain a couple of indices indicating macroeconomic state
        # remove irregularities and seasonal fluctuations
        decomp = seasonal_decompose(signal_series, model='additive', freq=freq, two_sided=False)
        trend_cycle = decomp.resid + decomp.trend
        return trend_cycle

    def _seasonal_adjest(self, signal_series, window_size):
        def _make_hycycles(se_idx, freq=12):
            # se_idx: contain a couple of indices indicating macroeconomic state
            # remove irregularities and seasonal fluctuations
            decomp = seasonal_decompose(se_idx, model='additive', freq=freq, two_sided=False)
            irreg = decomp.seasonal
            trend_cycle = se_idx - irreg
            return trend_cycle[-1]

        rolling_adj = signal_series.rolling(window=window_size).apply(_make_hycycles)
        head_tc = self._make_trend_cycle(signal_series.head(window_size))

        rolling_adj[rolling_adj.isnull()] = head_tc.reindex(rolling_adj[rolling_adj.isnull()].index)

        return rolling_adj.dropna()

    def _filter_trend(self, signal_series):
        cycle, trend = hpfilter(signal_series.dropna(), lamb=129600)
        return cycle

    def _cumsum_by_year(self, signal_series):
        year = pd.to_datetime(signal_series.index).year
        signal_series = signal_series.groupby(year).cumsum()
        return signal_series

    def _standard(self, signal_series):
        signal_series = (signal_series - signal_series.mean()) / signal_series.std()
        return signal_series

    def _min_max(self, signal_series):
        signal_series = signal_series.divide(signal_series.abs().max())
        return signal_series

    def _ttm(self, signal_series):
        return signal_series.rolling(12).mean().dropna()

    def _mom(self, signal_series, frequency):
        if frequency == 'm':
            return signal_series.pct_change(1).dropna()
        if frequency == 'd':
            return signal_series.pct_chage(20).dropna()

    def _yoy(self, signal_series):
        return signal_series.pct_change(12).dropna()

    def _ffill(self, signal_series):
        return signal_series.fillna(method='ffill').dropna()

    def _diff(self, signal_series):
        return signal_series.diff(1).dropna()

    def _binary(self, signal_series):
        signal_series[signal_series > 0] = 1
        signal_series[signal_series <= 0] = 0
        return signal_series

    def work(self, signal_series, flow):
        if isinstance(flow, dict):
            if flow['name'] == 'sample':
                signal_series = self._sample_data(signal_series, frequency=flow['frequency'], method=flow.get('method'))
            elif flow['name'] == 'unique_time':
                pass
                # signal_series = self._time_index_month_unique(signal_series)
            elif flow['name'] == 'ma':
                signal_series = self._moving_arerage(signal_series, flow['window'])
            elif flow['name'] == 'interpolate':
                signal_series = self._reindex_and_interpolate(signal_series, frequency=flow['frequency'])
            elif flow['name'] == 'seasonal_adjust':
                signal_series = self._seasonal_adjest(signal_series, window_size=flow['window_size'])
            elif flow['name'] == 'filter_trend':
                signal_series = self._filter_trend(signal_series)
            elif flow['name'] == 'standard':
                signal_series = self._standard(signal_series)
            elif flow['name'] == 'ttm':
                signal_series = self._moving_arerage(signal_series, flow['window'])
            elif flow['name'] == 'min_max':
                signal_series = self._min_max(signal_series)
            elif flow['name'] == 'mom':
                signal_series = self._mom(signal_series, frequency=flow['frequency'])
            elif flow['name'] == 'yoy':
                signal_series = self._yoy(signal_series)
            elif flow['name'] == 'diff':
                signal_series = self._diff(signal_series)
            elif flow['name'] == 'binary':
                signal_series = self._binary(signal_series)
            elif flow['name'] == 'ffill':
                signal_series = self._ffill(signal_series)
            elif flow['name'] == 'year_cumsum':
                signal_series = self._cumsum_by_year(signal_series)
            elif flow['name'] == 'miuus':
                signal_series = self._minus(signal_series, flow['other_indic_id'], flow['start_date'])
            else:
                LoggerUtils.get_logger().info('do not recognize flow {}'.format(flow['name']))
        else:
            LoggerUtils.get_logger().info('flow is not a dict')
        return signal_series

    def process(self, signal_series, work_flow):
        if work_flow is None:
            return signal_series
        for flow in work_flow:
            signal_series = self.work(signal_series, flow)
        return signal_series


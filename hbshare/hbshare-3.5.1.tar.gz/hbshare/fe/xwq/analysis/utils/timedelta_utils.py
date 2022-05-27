# -*- coding: utf-8 -*-

from datetime import date, timedelta
import datetime
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import re
import time


class TimeDateUtil(object):
    @staticmethod
    def convert_str_to_date(src_str, src_format):
        try:
            d = datetime.datetime.strptime(src_str, src_format)
        except ValueError:
            d = None
        except TypeError:
            d = None
        return d

    @staticmethod
    def covert_date_to_str(src_date, tgt_format):
        return src_date.strftime(tgt_format)

    @staticmethod
    def convert_format(src_str, src_format, tgt_format):
        src_date = TimeDateUtil.convert_str_to_date(src_str, src_format)
        if src_date is None:
            return None
        return TimeDateUtil.covert_date_to_str(src_date, tgt_format)

    @staticmethod
    def is_valid_date_format(src_str, src_format):
        return TimeDateUtil.convert_str_to_date(src_str, src_format) is not None

    @staticmethod
    def get_cur_date_str(tgt_format):
        now = datetime.datetime.now()
        return TimeDateUtil.covert_date_to_str(now, tgt_format)

    @staticmethod
    def get_last_days_date(tgt_format, n):
        last_days = date.today() - timedelta(n)
        return last_days.strftime(tgt_format)

    @staticmethod
    def get_previous_date_str(src_str, src_format, tgt_format, n):
        last_days = TimeDateUtil.convert_str_to_date(src_str, src_format) - timedelta(n)
        return last_days.strftime(tgt_format)

    @staticmethod
    def get_current_timestamp():
        return time.time()

    @staticmethod
    def get_timestamp_arr(arr, interpolation=False):
        """
        :param arr: '2016-01-01'
        :param interpolation:
        :return: 736332.0
        """
        if len(arr) == 0:
            return np.empty([0, 0])
        if not interpolation:
            return np.vectorize(lambda dt: mdates.datestr2num(dt))(arr)
        else:
            first_val = mdates.datestr2num(arr[0])
            return np.array([first_val + idx for idx, i in enumerate(arr)])

    @staticmethod
    def get_time_delta(src_str, tgt_str, src_format, tgt_format, unit='DAY'):
        last_days = TimeDateUtil.convert_str_to_date(src_str, src_format) - TimeDateUtil.convert_str_to_date(tgt_str, tgt_format)
        if unit == 'DAY':
            return last_days.days
        elif unit == 'SEC':
            return last_days.seconds
        return last_days.days

    @staticmethod
    def reset_time_format(df, src_format, tgt_format, column_name='TRADE_DATE'):
        """
        转换trade_date格式为“yyyy"
        :return:
        """
        new_time_index = list(
            map(lambda x: TimeDateUtil.convert_format(str(x), src_format, tgt_format), df[column_name].values))
        df[column_name] = pd.Series(new_time_index, index=df.index)
        return df

    @staticmethod
    def check_new_month(prev_date_str, cur_date_str):
        prev_year_month = prev_date_str[:7]
        cur_year_month = cur_date_str[:7]
        return prev_year_month, cur_year_month

    @staticmethod
    def check_regex(src_trade_date, reg):
        mat_reg = re.compile(reg)
        result = mat_reg.match(src_trade_date)
        return result

    @staticmethod
    def extract_year_month_day(date_str, date_format):
        dt = TimeDateUtil.convert_str_to_date(date_str, date_format)
        if dt is None:
            return None, None, None
        return dt.year, dt.month, dt.day

    @staticmethod
    def comp_ttm(fiscal_df,factor_name, date_format):
        """
        考虑有“财报-更正”情况的TTM
        针对利润表、现金流量表计算TTM
        注意：nan值的处理，现金流量表附表频率为半年
        针对资产负债表计算MEAN
        :return:
        """
        def compute_ttm(idxs, df, factor_name, factor_name_quarter):
            part_df = df.iloc[list(map(int, idxs))].dropna(subset=[factor_name_quarter], axis=0)
            if len(part_df.index) == 0:
                return np.nan
            elif part_df['MONTH'].iloc[-1] == 12:
                return part_df[factor_name].iloc[-1]
            elif len(part_df['MONTH'].unique().tolist()) < 4:
                return np.nan
            return np.sum(part_df.drop_duplicates(subset=['YEAR', 'MONTH'], keep='last')[factor_name_quarter])

        fiscal_df['YEAR'] = fiscal_df['END_DATE'].apply(lambda x: TimeDateUtil.convert_str_to_date(x, date_format).year)
        fiscal_df['MONTH'] = fiscal_df['END_DATE'].apply(lambda x: TimeDateUtil.convert_str_to_date(x, date_format).month)
        prev_year, prev_month, prev_val = 0, 0, 0.0
        factor_name_quarter = "{0}_{1}".format(factor_name, 'QUARTER')
        factor_name_ttm = "{0}_{1}".format(factor_name, 'TTM')
        for idx, (_, rows) in enumerate(fiscal_df.itterrows()):
            cur_year, cur_month, __ = TimeDateUtil.extract_year_month_day(rows['END_DATE'], date_format)
            next_year, next_month, __ = TimeDateUtil.extract_year_month_day(
                fiscal_df['END_DATE'].iloc[min(idx+1, len(fiscal_df.index)-1)], date_format)
            if cur_month == 3 and not np.isnan(prev_val):
                fiscal_df.loc[_, factor_name_quarter] = rows[factor_name]
            elif cur_month - prev_month == 3 and prev_year == cur_year and not np.isnan(prev_val):
                quarter_val = rows[factor_name] - prev_val
                fiscal_df.loc[_, factor_name_quarter] = quarter_val
            elif cur_month == prev_month and prev_year == cur_year and not np.isnan(prev_val):
                quarter_val = rows[factor_name] - prev_val
                fiscal_df.loc[_, factor_name_quarter] = quarter_val
            else:
                fiscal_df.loc[_, factor_name_quarter] = np.nan
            # 仅当这种情况下更新之前的数据
            if next_year != cur_year or next_month != cur_month:
                prev_year, prev_month = cur_year, cur_month
                prev_val = fiscal_df.loc[_, factor_name]
        # 滚动计算TTM
        tot = len(fiscal_df.index)
        fiscal_df['IDX'] = range(tot)
        fiscal_df[factor_name_ttm] = fiscal_df['IDX'].rolling(window=tot, min_periods=0, center=False)\
            .apply(lambda x: compute_ttm(x, fiscal_df, factor_name, factor_name_quarter))
        return fiscal_df.drop(['YEAR', 'MONTH', 'IDX', factor_name_quarter], axis=1)

    @staticmethod
    def comp_ma(fiscal_df, factor_name, date_format, window=4):
        """
        注意nan值的处理
        针对资产负债表计算MEAN
        :return:
        """
        def compute_ma(idxs, df, factor_name, window):
            part_df = df.iloc[list(map(int, idxs))]
            if len(part_df.index) == 0:
                return np.nan
            last_publish_date = part_df['PUBLISH_DATE'].iloc[-1]
            last_end_date = part_df['END_DATE'].iloc[-1]
            part_df = part_df[(part_df['END_DATE'] <= last_end_date) & (part_df['PUBLISH_DATE'] <= last_publish_date)] \
                .drop_duplicates(subset=['TICKER_SYMBOL', 'END_DATE'], keep='last') \
                .sort_values(['TICKER_SYMBOL', 'END_DATE', 'PUBLISH_DATE'], ascending=[True, True, True]) \
                .dropna(subset=[factor_name], axis=0)
            return np.mean(part_df.drop_duplicates(subset=['YEAR', 'MONTH'], keep='last').tail(window)[factor_name])

        factor_name_mean = "{0}_{1}".format(factor_name, 'MA')
        fiscal_df['YEAR'] = fiscal_df['END_DATE'].apply(lambda x: TimeDateUtil.convert_str_to_date(x, date_format).year)
        fiscal_df['MONTH'] = fiscal_df['END_DATE'].apply(lambda x: TimeDateUtil.convert_str_to_date(x, date_format).month)
        # 均值
        fiscal_df = fiscal_df.sort_values(by=['TICKER_SYMBOL', 'PUBLISH_DATE', 'END_DATE'], ascending=[True, True, True])
        tot = len(fiscal_df.index)
        fiscal_df['IDX'] = range(tot)
        fiscal_df[factor_name_mean] = fiscal_df['IDX'].rolling(window=tot, min_periods=0, center=False) \
            .apply(lambda x: compute_ma(x, fiscal_df, factor_name, window), raw=True)
        return fiscal_df.drop(['YEAR', 'MONTH', 'IDX'], axis=1)

    @staticmethod
    def comp_diff(fiscal_df, factor_name, date_format):
        """
        注意nan值的处理
        针对资产负债表计算上期变化
        :return:
        """
        def compute_diff(idxs, df, factor_name):
            part_df = df.iloc[list(map(int, idxs))].dropna(subset=[factor_name], axis=0)
            if len(part_df.index) == 0:
                return np.nan
            return part_df.drop_duplicates(subset=['YEAR', 'MONTH'], keep='last')[factor_name].diff(period=1).iloc[-1]

        factor_name_delta = "{0}_{1}".format(factor_name, 'DELTA')
        fiscal_df['YEAR'] = fiscal_df['END_DATE'].apply(lambda x: TimeDateUtil.convert_str_to_date(x, date_format).year)
        fiscal_df['MONTH'] = fiscal_df['END_DATE'].apply(lambda x: TimeDateUtil.convert_str_to_date(x, date_format).month)
        # 与上期之差
        tot = len(fiscal_df.index)
        fiscal_df['IDX'] = range(tot)
        fiscal_df[factor_name_delta] = fiscal_df['IDX'].rolling(window=tot, min_periods=0, center=False) \
            .apply(lambda x: compute_diff(x, fiscal_df, factor_name), raw=True)
        return fiscal_df.drop(['YEAR', 'MONTH', 'IDX'], axis=1)
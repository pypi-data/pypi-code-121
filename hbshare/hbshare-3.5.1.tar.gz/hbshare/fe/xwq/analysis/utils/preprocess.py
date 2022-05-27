# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.utils.const_var import TimeDateFormat
from hbshare.fe.xwq.analysis.utils.logger_utils import LoggerUtils
from hbshare.fe.xwq.analysis.utils.timedelta_utils import TimeDateUtil
import pandas as pd
import os


class Preprocess:
    @staticmethod
    def check_newest_data(factor_path, factor_names=[]):
        """
        判断各个因子的最新时间
        :param factor_path:
        :param factor_names:
        :return:
        """
        newest_date = ''
        for factor_name in factor_names:
            td = Preprocess.check_lastest_date(factor_path, factor_name.lower())
            newest_date = td if newest_date == '' or td == '' or td < newest_date else newest_date
        return newest_date

    @staticmethod
    def check_lastest_date(factor_path, factor_name):
        """
        检验给定某因子，在因子文件夹路径下的最新日期
        :param factor_path:
        :param factor_name:
        :return:
        """
        dir_path = factor_path + factor_name
        newest_date = ''
        if not os.path.isdir(dir_path):
            return newest_date
        for f_name in os.listdir(dir_path):
            items = f_name.split('.')
            if not os.path.isfile(dir_path + '/' + f_name) or factor_name not in f_name or len(items) != 3:
                continue
            date = TimeDateUtil.convert_format(items[1], TimeDateFormat.YMD.value, TimeDateFormat.YMDHYPHEN.value)
            newest_date = date if newest_date == '' or date > newest_date else newest_date
        return newest_date

    @staticmethod
    def output_factor(factor_path, factor_name, start_date, end_date, factor_df):
        """
        输出因子文件
        :return:
        """
        if factor_name not in factor_df.columns:
            LoggerUtils().get_logger().error('[Preprocess][OutputFactor] factorName:{0} not in df'.format(factor_name))
            return
        part_df = factor_df[['TRADE_DATE', 'TICKER-SYMBOL', factor_name]].copy(deep=True)
        part_df = part_df.dropna(subset=[factor_name], how='any', axis=0)
        part_df = part_df[(part_df['TRADE_DATE'] >= TimeDateUtil.convert_format(start_date, TimeDateFormat.YMDHYPHEN.value, TimeDateFormat.YMD.value)) &
                          (part_df['TRADE_DATE'] <= TimeDateUtil.convert_format(end_date, TimeDateFormat.YMDHYPHEN.value, TimeDateFormat.YMD.value))]
        g = part_df.groupby(['TRADE_DATE'])
        factor_name = factor_name.lower()
        for td, pp_df in g:
            dir_name = "{0}{1}".format(factor_path, factor_name)
            if not os.path.isdir(dir_name):
                os.mkdir(dir_name)
            f_name = "{0}{1}/{2}.{3}.csv".format(factor_path, factor_name, factor_name, td)
            pp_df[['TICKER_SYMBOL', factor_name.upper()]].to_csv(f_name, encoding='utf-8', header=False, index=False)
        return

    @staticmethod
    def get_neued_signal(x, previous_date, factor_name='value'):
        """
        中性化
        """
        exclude_style_factor = ['BETA', 'RESVOL']
        signal = x.copy(deep=True).dropna()
        if signal.shape[0] > 0:
            series = signal[['ticker', factor_name]].set_index('ticker').dropna()
            # neued = uqer.standardize(uqer.neutralize(uqer.winsorize(series)), target_date=previous_date,
            #                          exclude_style_list=exclude_style_factor)
            neued = uqer.standardize(uqer.neutralize(uqer.winsorize(series)))
            return neued

    @staticmethod
    def merge_dfs(dfs, aligned_cols=[]):
        """
        按给定的列名，合并多个dataframe
        :param dfs:
        :param aligned_cols:
        :return:
        """
        dfs = [df for df in dfs if len(df.index) > 0]
        merged = pd.DataFrame()
        if len(dfs) == 0:
            return merged
        merged = dfs[0]
        for i in range(1, len(dfs)):
            merged = merged.merge(dfs[i], left_on=aligned_cols, right_cols=aligned_cols, how='outer')
        return merged


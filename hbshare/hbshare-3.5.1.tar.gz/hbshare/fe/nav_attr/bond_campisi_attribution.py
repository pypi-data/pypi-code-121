
"""
净值归因模型
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from datetime import datetime, timedelta
from hbshare.fe.common.util.verifier import verify_type
from hbshare.fe.common.util.exception import InputParameterError, PreprocessError
from hbshare.fe.common.util.logger import logger
from hbshare.fe.xwq.analysis.orm.http_request import Curl_Request
from hbshare.fe.xwq.analysis.orm.hbdb import HBDB


class BondCampisiAttributionOutputs:
    def __init__(self):
        self.params_df = None
        self.p_value_df = None
        self.r_square_series = None

    def to_dict(self):
        return {
            "params_df": self.params_df,
            "p_value_df": self.p_value_df,
            "r_square_series": self.r_square_series,
        }


class BondCampisiAttribution:
    def __init__(self, fund_id, start_date, end_date, frequency):
        """
        :param fund_id: 基金代码
        :param start_date: 归因的起始时间
        :param end_date: 归因的结束时间
        :param frequency: 归因频率
        """
        self.fund_id = fund_id
        self.start_date_backup = (datetime.strptime(start_date, '%Y%m%d') - timedelta(200)).strftime('%Y%m%d')
        self.start_date = start_date
        self.end_date = end_date
        self.frequency = frequency
        self.deposit = 0.015 / 365.0
        self.window = 60
        self._verify_input_param()
        self._load_data()
        self._init_bond_campisi_attribution_data()

    def _verify_input_param(self):
        verify_type(self.fund_id, 'fund_id', str)
        verify_type(self.start_date, 'start_date', str)
        verify_type(self.end_date, 'end_date', str)
        verify_type(self.end_date, 'frequency', str)
        if self.frequency not in ['day', 'week', 'month', 'quarter']:
            msg = "frequency not supported, check your input"
            logger.error(msg)
            raise InputParameterError(message=msg)

    def _load_data(self):
        self.calendar_df = HBDB().read_cal(self.start_date_backup, self.end_date)
        self.calendar_df = self.calendar_df.rename(columns={'JYRQ': 'CALENDAR_DATE', 'SFJJ': 'IS_OPEN', 'SFZM': 'IS_WEEK_END', 'SFYM': 'IS_MONTH_END'})
        self.calendar_df['CALENDAR_DATE'] = self.calendar_df['CALENDAR_DATE'].astype(str)
        self.calendar_df = self.calendar_df.sort_values('CALENDAR_DATE')
        self.calendar_df['IS_OPEN'] = self.calendar_df['IS_OPEN'].astype(int).replace({0: 1, 1: 0})
        self.calendar_df['IS_WEEK_END'] = self.calendar_df['IS_WEEK_END'].fillna(0).astype(int)
        self.calendar_df['IS_MONTH_END'] = self.calendar_df['IS_MONTH_END'].fillna(0).astype(int)
        self.calendar_df['MONTH'] = self.calendar_df['CALENDAR_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d').month)
        self.calendar_df['IS_QUARTER_END'] = np.where((self.calendar_df['IS_MONTH_END'] == 1) & (self.calendar_df['MONTH'].isin([3, 6, 9, 12])), 1, 0)
        self.calendar_df['IS_QUARTER_END'] = self.calendar_df['IS_QUARTER_END'].astype(int)
        self.calendar_df = self.calendar_df[['CALENDAR_DATE', 'IS_OPEN', 'IS_WEEK_END', 'IS_MONTH_END', 'IS_QUARTER_END']]

        self.fund_nav_series = HBDB().read_fund_cumret_given_code(self.fund_id, self.start_date_backup, self.end_date)
        self.fund_nav_series = self.fund_nav_series.rename(columns={'JJDM': 'FUND_CODE', 'JZRQ': 'TRADE_DATE', 'HBCL': 'CUM_RET'})
        self.fund_nav_series['TRADE_DATE'] = self.fund_nav_series['TRADE_DATE'].astype(str)
        self.fund_nav_series = self.fund_nav_series.sort_values('TRADE_DATE')
        self.fund_nav_series['ADJ_NAV'] = 0.01 * self.fund_nav_series['CUM_RET'] + 1
        # self.fund_nav_series['ADJ_RET'] = self.fund_nav_series['ADJ_NAV'].pct_change()
        self.fund_nav_series = self.fund_nav_series.set_index('TRADE_DATE')
        self.fund_nav_series = self.fund_nav_series['ADJ_NAV']
        # self.fund_nav_series = self.fund_nav_series.iloc[(np.where(self.fund_nav_series.index == self.start_date)[0][0] - self.window + 1):]

        index_list = ['CBA00301', 'CBA00801', 'CBA00701', 'CBA04201', 'CBA02501', 'CBA03801', 'H11025', '000832', '000906']
        self.factor_data_df = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date_backup, index_list)
        self.factor_data_df = self.factor_data_df.rename(columns={'zqdm': 'INDEX_CODE', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        self.factor_data_df['TRADE_DATE'] = self.factor_data_df['TRADE_DATE'].astype(str)
        self.factor_data_df = self.factor_data_df.pivot(index='TRADE_DATE', columns='INDEX_CODE', values='CLOSE_INDEX')
        self.factor_data_df = self.factor_data_df.sort_index()
        self.factor_data_df = self.factor_data_df.pct_change()
        # self.factor_data_df = self.factor_data_df.iloc[(np.where(self.factor_data_df.index == self.start_date)[0][0] - self.window + 1):]

        duration_index_list = ['CBA00801', 'CBA00701', 'CBA04201', 'CBA02501', 'CBA03801']
        self.duration_data_df = Curl_Request().get_duration_between_dates(self.start_date_backup, self.end_date)
        self.duration_data_df = self.duration_data_df.rename(columns={'zqdm': 'INDEX_CODE', 'jyrq': 'TRADE_DATE', 'jq': 'DURATION'})
        self.duration_data_df = self.duration_data_df[self.duration_data_df['INDEX_CODE'].isin(duration_index_list)]
        self.duration_data_df['TRADE_DATE'] = self.duration_data_df['TRADE_DATE'].astype(str)
        self.duration_data_df = self.duration_data_df.pivot(index='TRADE_DATE', columns='INDEX_CODE', values='DURATION')
        self.duration_data_df = self.duration_data_df.sort_index()
        self.duration_data_df.columns = [col + '_JQ' for col in self.duration_data_df.columns]

        self.factor_data_df = pd.concat([self.factor_data_df, self.duration_data_df], axis=1)
        self.factor_data_df['F_level'] = self.factor_data_df['CBA00301'] - self.deposit
        self.factor_data_df['F_slope'] = self.factor_data_df['CBA00701_JQ'] / (self.factor_data_df['CBA00701_JQ'] - self.factor_data_df['CBA00801_JQ']) * self.factor_data_df['CBA00801'] \
                                       + self.factor_data_df['CBA00801_JQ'] / (self.factor_data_df['CBA00801_JQ'] - self.factor_data_df['CBA00701_JQ']) * self.factor_data_df['CBA00701']
        self.factor_data_df['F_credit'] = self.factor_data_df['CBA02501_JQ'] / (self.factor_data_df['CBA02501_JQ'] - self.factor_data_df['CBA04201_JQ']) * self.factor_data_df['CBA04201'] \
                                        + self.factor_data_df['CBA04201_JQ'] / (self.factor_data_df['CBA04201_JQ'] - self.factor_data_df['CBA02501_JQ']) * self.factor_data_df['CBA02501']
        self.factor_data_df['F_default'] = self.factor_data_df['CBA04201_JQ'] / (self.factor_data_df['CBA04201_JQ'] - self.factor_data_df['CBA03801_JQ']) * self.factor_data_df['CBA03801'] \
                                         + self.factor_data_df['CBA03801_JQ'] / (self.factor_data_df['CBA03801_JQ'] - self.factor_data_df['CBA04201_JQ']) * self.factor_data_df['CBA04201']
        self.factor_data_df['F_currency'] = self.factor_data_df['H11025'] - self.deposit
        self.factor_data_df['F_convertible'] = self.factor_data_df['000832'] - self.deposit
        self.factor_data_df['F_equity'] = self.factor_data_df['000906'] - self.deposit

    def get_trading_day_list(self, nav_frequency):
        if nav_frequency == 'day':
            trading_day_list = sorted(list(self.calendar_df[self.calendar_df['IS_OPEN'] == 1]['CALENDAR_DATE']))
        elif nav_frequency == 'week':
            trading_day_list = sorted(list(self.calendar_df[self.calendar_df['IS_WEEK_END'] == 1]['CALENDAR_DATE']))
        elif nav_frequency == 'month':
            trading_day_list = sorted(list(self.calendar_df[self.calendar_df['IS_MONTH_END'] == 1]['CALENDAR_DATE']))
        elif nav_frequency == 'quarter':
            trading_day_list = sorted(list(self.calendar_df[self.calendar_df['IS_QUARTER_END'] == 1]['CALENDAR_DATE']))
        else:
            trading_day_list = []
        return trading_day_list

    def _init_bond_campisi_attribution_data(self):
        compute_list = self.get_trading_day_list(self.frequency)
        compute_list = [date for date in compute_list if (date >= self.start_date) and (date <= self.end_date)]
        date_list = self.get_trading_day_list('day')
        if len(compute_list) < 1:
            msg = "There is no complete {0} interval during start_date and end_date, check your input".format(self.frequency)
            logger.error(msg)
            raise InputParameterError(message=msg)

        preprocessed_data = dict()
        if not (self.fund_nav_series.empty or self.factor_data_df.empty):
            fund_nav_series = self.fund_nav_series.reindex(date_list).interpolate().dropna().sort_index()
            fund_nav_series = fund_nav_series / fund_nav_series.iloc[0]
            fund_ret_series = fund_nav_series.pct_change().dropna()
            factor_data_df = self.factor_data_df.reindex(fund_ret_series.index).fillna(0.)
            assert (fund_ret_series.shape[0] == factor_data_df.shape[0])

            for date in compute_list:
                interval_data = dict()
                fund_ret_series_date = fund_ret_series[fund_ret_series.index <= date].iloc[-self.window:]
                factor_data_df_date = factor_data_df[factor_data_df.index <= date].iloc[-self.window:]
                if len(fund_ret_series_date) / self.window <= 0.7 or len(factor_data_df_date) / self.window <= 0.7:
                    interval_data['fund_ret_series'] = pd.Series()
                    interval_data['factor_data_df'] = pd.DataFrame()
                else:
                    interval_data['fund_ret_series'] = fund_ret_series_date
                    interval_data['factor_data_df'] = factor_data_df_date
                preprocessed_data[date] = interval_data
            self.preprocessed_data = preprocessed_data
        else:
            msg = "Data empty occurred, check your input"
            logger.error(msg)
            raise PreprocessError(message=msg)

    def _campisi_analysis(self):
        bond_fund_position = HBDB().read_bond_fund_position_given_code(self.fund_id)
        bond_fund_position = bond_fund_position.rename(columns={'jjdm': 'FUND_CODE', 'jsrq': 'REPORT_DATE', 'gptzsz': 'STOCK', 'kzzsz': 'CONVERTIBLE'})
        bond_fund_position['REPORT_DATE'] = bond_fund_position['REPORT_DATE'].astype(str)
        bond_fund_position = bond_fund_position.sort_values('REPORT_DATE')
        trade_cal = self.calendar_df[self.calendar_df['IS_OPEN'] == 1]
        trade_cal['TRADE_DATE'] = trade_cal['CALENDAR_DATE']
        self.calendar_df = self.calendar_df.merge(trade_cal[['CALENDAR_DATE', 'TRADE_DATE']], on=['CALENDAR_DATE'], how='left')
        self.calendar_df['TRADE_DATE'] = self.calendar_df['TRADE_DATE'].fillna(method='ffill')
        bond_fund_position = bond_fund_position.merge(self.calendar_df[['CALENDAR_DATE', 'TRADE_DATE']], left_on='REPORT_DATE', right_on='CALENDAR_DATE', how='left')

        params_list, p_value_list, r_square_list = [], [], []
        for date, period_data in self.preprocessed_data.items():
            bond_fund_position_date = bond_fund_position[bond_fund_position['TRADE_DATE'] <= date].iloc[-2:]
            bond_fund_position_stock = True if bond_fund_position_date['STOCK'].fillna(0.0).sum() > 0 else False
            bond_fund_position_convertible = True if bond_fund_position_date['CONVERTIBLE'].fillna(0.0).sum() > 0 else False
            factor_list = ['F_level', 'F_slope', 'F_credit', 'F_default', 'F_currency']
            if bond_fund_position_convertible:
                factor_list = factor_list + ['F_convertible']
            if bond_fund_position_stock:
                factor_list = factor_list + ['F_equity']
            
            if period_data['fund_ret_series'].empty or period_data['factor_data_df'].empty:
                logger.warning("{}: fund_ret_series or factor_data_df is empty !".format(date))
                params = pd.DataFrame(index=[date], columns=factor_list)
                p_value = pd.DataFrame(index=[date], columns=factor_list)
                r_square = pd.Series(index=[date])
            else:
                fund_ret_series = period_data['fund_ret_series']
                fund_ret_series = (fund_ret_series - fund_ret_series.mean()) / fund_ret_series.std(ddof=1)
                factor_data_df = period_data['factor_data_df'][factor_list]
                factor_data_df = (factor_data_df - factor_data_df.mean()) / factor_data_df.std(ddof=1)
                factor_data_df = sm.add_constant(factor_data_df)
                result = sm.OLS(fund_ret_series, factor_data_df.values).fit()
                params = pd.DataFrame(result.params, columns=[date]).T
                params.columns = ['CONST'] + factor_list
                p_value = pd.DataFrame(result.pvalues, columns=[date]).T
                p_value.columns = ['CONST'] + factor_list
                r_square = pd.Series(result.rsquared)
                r_square.index = [date]
            params_list.append(params)
            p_value_list.append(p_value)
            r_square_list.append(r_square)
            print('[{0}]/[{1}]归因done'.format(self.fund_id, date))
        params_df = pd.concat(params_list)
        p_value_df = pd.concat(p_value_list)
        r_square_series = pd.concat(r_square_list)
        return params_df, p_value_df, r_square_series

    def get_all(self):
        output = BondCampisiAttributionOutputs()
        params_df, p_value_df, r_square_series = self._campisi_analysis()
        output.params_df = params_df
        output.p_value_df = p_value_df
        output.r_square_series = r_square_series
        return output.to_dict()


if __name__ == '__main__':
    # # 分析样本：成立满6个月的纯债型、混合型债券基金
    # bond_fund = HBDB().read_bond_fund_info()
    # bond_fund = bond_fund.rename(columns={'jjdm': 'FUND_CODE', 'jjmc': 'FUND_FULL_NAME', 'jjjc': 'FUND_SHORT_NAME', 'clrq': 'BEGIN_DATE', 'zzrq': 'END_DATE', 'ejfl': 'FUND_TYPE', 'kffb': 'OPEN_CLOSE'})
    # bond_fund['FUND_TYPE'] = bond_fund['FUND_TYPE'].replace({'22': '短期纯债型', '23': '混合债券型一级', '24': '混合债券型二级', '27': '中长期纯债型'})
    # bond_fund['OPEN_CLOSE'] = bond_fund['OPEN_CLOSE'].replace({'0': '开放式', '1': '封闭式'})
    # bond_fund = bond_fund.dropna(subset=['BEGIN_DATE'])
    # bond_fund['END_DATE'] = bond_fund['END_DATE'].fillna(20990101)
    # bond_fund['BEGIN_DATE'] = bond_fund['BEGIN_DATE'].astype(int)
    # bond_fund['END_DATE'] = bond_fund['END_DATE'].astype(int)
    # bond_fund['BEGIN_DATE'] = bond_fund['BEGIN_DATE'].astype(str)
    # bond_fund['END_DATE'] = bond_fund['END_DATE'].astype(str)
    # date_before = (datetime.today() - timedelta(180)).strftime('%Y%m%d')
    # bond_fund = bond_fund[bond_fund['BEGIN_DATE'] <= date_before]

    res = BondCampisiAttribution(fund_id='050027', start_date='20220401', end_date='20220506', frequency='day').get_all()
    print(res)

    # # 样图
    # import matplotlib.pyplot as plt
    # plt.rcParams['font.sans-serif'] = ['SimHei']
    # plt.rcParams['axes.unicode_minus'] = False
    # line_color_list = ['#F04950', '#6268A2', '#959595', '#333335', '#EE703F', '#7E4A9B', '#8A662C', '#44488E']
    # bar_color_list = ['#C94649', '#EEB2B4', '#E1777A', '#D57C56', '#E39A79', '#DB8A66', '#E5B88C',
    #                   '#8588B7', '#B4B6D1', '#55598D', '#628497', '#A9C6CB', '#866EA9', '#B79BC7',
    #                   '#7D7D7E', '#CACACA', '#A7A7A8', '#606063', '#C4C4C4', '#99999B', '#B7B7B7']
    # periods = 4
    #
    # params_df = res['params_df'].drop('CONST', axis=1)
    # params_df = params_df.sort_index().iloc[-periods:].fillna(0.0)
    # xlabels = list(params_df.columns)
    # xlabels = [xlabel.replace('F_level', '系统').replace('F_slope', '斜率').replace('F_credit', '信用风险溢价').replace('F_default', '违约风险补偿').replace('F_currency', '货币').replace('F_convertible', '转债').replace('F_equity', '权益')for xlabel in xlabels]
    # theta = np.linspace(0.0, 2.0 * np.pi, len(xlabels), endpoint=False)
    # ydata = params_df.values
    # labels = list(params_df.index)
    # labels = [label[:6].replace('03', 'Q1').replace('06', 'Q2').replace('09', 'Q3').replace('12', 'Q4') for label in labels]
    # for i in range(periods):
    #     plt.polar(np.concatenate((theta, [theta[0]])), np.concatenate((ydata[i], [ydata[i][0]])), label=labels[i], color=line_color_list[i])
    # plt.gca().set_xticks(theta)
    # plt.gca().set_xticklabels(xlabels)
    # plt.legend(ncol=periods, bbox_to_anchor=(1, -0.05))
    # plt.title('各因子暴露')
    # plt.tight_layout()
    # plt.show()
    #
    # p_value_df = res['p_value_df'].drop('CONST', axis=1)
    # p_value_df = p_value_df.sort_index().iloc[-periods:].fillna(0.0)
    # xlabels = list(p_value_df.columns)
    # xlabels = [xlabel.replace('F_level', '系统').replace('F_slope', '斜率').replace('F_credit', '信用风险溢价').replace('F_default', '违约风险补偿').replace('F_currency', '货币').replace('F_convertible', '转债').replace('F_equity', '权益') for xlabel in xlabels]
    # theta = np.linspace(0.0, 2.0 * np.pi, len(xlabels), endpoint=False)
    # ydata = p_value_df.values
    # labels = list(p_value_df.index)
    # labels = [label[:6].replace('03', 'Q1').replace('06', 'Q2').replace('09', 'Q3').replace('12', 'Q4') for label in labels]
    # for i in range(periods):
    #     plt.polar(np.concatenate((theta, [theta[0]])), np.concatenate((ydata[i], [ydata[i][0]])), label=labels[i], color=line_color_list[i])
    # plt.gca().set_xticks(theta)
    # plt.gca().set_xticklabels(xlabels)
    # plt.legend(ncol=periods, bbox_to_anchor=(1, -0.05))
    # plt.title('各因子暴露p值')
    # plt.tight_layout()
    # plt.show()
    #
    # r_square_series = res['r_square_series']
    # r_square_series = r_square_series.sort_index().iloc[-periods:].fillna(0.0)
    # r_square_series.index = map(lambda x: x[:6].replace('03', 'Q1').replace('06', 'Q2').replace('09', 'Q3').replace('12', 'Q4'), r_square_series.index)
    # plt.bar(range(periods), r_square_series, width=0.5, tick_label=list(r_square_series.index), label='回归日期', color=bar_color_list[0])
    # plt.legend()
    # plt.title('回归R2')
    # plt.tight_layout()
    # plt.show()
    #
    # params_df = res['params_df'].drop('CONST', axis=1)
    # params_df = params_df.sort_index().fillna(0.0)
    # params_df.index = map(lambda x: datetime.strptime(str(x), '%Y%m%d'), params_df.index)
    # labels = list(params_df.columns)
    # labels = [label.replace('F_level', '系统').replace('F_slope', '斜率').replace('F_credit', '信用风险溢价').replace('F_default', '违约风险补偿').replace('F_currency', '货币').replace('F_convertible', '转债').replace('F_equity', '权益') for label in labels]
    # params_df.columns = labels
    # fig, ax = plt.subplots(figsize=(10, 5))
    # for i in range(len(labels)):
    #     plt.plot(params_df.index, params_df[labels[i]].values, label=labels[i], color=line_color_list[i])
    # plt.legend(ncol=len(labels), bbox_to_anchor=(0.9, -0.20))
    # plt.xticks(rotation=90)
    # plt.title('各因子暴露变化')
    # plt.tight_layout()
    # plt.show()
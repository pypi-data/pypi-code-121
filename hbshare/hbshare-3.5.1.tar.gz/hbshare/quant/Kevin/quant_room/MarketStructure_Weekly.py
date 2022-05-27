"""
指增策略 - 市场结构Weekly
"""
import pandas as pd
import hbshare as hbs
import numpy as np
import os
from scipy import stats
import statsmodels.api as sm
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params, style_names, industry_names
import datetime
import plotly.graph_objs as go
from plotly.offline import plot as plot_ly
from statsmodels.stats.weightstats import DescrStatsW
from hbshare.fe.common.util.data_loader import get_trading_day_list
import plotly.figure_factory as ff
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB


def plot_render(plot_dic, width=1200, height=600, **kwargs):
    kwargs['output_type'] = 'div'
    plot_str = plotly.offline.plot(plot_dic, **kwargs)
    print('%%angular <div style="height: %ipx; width: %spx"> %s </div>' % (height, width, plot_str))


def get_shift_date(date):
    trade_dt = datetime.datetime.strptime(date, '%Y%m%d')
    pre_date = (trade_dt - datetime.timedelta(days=100)).strftime('%Y%m%d')

    sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
        pre_date, date)
    res = hbs.db_data_query('readonly', sql_script, page_size=5000)
    df = pd.DataFrame(res['data']).rename(
        columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                 "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
    df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
    df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
    df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

    trading_day_list = df[df['isMonthEnd'] == 1]['calendarDate'].tolist()

    return trading_day_list[-1]


def get_benchmark_components(date):
    sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and " \
                 "SecuCode in ('000300', '000905', '000852')"
    res = hbs.db_data_query('readonly', sql_script)
    index_info = pd.DataFrame(res['data'])
    inner_code_series = index_info.set_index('SECUCODE')['INNERCODE']

    weight = []
    for benchmark_id in ['000300', '000905', '000852']:
        inner_code = inner_code_series.loc[benchmark_id]
        sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                     "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                     "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        weight_df = data.rename(
            columns={"SECUCODE": "ticker", "ENDDATE": "effDate", "WEIGHT": "weight"})
        weight_df['benchmark_id'] = benchmark_id
        weight.append(weight_df[['ticker', 'benchmark_id']])

    return pd.concat(weight)


def get_mkt_info(start_date, end_date):
    path = r'D:\kevin\risk_model_jy\RiskModel\data\common_data\chg_pct'
    listdir = os.listdir(path)
    listdir = [x for x in listdir if start_date < x.split('.')[0] <= end_date]
    data = []
    for filename in listdir:
        date_t_rate = pd.read_csv(os.path.join(path, filename), dtype={"tradeDate": str})
        date_t_rate['ticker'] = date_t_rate['ticker'].apply(lambda x: str(x).zfill(6))
        data.append(date_t_rate)

    data = pd.concat(data)
    # filter
    data = data[(data['dailyReturnReinv'] >= -0.2) & (data['dailyReturnReinv'] <= 0.2)]
    data = pd.pivot_table(data, index='tradeDate', columns='ticker', values='dailyReturnReinv').sort_index()
    data = data.dropna(how='any', axis=1)

    return data


def get_benchmark_weight(date):
    sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and " \
                 "SecuCode in ('000300', '000905', '000852')"
    res = hbs.db_data_query('readonly', sql_script)
    index_info = pd.DataFrame(res['data'])
    inner_code_series = index_info.set_index('SECUCODE')['INNERCODE']

    weight = []
    for benchmark_id in ['000905']:
        inner_code = inner_code_series.loc[benchmark_id]
        sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                     "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                     "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        weight_df = data.rename(
            columns={"SECUCODE": "ticker", "ENDDATE": "effDate", "WEIGHT": "weight"})
        weight_df['benchmark_id'] = benchmark_id
        weight.append(weight_df[['ticker', 'benchmark_id', 'weight']])

    return pd.concat(weight)


def get_industry_class(trade_date):
    path = r'D:\kevin\risk_model_jy\RiskModel\data'
    data = pd.read_json(os.path.join(path, r'common_data/sw_new.json'), dtype={'ticker': str})

    data['outDate'] = data['outDate'].fillna(20991231)
    data['intoDate'] = data['intoDate'].map(int).map(str)
    data['outDate'] = data['outDate'].map(int).map(str)

    data = data[(data['intoDate'] <= trade_date) & (data['outDate'] >= trade_date)].drop_duplicates(subset='ticker')

    return data.set_index('ticker')['industryName1']


def group_test(df, group_col, value_col):
    df_copy = df.copy()
    bins = [df_copy[group_col].quantile(x) for x in [0, 0.2, 0.4, 0.6, 0.8, 1.0]]
    labels = ['group_' + str(x) for x in range(1, 6)]
    df_copy['group'] = pd.cut(df_copy[group_col], bins, right=False, labels=labels)

    return df_copy.groupby('group')[value_col].mean()


class AlphaSeries:
    def __init__(self, start_date, end_date, fund_info, benchmark_id='000905'):
        self.start_date = start_date
        self.end_date = end_date
        self.fund_info = fund_info
        self.benchmark_id = benchmark_id

    def calculate(self):
        trading_day_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")
        fund_dict = self.fund_info.set_index('管理人')['产品ID'].to_dict()
        nav_series_list = []
        for name, fund_id in fund_dict.items():
            start_date = self.fund_info[self.fund_info['管理人'] == name]['运作起始日期'].values[0]
            start_date = pd.to_datetime(start_date).strftime('%Y%m%d')
            sql_script = "SELECT a.jjdm fund_id, b.jzrq TRADEDATE, b.fqdwjz as ADJ_NAV from " \
                         "st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b where a.cpfl = '4' and a.jjdm = b.jjdm " \
                         "and a.jjzt not in ('3') " \
                         "and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                         "order by b.jzrq".format(fund_id, start_date, self.end_date)
            res = hbs.db_data_query("highuser", sql_script, page_size=5000)
            data = pd.DataFrame(res['data']).set_index('TRADEDATE')['ADJ_NAV']
            data.name = name
            nav_series_list.append(data)
        nav_df = pd.concat(nav_series_list, axis=1).sort_index().reindex(trading_day_list).dropna(how='all', axis=0)
        nav_df = nav_df.fillna(method='ffill')

        for col in nav_df.columns:
            nav_df[col] = nav_df[col] / nav_df[col].shift(1) - 1
        mean_alpha = nav_df.mean(axis=1).dropna()  # 策略周度平均收益

        sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format(self.benchmark_id, self.start_date, self.end_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        index_return = data.set_index('TRADEDATE').reindex(trading_day_list)['TCLOSE'].pct_change().dropna()

        idx = mean_alpha.index.intersection(index_return.index)
        excess_return = mean_alpha.reindex(idx) - index_return.reindex(idx)

        return excess_return


class MarketLiquidity:
    def __init__(self, trade_date):
        self.trade_date = trade_date

    def run(self):
        # A股行情
        sql_script = "SELECT SYMBOL, SNAME, VOTURNOVER, PCHG FROM finchina.CHDQUOTE WHERE" \
                     " TDATE = {}".format(self.trade_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script, page_size=5000)['data'])
        data = data[data['SYMBOL'].str[0].isin(['0', '3', '6'])]
        data = data[data['VOTURNOVER'] > 1e-8]
        # data = data[~data['SNAME'].str.contains('ST')]
        # data = data[~data['SNAME'].str.contains('N')]
        # data = data[~data['SNAME'].str.contains('C')]
        data = data.rename(columns={"SYMBOL": "ticker", "VOTURNOVER": "trade_volume"})[
            ['ticker', 'trade_volume']].dropna()
        pre_date = get_shift_date(self.trade_date)
        bm_components = get_benchmark_components(pre_date)
        data = pd.merge(data, bm_components, on='ticker', how='left')
        data['benchmark_id'] = data['benchmark_id'].fillna('other')

        path = r'D:\kevin\risk_model_jy\RiskModel\data'
        date_t_rate = pd.read_json(os.path.join(path, 'common_data/turnover_rate/{0}.json'.format(self.trade_date)),
                                   typ='series').to_frame('turnover_rate')
        date_t_rate.index.name = 'ticker'
        date_t_rate = date_t_rate.reset_index()
        date_t_rate['ticker'] = date_t_rate['ticker'].apply(lambda x: str(x).zfill(6))
        data = pd.merge(data, date_t_rate, on='ticker')
        data['equity'] = data['trade_volume'] / data['turnover_rate']

        turnover_rate = data.groupby('benchmark_id').apply(lambda x: x['trade_volume'].sum() / x['equity'].sum())
        turnover_rate.loc['market_A'] = data['trade_volume'].sum() / data['equity'].sum()
        tmp = data[data['benchmark_id'].isin(['000852', 'other'])]
        turnover_rate.loc['1000_plus_other'] = tmp['trade_volume'].sum() / tmp['equity'].sum()
        turnover_rate = turnover_rate.to_frame('value').reset_index().rename(columns={"benchmark_id": "factor_name"})
        map_dict = {"000300": "to_300", "000905": "to_500", "000852": "to_1000", "other": "to_other",
                    "market_A": "to_A", "1000_plus_other": "to_small"}
        turnover_rate['factor_name'] = turnover_rate['factor_name'].map(map_dict)

        sql_script = "SELECT * FROM mac_stock_trading_cr WHERE TRADE_DATE = {}".format(self.trade_date)
        engine = create_engine(engine_params)
        tmp = pd.read_sql(sql_script, engine)
        liq_ratio = data.groupby('benchmark_id')['trade_volume'].sum() / data['trade_volume'].sum()
        liq_ratio.loc['1000_plus_other'] = liq_ratio.loc['000852'] + liq_ratio.loc['other']
        liq_ratio.loc['top_5p'] = tmp['cr5'].values[0]
        liq_ratio.loc['top_10p'] = tmp['cr10'].values[0]
        liq_ratio = liq_ratio.to_frame('value').reset_index().rename(columns={"benchmark_id": "factor_name"})
        map_dict = {"000300": "tr_300", "000905": "tr_500", "000852": "tr_1000", "other": "tr_other",
                    "1000_plus_other": "tr_small", "top_5p": "top_5p", "top_10p": "top_10p"}
        liq_ratio['factor_name'] = liq_ratio['factor_name'].map(map_dict)

        factor = pd.concat([turnover_rate, liq_ratio])

        factor.to_csv('D:\\AlphaMonitor\\MarketLiquidity\\{}.csv'.format(self.trade_date), index=False)


class LiquidityTest:
    def __init__(self, start_date, end_date, alpha):
        self.start_date = start_date
        self.end_date = end_date
        self.alpha_series = alpha

    def run(self):
        week_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")

        data_path = "D:\\AlphaMonitor\\MarketLiquidity"
        filenames = os.listdir(data_path)
        daily_data = []
        for file_name in filenames:
            data = pd.read_csv(os.path.join(data_path, file_name))
            data['trade_date'] = file_name.split('.')[0]
            daily_data.append(data)
        daily_data = pd.concat(daily_data)
        daily_data = pd.pivot_table(daily_data, index='trade_date', columns='factor_name', values='value').sort_index()

        factor_list = []
        for i in range(1, len(week_list)):
            pre_week = week_list[i - 1]
            current_week = week_list[i]
            period_data = daily_data[(daily_data.index > pre_week) & (daily_data.index <= current_week)]
            if len(period_data) >= 4:
                factor = period_data.mean().to_frame('value').reset_index()
                factor['trade_date'] = current_week
                factor_list.append(factor)
            else:
                pass

        factor_df = pd.concat(factor_list)
        factor_df = pd.pivot_table(factor_df, index='trade_date', columns='factor_name', values='value').sort_index()

        factor_df = pd.merge(factor_df, self.alpha_series.to_frame('alpha'), left_index=True, right_index=True)

        group_alpha = group_test(factor_df, 'tr_1000', 'alpha')

        return group_alpha


class StockDivergence:
    def __init__(self, start_date, end_date, alpha, mode='regular'):
        self.start_date = start_date
        self.end_date = end_date
        self.alpha_series = alpha
        self.mode = mode

    @staticmethod
    def get_mkt_info(start_date, end_date):
        path = r'D:\kevin\risk_model_jy\RiskModel\data\common_data\chg_pct'
        listdir = os.listdir(path)
        listdir = [x for x in listdir if start_date < x.split('.')[0] <= end_date]
        data = []
        for filename in listdir:
            date_t_rate = pd.read_csv(os.path.join(path, filename), dtype={"tradeDate": str})
            date_t_rate['ticker'] = date_t_rate['ticker'].apply(lambda x: str(x).zfill(6))
            data.append(date_t_rate)

        data = pd.concat(data)
        # filter
        data = data[(data['dailyReturnReinv'] >= -0.2) & (data['dailyReturnReinv'] <= 0.2)]
        data = pd.pivot_table(data, index='tradeDate', columns='ticker', values='dailyReturnReinv').sort_index()
        data = data.dropna(how='any', axis=1)

        return data

    @staticmethod
    def get_spec_info(start_date, end_date):
        path = r'D:\kevin\risk_model_jy\RiskModel\data\zzqz_sw\specific_return'
        listdir = os.listdir(path)
        listdir = [x for x in listdir if start_date < x.split('.')[0] <= end_date]
        data = []
        for filename in listdir:
            date_t_rate = pd.read_csv(os.path.join(path, filename), dtype={"trade_date": str})
            date_t_rate['ticker'] = date_t_rate['ticker'].apply(lambda x: str(x).zfill(6))
            data.append(date_t_rate)

        data = pd.concat(data)
        # filter
        data = pd.pivot_table(data, index='trade_date', columns='ticker', values='s_ret').sort_index()
        data = data.dropna(how='any', axis=1)

        return data

    @staticmethod
    def calculate_factor(df, date):
        factor = pd.DataFrame(index=[date], columns=['std_1', 'std_2', 'kurt_1', 'kurt_2'])
        # method1
        factor.loc[date, 'std_1'] = df.std(axis=1).mean()
        factor.loc[date, 'kurt_1'] = df.kurt(axis=1).mean()
        # method2
        factor.loc[date, 'std_2'] = ((1 + df).prod() - 1).std()
        factor.loc[date, 'kurt_2'] = ((1 + df).prod() - 1).kurt()

        factor = pd.melt(factor, var_name='factor_name')

        return factor

    def run(self):
        week_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")
        factor_list = []
        from tqdm import tqdm
        for i in tqdm(range(len(week_list) - 1)):
            pre_week = week_list[i]
            current_week = week_list[i + 1]
            if self.mode == "regular":
                period_data = self.get_mkt_info(pre_week, current_week)
            else:
                period_data = self.get_spec_info(pre_week, current_week)
            if period_data.shape[0] < 4:
                continue
            pre_date = get_shift_date(current_week)
            bm_components = get_benchmark_components(pre_date)

            factor_list_period = []

            # 300
            universe = bm_components[bm_components['benchmark_id'] == '000300']['ticker'].tolist()
            idx = set(universe).intersection(set(period_data.columns.tolist()))
            factor = self.calculate_factor(period_data[idx], current_week)
            factor['universe'] = 'hs300'
            factor_list_period.append(factor)
            # 500
            universe = bm_components[bm_components['benchmark_id'] == '000905']['ticker'].tolist()
            idx = set(universe).intersection(set(period_data.columns.tolist()))
            factor = self.calculate_factor(period_data[idx], current_week)
            factor['universe'] = 'zz500'
            factor_list_period.append(factor)
            # 1000
            universe = bm_components[bm_components['benchmark_id'] == '000852']['ticker'].tolist()
            idx = set(universe).intersection(set(period_data.columns.tolist()))
            factor = self.calculate_factor(period_data[idx], current_week)
            factor['universe'] = 'zz1000'
            factor_list_period.append(factor)
            factor_list_period.append(factor)
            # other
            universe = bm_components['ticker'].tolist()
            idx = set(period_data.columns.tolist()) - set(universe)
            factor = self.calculate_factor(period_data[idx], current_week)
            factor['universe'] = 'other'
            factor_list_period.append(factor)
            # 1000 + other
            universe = bm_components[bm_components['benchmark_id'].isin(['000300', '000905'])]['ticker'].tolist()
            idx = set(period_data.columns.tolist()) - set(universe)
            factor = self.calculate_factor(period_data[idx], current_week)
            factor['universe'] = 'small'
            factor_list_period.append(factor)
            # all_market
            factor = self.calculate_factor(period_data, current_week)
            factor['universe'] = 'all'
            factor_list_period.append(factor)

            t_date_factor = pd.concat(factor_list_period)
            t_date_factor['trade_date'] = current_week

            factor_list.append(t_date_factor)

        factor_df = pd.concat(factor_list)
        factor_df['f_name'] = factor_df['universe'] + '_' + factor_df['factor_name']
        factor_df = pd.pivot_table(factor_df, index='trade_date', columns='f_name', values='value').sort_index()
        factor_df = pd.merge(factor_df, self.alpha_series.to_frame('alpha'), left_index=True, right_index=True)

        group_alpha = group_test(factor_df, 'small_std_2', 'alpha')

        return group_alpha


class MarketSpread:
    def __init__(self, start_date, end_date, alpha):
        self.start_date = start_date
        self.end_date = end_date
        self.alpha_series = alpha

    @staticmethod
    def get_mkt_info(start_date, end_date):
        path = r'D:\kevin\risk_model_jy\RiskModel\data\common_data\chg_pct'
        listdir = os.listdir(path)
        listdir = [x for x in listdir if start_date < x.split('.')[0] <= end_date]
        data = []
        for filename in listdir:
            date_t_rate = pd.read_csv(os.path.join(path, filename), dtype={"tradeDate": str})
            date_t_rate['ticker'] = date_t_rate['ticker'].apply(lambda x: str(x).zfill(6))
            data.append(date_t_rate)

        data = pd.concat(data)
        # filter
        data = data[(data['dailyReturnReinv'] >= -0.2) & (data['dailyReturnReinv'] <= 0.2)]
        data = pd.pivot_table(data, index='tradeDate', columns='ticker', values='dailyReturnReinv').sort_index()
        data = data.dropna(how='any', axis=1)

        return data

    @staticmethod
    def _calculate(df, index_return):
        win_ratio = 100 - stats.percentileofscore(np.array(df['return']), index_return)
        win_med = df[df['return'] >= index_return]['return'].median()
        lose_med = df[df['return'] < index_return]['return'].median()

        return win_ratio, win_med, lose_med

    def run(self):
        week_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")
        sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format('000905', self.start_date, self.end_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        data['index_return'] = data['TCLOSE'].pct_change()
        index_return = data.set_index('TRADEDATE')['index_return']
        win_ratio_df = pd.DataFrame(
            index=week_list, columns=['win_ratio_500', 'win_spread_500', 'lose_spread_500',
                                      'win_ratio_1000', 'win_spread_1000', 'lose_spread_1000',
                                      'win_ratio_other', 'win_spread_other', 'lose_spread_other',
                                      'win_ratio_small', 'win_spread_small', 'lose_spread_small',
                                      'win_ratio_all', 'win_spread_all', 'lose_spread_all'])
        from tqdm import tqdm
        for i in tqdm(range(len(week_list) - 1)):
            pre_week = week_list[i]
            current_week = week_list[i + 1]
            period_data = self.get_mkt_info(pre_week, current_week)
            period_return = (1 + index_return.loc[period_data.index]).prod() - 1
            period_ret = (1 + period_data).prod() - 1
            period_ret = period_ret.to_frame('return')
            if period_data.shape[0] < 4:
                continue
            pre_date = get_shift_date(current_week)
            bm_components = get_benchmark_components(pre_date)

            # 500
            universe = bm_components[bm_components['benchmark_id'] == '000905']['ticker'].tolist()
            idx = set(universe).intersection(set(period_data.columns.tolist()))
            win_ratio, win_med, lose_med = self._calculate(period_ret.loc[idx], period_return)
            win_ratio_df.loc[current_week, ['win_ratio_500', 'win_spread_500', 'lose_spread_500']] = \
                [win_ratio, win_med - period_return, period_return - lose_med]
            # 1000
            universe = bm_components[bm_components['benchmark_id'] == '000852']['ticker'].tolist()
            idx = set(universe).intersection(set(period_data.columns.tolist()))
            win_ratio, win_med, lose_med = self._calculate(period_ret.loc[idx], period_return)
            win_ratio_df.loc[current_week, ['win_ratio_1000', 'win_spread_1000', 'lose_spread_1000']] = \
                [win_ratio, win_med - period_return, period_return - lose_med]
            # other
            universe = bm_components['ticker'].tolist()
            idx = set(period_data.columns.tolist()) - set(universe)
            win_ratio, win_med, lose_med = self._calculate(period_ret.loc[idx], period_return)
            win_ratio_df.loc[current_week, ['win_ratio_other', 'win_spread_other', 'lose_spread_other']] = \
                [win_ratio, win_med - period_return, period_return - lose_med]
            # small
            universe = bm_components[bm_components['benchmark_id'].isin(['000300', '000905'])]['ticker'].tolist()
            idx = set(period_data.columns.tolist()) - set(universe)
            win_ratio, win_med, lose_med = self._calculate(period_ret.loc[idx], period_return)
            win_ratio_df.loc[current_week, ['win_ratio_small', 'win_spread_small', 'lose_spread_small']] = \
                [win_ratio, win_med - period_return, period_return - lose_med]
            # all
            win_ratio, win_med, lose_med = self._calculate(period_ret, period_return)
            win_ratio_df.loc[current_week, ['win_ratio_all', 'win_spread_all', 'lose_spread_all']] = \
                [win_ratio, win_med - period_return, period_return - lose_med]

        win_ratio_df = win_ratio_df.dropna(axis=0)
        win_ratio_df['f1'] = win_ratio_df['win_spread_other'] - win_ratio_df['lose_spread_other']
        win_ratio_df['f2'] = win_ratio_df['win_ratio_other'] * win_ratio_df['win_spread_other']
        win_ratio_df['f3'] = (100 - win_ratio_df['win_ratio_other']) * win_ratio_df['lose_spread_other']
        win_ratio_df['f4'] = win_ratio_df['f2'] - win_ratio_df['f3']

        factor_df = pd.merge(win_ratio_df, self.alpha_series.to_frame('alpha'), left_index=True, right_index=True)

        # group_alpha = group_test(factor_df, 'small_std_2', 'alpha')

        name_list = ['win_ratio_other', 'f1', 'f2', 'f3', 'f4']
        group_list = []
        for name in name_list:
            group_alpha = group_test(factor_df, name, 'alpha').to_frame(name)
            group_list.append(group_alpha)

        group_df = pd.concat(group_list, axis=1)

        return group_df


class StyleFactor:
    def __init__(self, start_date, end_date, alpha):
        self.start_date = start_date
        self.end_date = end_date
        self.alpha_series = alpha

    @staticmethod
    def get_style_factor(start_date, end_date):
        """
        风格因子收益率
        """
        trade_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=30)).strftime('%Y%m%d')
        sql_script = "SELECT * FROM factor_return where trade_date >= {} and trade_date <= {}".format(pre_date,
                                                                                                      end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        data = pd.pivot_table(
            data, index='trade_date', columns='factor_name', values='factor_ret').sort_index()[style_names]

        return data

    @staticmethod
    def get_ind_factor(start_date, end_date):
        """
        行业因子收益率
        """
        trade_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=30)).strftime('%Y%m%d')
        sql_script = "SELECT * FROM factor_return where trade_date >= {} and trade_date <= {}".format(pre_date,
                                                                                                      end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        data = pd.pivot_table(
            data, index='trade_date', columns='factor_name', values='factor_ret').sort_index()[industry_names.values()]

        return data

    def run_factor_return(self):
        week_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")
        style_df = self.get_style_factor(self.start_date, self.end_date)

        factor_return = []

        for i in range(len(week_list) - 1):
            pre_week = week_list[i]
            current_week = week_list[i + 1]
            period_data = style_df[(style_df.index > pre_week) & (style_df.index <= current_week)]
            if period_data.shape[0] < 4:
                continue
            period_ret = (1 + period_data).prod() - 1
            # period_ret = period_data.sum()
            period_ret = period_ret.to_frame(current_week).T
            factor_return.append(period_ret)

        factor_return = pd.concat(factor_return)
        factor_df = pd.merge(factor_return, self.alpha_series.to_frame('alpha'), left_index=True, right_index=True)

        # group_alpha = group_test(factor_df, 'momentum', 'alpha')

        name_list = ['size', 'btop', 'earnyield', 'leverage']
        group_list = []
        for name in name_list:
            group_alpha = group_test(factor_df, name, 'alpha').to_frame(name)
            group_list.append(group_alpha)

        group_df = pd.concat(group_list, axis=1)

        return group_df

    def run_factor_vol(self):
        week_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")
        style_df = self.get_style_factor(self.start_date, self.end_date)

        factor_vol = []

        for i in range(len(week_list) - 1):
            pre_week = week_list[i]
            current_week = week_list[i + 1]
            period_data = style_df[(style_df.index > pre_week) & (style_df.index <= current_week)]
            if period_data.shape[0] < 4:
                continue
            # period_data = style_df[style_df.index <= current_week][-10:]
            rolling_vol = period_data.std().to_frame(current_week).T
            factor_vol.append(rolling_vol)

        factor_vol = pd.concat(factor_vol)
        factor_df = pd.merge(factor_vol, self.alpha_series.to_frame('alpha'), left_index=True, right_index=True)
        # a = factor_df.corr('spearman')['alpha']

        # group_alpha = group_test(factor_df, 'momentum', 'alpha')

        name_list = ['earnyield', 'resvol', 'growth']
        group_list = []
        for name in name_list:
            group_alpha = group_test(factor_df, name, 'alpha').to_frame(name)
            group_list.append(group_alpha)

        group_df = pd.concat(group_list, axis=1)

        return group_df


class IndustryFactor:
    def __init__(self, start_date, end_date, alpha):
        self.start_date = start_date
        self.end_date = end_date
        self.alpha_series = alpha

    @staticmethod
    def get_mkt_info(start_date, end_date):
        path = r'D:\kevin\risk_model_jy\RiskModel\data\common_data\chg_pct'
        listdir = os.listdir(path)
        listdir = [x for x in listdir if start_date < x.split('.')[0] <= end_date]
        data = []
        for filename in listdir:
            date_t_rate = pd.read_csv(os.path.join(path, filename), dtype={"tradeDate": str})
            date_t_rate['ticker'] = date_t_rate['ticker'].apply(lambda x: str(x).zfill(6))
            data.append(date_t_rate)

        data = pd.concat(data)
        # filter
        data = data[(data['dailyReturnReinv'] >= -0.2) & (data['dailyReturnReinv'] <= 0.2)]
        data = pd.pivot_table(data, index='tradeDate', columns='ticker', values='dailyReturnReinv').sort_index()
        data = data.dropna(how='any', axis=1)

        return data

    @staticmethod
    def get_benchmark_weight(date):
        sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and " \
                     "SecuCode in ('000300', '000905', '000852')"
        res = hbs.db_data_query('readonly', sql_script)
        index_info = pd.DataFrame(res['data'])
        inner_code_series = index_info.set_index('SECUCODE')['INNERCODE']

        weight = []
        for benchmark_id in ['000905']:
            inner_code = inner_code_series.loc[benchmark_id]
            sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                         "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                         "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
            data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
            weight_df = data.rename(
                columns={"SECUCODE": "ticker", "ENDDATE": "effDate", "WEIGHT": "weight"})
            weight_df['benchmark_id'] = benchmark_id
            weight.append(weight_df[['ticker', 'benchmark_id', 'weight']])

        return pd.concat(weight)

    @staticmethod
    def get_industry_class(trade_date):
        path = r'D:\kevin\risk_model_jy\RiskModel\data'
        data = pd.read_json(os.path.join(path, r'common_data/sw_new.json'), dtype={'ticker': str})

        data['outDate'] = data['outDate'].fillna(20991231)
        data['intoDate'] = data['intoDate'].map(int).map(str)
        data['outDate'] = data['outDate'].map(int).map(str)

        data = data[(data['intoDate'] <= trade_date) & (data['outDate'] >= trade_date)].drop_duplicates(subset='ticker')

        return data.set_index('ticker')['industryName1']

    def run(self):
        week_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")
        factor_df = pd.DataFrame(
            index=week_list, columns=['ind_diff_mean', 'ind_diff_med', 'weighted_diff'])

        from tqdm import tqdm
        for i in tqdm(range(len(week_list) - 1)):
            pre_week = week_list[i]
            current_week = week_list[i + 1]
            period_data = self.get_mkt_info(pre_week, current_week)
            if period_data.shape[0] < 4:
                continue
            pre_date = get_shift_date(current_week)
            bm_weight = self.get_benchmark_weight(pre_date)
            industry_class = self.get_industry_class(current_week)
            period_ret = ((1 + period_data).prod() - 1).to_frame('ret')
            df = period_ret.merge(bm_weight.set_index('ticker')[['benchmark_id']],
                                  left_index=True, right_index=True, how='left').fillna('other')
            df = pd.merge(df, industry_class.to_frame('industry'), left_index=True, right_index=True)

            ind_ret = df.groupby(['benchmark_id', 'industry'])['ret'].mean().reset_index()
            ind_ret = pd.pivot_table(ind_ret, index='industry', columns='benchmark_id', values='ret').sort_index()

            bm_df = bm_weight.set_index('ticker')[['weight']].merge(industry_class, left_index=True, right_index=True)
            bm_df = bm_df.groupby('industryName1')['weight'].sum().to_frame('weight') / 100.

            ind_ret = pd.merge(ind_ret, bm_df, left_index=True, right_index=True)
            ind_ret['diff'] = ind_ret['other'] - ind_ret['000905']

            factor_df.loc[current_week, 'ind_diff_mean'] = ind_ret['diff'].mean()
            factor_df.loc[current_week, 'ind_diff_med'] = ind_ret['diff'].median()
            factor_df.loc[current_week, 'weighted_diff'] = (ind_ret['diff'] * ind_ret['weight']).sum()

        factor_df = factor_df.dropna()
        factor_df = pd.merge(factor_df, self.alpha_series.to_frame('alpha'), left_index=True, right_index=True)
        # a = factor_df.astype(float).corr('spearman')['alpha']

        # group_alpha = group_test(factor_df, 'momentum', 'alpha')

        name_list = ['ind_diff_mean', 'ind_diff_med', 'weighted_diff']
        group_list = []
        for name in name_list:
            group_alpha = group_test(factor_df, name, 'alpha').to_frame(name)
            group_list.append(group_alpha)

        group_df = pd.concat(group_list, axis=1)

        return group_df


def summary_analysis(alpha):
    data = pd.read_excel(
        'D:\\研究基地\\G-专题报告\\量化超额市场微观环境分析\\数据相关.xlsx', dtype={"trade_date": str}, sheet_name=1)
    data = data.set_index('trade_date')
    data = pd.merge(data, alpha.to_frame('alpha'), left_index=True, right_index=True)
    corr = data.corr('spearman')

    fig = ff.create_annotated_heatmap(
        z=corr.to_numpy().round(3),
        x=list(corr.index.values),
        y=list(corr.columns.values),
        xgap=3, ygap=3,
        zmin=-1, zmax=1,
        colorscale='earth',
        colorbar_thickness=30,
        colorbar_ticklen=3,
    )
    fig.update_layout(title_text='<b>Correlation Matrix (cont. features)<b>',
                      title_x=0.5,
                      titlefont={'size': 24},
                      width=1000, height=800,
                      xaxis_showgrid=False,
                      xaxis={'side': 'bottom'},
                      yaxis_showgrid=False,
                      yaxis_autorange='reversed',
                      paper_bgcolor=None,
                      )
    plot_ly(fig, filename="D:\\123.html", auto_open=False)


class AlphaMonitorWeekly:
    """
    周度版本的超额观测框架
    """
    def __init__(self, trade_date, is_increment=1):
        self.trade_date = trade_date
        self.is_increment = is_increment
        self._load_pre_week()

    def _load_pre_week(self):
        trade_dt = datetime.datetime.strptime(self.trade_date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=20)).strftime('%Y%m%d')
        week_list = get_trading_day_list(pre_date, self.trade_date, frequency="week")
        self.pre_week = week_list[-2]

    def calculate_liq_factor(self):
        """
        tr = tr_1000 - tr_500
        """
        trading_day_list = get_trading_day_list(self.pre_week, self.trade_date)[1:]
        liq_ratio = pd.DataFrame(index=trading_day_list, columns=['tr'])
        tr_list = []
        for trading_day in trading_day_list:
            sql_script = "SELECT SYMBOL, SNAME, VOTURNOVER, PCHG FROM finchina.CHDQUOTE WHERE" \
                         " TDATE = {}".format(trading_day)
            data = pd.DataFrame(hbs.db_data_query('readonly', sql_script, page_size=5000)['data'])
            data = data[data['SYMBOL'].str[0].isin(['0', '3', '6'])]
            data = data[data['VOTURNOVER'] > 1e-8]
            # data = data[~data['SNAME'].str.contains('ST')]
            # data = data[~data['SNAME'].str.contains('N')]
            # data = data[~data['SNAME'].str.contains('C')]
            data = data.rename(columns={"SYMBOL": "ticker", "VOTURNOVER": "trade_volume"})[
                ['ticker', 'trade_volume']].dropna()
            pre_date = get_shift_date(self.trade_date)
            bm_components = get_benchmark_components(pre_date)
            data = pd.merge(data, bm_components, on='ticker', how='left')
            data['benchmark_id'] = data['benchmark_id'].fillna('other')

            path = r'D:\kevin\risk_model_jy\RiskModel\data'
            date_t_rate = pd.read_json(os.path.join(path, 'common_data/turnover_rate/{0}.json'.format(trading_day)),
                                       typ='series').to_frame('turnover_rate')
            date_t_rate.index.name = 'ticker'
            date_t_rate = date_t_rate.reset_index()
            date_t_rate['ticker'] = date_t_rate['ticker'].apply(lambda x: str(x).zfill(6))
            data = pd.merge(data, date_t_rate, on='ticker')
            data['equity'] = data['trade_volume'] / data['turnover_rate']

            tmp = data.groupby('benchmark_id')['trade_volume'].sum() / data['trade_volume'].sum()
            tr_list.append(tmp.to_frame(trading_day))
            liq_ratio.loc[trading_day, 'tr'] = tmp.loc['000852'] - tmp.loc['000905']

        tr_df = pd.concat(tr_list, axis=1).T.sort_index()
        tr_df['trade_date'] = tr_df.index
        tr_df.rename(columns={"000300": "hs300", "000905": "zz500", "000852": "zz1000"}, inplace=True)
        tr_df.reset_index(drop=True, inplace=True)
        # save
        # sql_script = """
        #     create table am_liq_ratio(
        #     id int auto_increment primary key,
        #     trade_date date not null,
        #     hs300 decimal(6, 4),
        #     zz500 decimal(6, 4),
        #     zz1000 decimal(6, 4),
        #     other decimal(6, 4))
        # """
        # create_table('am_liq_ratio', sql_script)
        table_name = 'am_liq_ratio'
        sql_script = "delete from {} where trade_date in ({})".format(
            table_name, ','.join(tr_df['trade_date'].tolist()))
        # delete first
        delete_duplicate_records(sql_script)
        # add new records
        WriteToDB().write_to_db(tr_df, table_name)

        return liq_ratio['tr'].mean()

    def calculate_divergence_factor(self):
        """
        cs_vol_scap
        """
        period_data = get_mkt_info(self.pre_week, self.trade_date)
        pre_date = get_shift_date(self.trade_date)
        bm_components = get_benchmark_components(pre_date)
        universe = bm_components[bm_components['benchmark_id'].isin(['000300', '000905'])]['ticker'].tolist()
        idx = set(period_data.columns.tolist()) - set(universe)
        stock_return = (1 + period_data[idx]).prod() - 1

        return stock_return.std()

    def calculate_spread_factor(self):
        """
        1、win_ratio
        2、spread = win_spread - lose_spread
        3、weighted_spread = win_ratio * win_spread – (1 – win_ratio) * lose_spread
        """
        period_data = get_mkt_info(self.pre_week, self.trade_date)
        pre_date = get_shift_date(self.trade_date)
        bm_components = get_benchmark_components(pre_date)
        universe = bm_components['ticker'].tolist()
        idx = set(period_data.columns.tolist()) - set(universe)
        stock_return = (1 + period_data[idx]).prod() - 1
        # index_return
        sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format('000905', self.pre_week, self.trade_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        data['index_return'] = data['TCLOSE'].pct_change()
        index_return = data.set_index('TRADEDATE')['index_return']
        index_return = (1 + index_return.loc[period_data.index]).prod() - 1
        # calculate
        win_ratio = 100 - stats.percentileofscore(np.array(stock_return), index_return)
        win_spread = stock_return[stock_return >= index_return].median() - index_return
        lose_spread = index_return - stock_return[stock_return < index_return].median()
        combine_factor = win_ratio * win_spread - (100 - win_ratio) * lose_spread
        # save
        week_ret = stock_return.to_frame('week_ret').reset_index()
        week_ret['trade_date'] = self.trade_date
        # sql_script = """
        #     create table am_week_ret(
        #     id int auto_increment primary key,
        #     trade_date date not null,
        #     ticker varchar(10),
        #     week_ret decimal(6, 4))
        # """
        # create_table('am_week_ret', sql_script)
        table_name = 'am_week_ret'
        sql_script = "delete from {} where trade_date in ({})".format(
            table_name, ','.join(week_ret['trade_date'].tolist()))
        # delete first
        delete_duplicate_records(sql_script)
        # add new records
        WriteToDB().write_to_db(week_ret, table_name)

        return win_ratio, win_spread - lose_spread, combine_factor

    def calculate_style_factor(self):
        """
        风格因子收益率
        (+): Momentum、Beta、Growth
        (-): Size、Earnyield
        """
        sql_script = "SELECT * FROM factor_return where trade_date > {} and trade_date <= {}".format(
            self.pre_week, self.trade_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        data = pd.pivot_table(data, index='trade_date', columns='factor_name', values='factor_ret').sort_index()
        factor_return = ((1 + data).prod() - 1) * 100.

        return factor_return.loc[['momentum', 'beta', 'growth', 'size', 'earnyield']]

    def calculate_ind_factor(self):
        period_data = get_mkt_info(self.pre_week, self.trade_date)
        pre_date = get_shift_date(self.trade_date)
        bm_weight = get_benchmark_weight(pre_date)
        industry_class = get_industry_class(self.trade_date)
        period_ret = ((1 + period_data).prod() - 1).to_frame('ret')
        df = period_ret.merge(bm_weight.set_index('ticker')[['benchmark_id']],
                              left_index=True, right_index=True, how='left').fillna('other')
        df = pd.merge(df, industry_class.to_frame('industry'), left_index=True, right_index=True)

        ind_ret = df.groupby(['benchmark_id', 'industry'])['ret'].mean().reset_index()
        ind_ret = pd.pivot_table(ind_ret, index='industry', columns='benchmark_id', values='ret').sort_index()

        bm_df = bm_weight.set_index('ticker')[['weight']].merge(industry_class, left_index=True, right_index=True)
        bm_df = bm_df.groupby('industryName1')['weight'].sum().to_frame('weight') / 100.

        ind_ret = pd.merge(ind_ret, bm_df, left_index=True, right_index=True)
        ind_ret['diff'] = ind_ret['other'] - ind_ret['000905']
        # save
        data = ind_ret.reset_index().rename(columns={"000905": "bm_in", "other": "bm_out"})
        data = data[['industry', 'bm_in', 'bm_out', 'weight']]
        data['trade_date'] = self.trade_date
        # sql_script = """
        #     create table am_ind_ret(
        #     id int auto_increment primary key,
        #     trade_date date not null,
        #     industry varchar(20),
        #     bm_in decimal(6, 4),
        #     bm_out decimal(6, 4),
        #     weight decimal(6, 4))
        # """
        # create_table('am_ind_ret', sql_script)
        table_name = 'am_ind_ret'
        sql_script = "delete from {} where trade_date in ({})".format(
            table_name, ','.join(data['trade_date'].tolist()))
        # delete first
        delete_duplicate_records(sql_script)
        # add new records
        WriteToDB().write_to_db(data, table_name)

        return (ind_ret['diff'] * ind_ret['weight']).sum()

    def calculate_summary(self):
        factor_list = ['tr', 'cs_vol_scap', 'win_ratio', 'spread', 'weighted_spread',
                       'momentum', 'beta', 'growth', 'size', 'earnyield', 'weighted_diff']
        factor_df = pd.DataFrame(index=[self.trade_date], columns=factor_list)

        factor_df.loc[self.trade_date, 'tr'] = self.calculate_liq_factor()
        factor_df.loc[self.trade_date, 'cs_vol_scap'] = self.calculate_divergence_factor()
        factor_df.loc[self.trade_date, ['win_ratio', 'spread', 'weighted_spread']] = self.calculate_spread_factor()
        factor_df.loc[self.trade_date, ['momentum', 'beta', 'growth', 'size', 'earnyield']] = \
            self.calculate_style_factor().tolist()
        factor_df.loc[self.trade_date, 'weighted_diff'] = self.calculate_ind_factor()

        factor_df['trade_date'] = factor_df.index
        factor_df = factor_df[['trade_date'] + factor_list].reset_index(drop=True)

        return factor_df

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.calculate_summary()
            sql_script = "delete from alpha_monitor where trade_date in ({})".format(
                ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, 'alpha_monitor')
        else:
            sql_script = """
                create table alpha_monitor(
                id int auto_increment primary key,
                trade_date date not null,
                tr decimal(6, 4),
                cs_vol_scap decimal(6, 4),
                win_ratio decimal(6, 2),
                spread decimal(6, 4),
                weighted_spread decimal(6, 4),
                momentum decimal(6, 4),
                beta decimal(6, 4),
                growth decimal(6, 4),
                size decimal(6, 4),
                earnyield decimal(6, 4),
                weighted_diff decimal(6, 4)) 
            """
            create_table('alpha_monitor', sql_script)
            data = pd.read_excel(
                'D:\\研究基地\\G-专题报告\\量化超额市场微观环境分析\\数据相关.xlsx', dtype={"trade_date": str}, sheet_name=1)
            # data = self.calculate_summary()
            WriteToDB().write_to_db(data, 'alpha_monitor')


class AlphaEnvPlot:
    def __init__(self, trade_date):
        self.trade_date = trade_date
        self._load_pre_week()

    def _load_pre_week(self):
        trade_dt = datetime.datetime.strptime(self.trade_date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=20)).strftime('%Y%m%d')
        week_list = get_trading_day_list(pre_date, self.trade_date, frequency="week")
        self.pre_week = week_list[-2]

    @staticmethod
    def plotly_area(df, title_text, figsize=(1200, 600)):
        fig_width, fig_height = figsize
        names = df.columns.tolist()

        data = []
        for name in names:
            tmp = go.Scatter(
                x=df.index,
                y=df[name],
                name=name,
                mode='lines',
                line=dict(width=0.5),
                fill='tonexty',
                stackgroup='one')
            data.append(tmp)

        layout = go.Layout(
            title=title_text,
            autosize=False,
            title_text='<b>{}<b>'.format(title_text),
            title_x=0.5,
            titlefont={'size': 24},
            width=fig_width,
            height=fig_height,
            showlegend=True,
            xaxis=dict(type='category'),
            yaxis=dict(
                type='linear',
                range=[1, 100],
                dtick=20,
                ticksuffix='%'))

        # fig = go.Figure(data=data, layout=layout)
        # plot_ly(fig, filename="D:\\123.html", auto_open=False)
        plot_render({"data": data, "layout": layout})

    @staticmethod
    def plotly_bins(df, index_return):
        market_df = df.copy()
        win_ratio = round(100 - stats.percentileofscore(np.array(market_df['return']), index_return), 1)
        win_med = market_df[market_df['return'] >= index_return]['return'].median()
        lose_med = market_df[market_df['return'] < index_return]['return'].median()

        market_df = market_df[market_df['return'].abs() <= 20.]
        interval_range = pd.interval_range(-20, 20, 100, closed='left')
        count_df = pd.cut(market_df['return'], bins=interval_range).value_counts().sort_index().to_frame('num')
        count_df['num_cumsum'] = count_df['num'].cumsum()
        count_df['start'] = count_df.index
        count_df['start'] = count_df['start'].apply(lambda x: round(x.left, 1))
        count_df['color'] = '#55CBF2'
        # locate the index return
        lower = round(np.floor(index_return / 0.4) * 0.4, 2)
        count_df.loc[count_df['start'] == lower, 'color'] = '#ff2d51'
        # locate the lower med
        lower = round(np.floor(lose_med / 0.4) * 0.4, 2)
        count_df.loc[count_df['start'] == lower, 'color'] = '#ffa400'
        # # locate the upper med
        lower = round(np.floor(win_med / 0.4) * 0.4, 2)
        count_df.loc[count_df['start'] == lower, 'color'] = '#ffa400'

        color_list = count_df[count_df['num_cumsum'] > 0]['color'].tolist()

        title_text = "当周中证500收益率{}%, 在1800以外的股票域中,跑赢指数的比例为{}%, 跑赢的个股收益中位数为{}%, 跑输的中位数为{}%".format(
            round(index_return, 2), win_ratio, round(win_med, 2), round(lose_med, 2))

        L = go.Layout(xaxis=dict(range=[-20, 20]), title=title_text, width=1200, height=600)
        D = go.Histogram(x=np.array(market_df['return']), xbins=dict(start=-20, end=20, size=0.4),
                         histfunc='count', histnorm='probability',
                         marker=dict(color=color_list, line=dict(color='white', width=1)))

        # F = go.Figure(data=[D], layout=L)
        # plot_ly(F, filename='D:\\456.html', auto_open=False)
        plot_render({"data": D, "layout": L})

    @staticmethod
    def plotly_line(df, title_text, figsize=(1200, 600)):
        fig_width, fig_height = figsize
        data = []
        for col in df.columns:
            trace = go.Scatter(
                x=df.index.tolist(),
                y=df[col],
                name=col,
                mode="lines+markers",
                line=dict(
                    shape='spline'
                )
            )
            data.append(trace)

        tick_vals = df.index.tolist()[::5]

        layout = go.Layout(
            title_text='<b>{}<b>'.format(title_text),
            title_x=0.5,
            titlefont={'size': 24},
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), tickformat=',.2%', showgrid=True),
            xaxis=dict(showgrid=True, tickvals=tick_vals),
            template='plotly_white'
        )

        # figure = go.Figure(data=data, layout=layout)
        # plot_ly(figure, filename='D:\\789.html', auto_open=False)
        plot_render({"data": data, "layout": layout})

    @staticmethod
    def plotly_style_bar(df, title_text, figsize=(1200, 600), legend_x=0.35):
        fig_width, fig_height = figsize
        cols = df.columns.tolist()
        # color_list = ['rgb(49, 130, 189)', 'rgb(204, 204, 204)', 'rgb(216, 0, 18)']
        color_list = ['rgb(49, 130, 189)', 'rgb(204, 204, 204)']
        data = []
        for i in range(len(cols)):
            col = cols[i]
            trace = go.Bar(
                x=df.index.tolist(),
                y=df[col],
                name=col,
                marker=dict(color=color_list[i])
            )
            data.append(trace)

        layout = go.Layout(
            title_text='<b>{}<b>'.format(title_text),
            title_x=0.5,
            titlefont={'size': 24},
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), tickformat=',.2%', showgrid=True),
            xaxis=dict(showgrid=True, tickangle=-30),
            legend=dict(orientation="h", x=legend_x),
            template='plotly_white'
        )

        # fig = go.Figure(data=data, layout=layout)
        # plot_ly(fig, filename='D:\\222.html', auto_open=False)
        plot_render({"data": data, "layout": layout})

    def run(self):
        engine = create_engine(engine_params)
        # liquidity
        sql_script = "SELECT * FROM am_liq_ratio where trade_date > {} and trade_date <= {}".format(
            self.pre_week, self.trade_date)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        liq_data = data.set_index('trade_date')[['hs300', 'zz500', 'zz1000', 'other']] * 100
        liq_data.rename(
            columns={"hs300": "沪深300", "zz500": "中证500", "zz1000": "中证1000", "other": "剩余小票"}, inplace=True)
        self.plotly_area(liq_data, "本周市场流动性分布")

        # market_spread
        sql_script = "SELECT * FROM am_week_ret where trade_date = {}".format(self.trade_date)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        market_df = data.copy()
        market_df['return'] = 100 * market_df['week_ret']
        # index_return
        sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format('000905', self.pre_week, self.trade_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        data['index_return'] = data['TCLOSE'].pct_change()
        index_return = 100. * ((1 + data.set_index('TRADEDATE')['index_return'].dropna()).prod() - 1)
        self.plotly_bins(market_df, index_return)

        # style_factor
        trade_dt = datetime.datetime.strptime(self.trade_date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=50)).strftime('%Y%m%d')
        sql_script = "SELECT * FROM factor_return where trade_date > {} and trade_date <= {}".format(
            pre_date, self.trade_date)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        factor_return = pd.pivot_table(
            data, index='trade_date', columns='factor_name', values='factor_ret').sort_index()[-20:]
        factor_return = factor_return[['momentum', 'beta', 'growth', 'size', 'earnyield']].cumsum()
        self.plotly_line(factor_return, "风格因子走势")

        # industry_factor
        sql_script = "SELECT * FROM am_ind_ret where trade_date = {}".format(self.trade_date)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        data = data.set_index('industry')[['bm_in', 'bm_out', 'weight']]
        data['ret_diff'] = data['bm_out'] - data['bm_in']
        data = data.rename(
            columns={"ret_diff": "成分股内外差值(外-内)", "weight": "基准权重"})[['成分股内外差值(外-内)', '基准权重']]
        data = data.sort_values(by='基准权重')
        self.plotly_style_bar(data, "成分内外行业收益统计")

    def quantile_plot(self):
        engine = create_engine(engine_params)
        sql_script = "SELECT * FROM alpha_monitor"
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        del data['id']
        data = data.set_index('trade_date').sort_index()
        data = data[data.index <= self.trade_date]

        percent_df = data.apply(lambda x: stats.percentileofscore(np.array(x), x.loc[self.trade_date]))
        percent_df = percent_df.to_frame('当期所处历史分位数水平').round(1)
        # 方向调整
        percent_df.loc['size'] = 100 - percent_df.loc['size']
        percent_df.loc['earnyield'] = 100 - percent_df.loc['earnyield']
        percent_df = percent_df.reindex(['weighted_diff', 'earnyield', 'size', 'growth', 'beta', 'momentum', 'spread',
                                         'win_ratio', 'cs_vol_scap', 'tr'])
        percent_df['因子'] = percent_df.index
        percent_df = percent_df.reset_index(drop=True)

        fig = px.bar(
            percent_df,
            y="因子",
            x="当期所处历史分位数水平",
            text='当期所处历史分位数水平',
            orientation='h'
        )

        fig.update_layout(title_text='<b>Factor Quantile: {}<b>'.format(self.trade_date),
                          title_x=0.5,
                          titlefont={'size': 24},
                          width=1200, height=600,
                          xaxis=dict(tickfont=dict(size=12), showgrid=True),
                          yaxis=dict(tickfont=dict(size=16))
                          )

        # plot_ly(fig, filename='D:\\456.html', auto_open=False)
        plot_render({"data": fig.data, "layout": fig.layout})


if __name__ == '__main__':
    # 超额收益Y
    fund_data = pd.read_excel('D:\\研究基地\\G-专题报告\\量化超额市场微观环境分析\\数据相关.xlsx', sheet_name=0)
    alpha_series = AlphaSeries('20181228', '20220422', fund_data).calculate()

    # 流动性因子
    # start_date = '20190101'
    # end_date = '20220422'
    # trading_day_list = get_trading_day_list(start_date, end_date)
    # from tqdm import tqdm
    # for trading_day in tqdm(trading_day_list):
    #     MarketLiquidity(trading_day).run()
    # results = LiquidityTest('20181228', '20220422', alpha_series).run()
    # 个股分化度因子
    # StockDivergence('20181228', '20220422', alpha_series).run()
    # 胜率因子
    # MarketSpread('20181228', '20220422', alpha_series).run()
    # 风格因子
    # StyleFactor('20181228', '20220422', alpha_series).run_factor_return()
    # 行业因子
    # IndustryFactor('20181228', '20220422', alpha_series).run()

    # summary_analysis(alpha_series)

    # main class
    # AlphaMonitorWeekly('20220520', is_increment=1).get_construct_result()

    AlphaEnvPlot('20220520').quantile_plot()
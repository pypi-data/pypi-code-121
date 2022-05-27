# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from hbshare.fe.xwq.analysis.utils.const_var import TimeDateFormat
from hbshare.fe.xwq.analysis.utils.timedelta_utils import TimeDateUtil
import numpy as np
import pandas as pd


def get_cal_and_trade_cal(start, end):
    """
    获取交易日期
    """
    cal = HBDB().read_cal(start, end)
    cal = cal.rename(columns={'JYRQ': 'TRADE_DATE', 'SFJJ': 'IS_OPEN', 'SFZM': 'IS_WEEK_END', 'SFYM': 'IS_MONTH_END'})
    cal['IS_OPEN'] = cal['IS_OPEN'].astype(int).replace({0: 1, 1: 0})
    cal['IS_WEEK_END'] = cal['IS_WEEK_END'].fillna(0).astype(int)
    cal['IS_MONTH_END'] = cal['IS_MONTH_END'].fillna(0).astype(int)
    cal = cal.sort_values('TRADE_DATE')
    trade_cal = cal[cal['IS_OPEN'] == 1]
    trade_cal['RECENT_TRADE_DATE'] = trade_cal['TRADE_DATE']
    trade_cal['PREV_TRADE_DATE'] = trade_cal['TRADE_DATE'].shift(1)
    trade_cal = trade_cal[['TRADE_DATE', 'RECENT_TRADE_DATE', 'PREV_TRADE_DATE', 'IS_OPEN', 'IS_WEEK_END', 'IS_MONTH_END']]
    cal = cal.merge(trade_cal[['TRADE_DATE', 'RECENT_TRADE_DATE']], on=['TRADE_DATE'], how='left')
    cal['RECENT_TRADE_DATE'] = cal['RECENT_TRADE_DATE'].fillna(method='ffill')
    cal = cal.merge(trade_cal[['TRADE_DATE', 'PREV_TRADE_DATE']], on=['TRADE_DATE'], how='left')
    cal['PREV_TRADE_DATE'] = cal['PREV_TRADE_DATE'].fillna(method='bfill')
    cal = cal[['TRADE_DATE', 'RECENT_TRADE_DATE', 'PREV_TRADE_DATE', 'IS_OPEN', 'IS_WEEK_END', 'IS_MONTH_END']]
    return cal, trade_cal

def fund_info(date):
    """
    研究对象
    """
    # 正常运行中的普通股票型、偏股混合型、灵活配置型公募基金
    fund = HBDB().read_stock_fund_info()
    fund = fund.rename(columns={'jjdm': 'FUND_CODE', 'jjmc': 'FUND_FULL_NAME', 'jjjc': 'FUND_SHORT_NAME',
                                'clrq': 'BEGIN_DATE', 'zzrq': 'END_DATE', 'ejfl': 'FUND_TYPE', 'kffb': 'OPEN_CLOSE'})
    # 成立距计算日期满1.5年
    date_before = TimeDateUtil.get_previous_date_str(date, TimeDateFormat.YMD.value, TimeDateFormat.YMD.value, 560)
    fund['BEGIN_DATE'] = fund['BEGIN_DATE'].astype(str)
    fund = fund[fund['BEGIN_DATE'] <= date_before]
    fund = fund.sort_values(['FUND_FULL_NAME', 'FUND_CODE']).drop_duplicates('FUND_FULL_NAME')
    # 成立以来股票占基金净资产的比例均值大于60%
    fund_gptzzjb = HBDB().read_fund_gptzzjb_given_codes(fund['FUND_CODE'].unique().tolist())
    fund_gptzzjb = fund_gptzzjb.rename(columns={'jjdm': 'FUND_CODE', 'jsrq': 'REPORT_DATE', 'gptzzjb': 'EQUITY_IN_NA'})
    fund_gptzzjb['REPORT_DATE'] = fund_gptzzjb['REPORT_DATE'].astype(str)
    fund_gptzzjb_mean = fund_gptzzjb[['FUND_CODE', 'EQUITY_IN_NA']].groupby('FUND_CODE').mean().reset_index()
    fund_gptzzjb_mean = fund_gptzzjb_mean[fund_gptzzjb_mean['EQUITY_IN_NA'] > 60]
    fund = fund[fund['FUND_CODE'].isin(fund_gptzzjb_mean['FUND_CODE'].unique().tolist())]
    # 近1.5年以来股票占基金净资产的比例均大于50
    fund_gptzzjb = fund_gptzzjb[(fund_gptzzjb['REPORT_DATE'] >= date_before) & (fund_gptzzjb['REPORT_DATE'] <= date)]
    fund_gptzzjb_min = fund_gptzzjb[['FUND_CODE', 'EQUITY_IN_NA']].groupby('FUND_CODE').min().reset_index()
    fund_gptzzjb_min = fund_gptzzjb_min[fund_gptzzjb_min['EQUITY_IN_NA'] > 50]
    fund = fund[fund['FUND_CODE'].isin(fund_gptzzjb_min['FUND_CODE'].unique().tolist())]
    total = len(fund)
    # todo: kffb字段nan值的处理
    fund['OPEN_CLOSE'] = fund['OPEN_CLOSE'].fillna('0')
    fund_overview = pd.DataFrame(index=['普通股票型基金', '偏股混合型基金', '灵活配置型基金'], columns=['开放式基金', '封闭式基金'])
    fund_overview.loc['普通股票型基金', '开放式基金'] = len(fund[(fund['FUND_TYPE'] == '13') & (fund['OPEN_CLOSE'] == '0')])
    fund_overview.loc['普通股票型基金', '封闭式基金'] = len(fund[(fund['FUND_TYPE'] == '13') & (fund['OPEN_CLOSE'] == '1')])
    fund_overview.loc['偏股混合型基金', '开放式基金'] = len(fund[(fund['FUND_TYPE'] == '37') & (fund['OPEN_CLOSE'] == '0')])
    fund_overview.loc['偏股混合型基金', '封闭式基金'] = len(fund[(fund['FUND_TYPE'] == '37') & (fund['OPEN_CLOSE'] == '1')])
    fund_overview.loc['灵活配置型基金', '开放式基金'] = len(fund[(fund['FUND_TYPE'] == '35') & (fund['OPEN_CLOSE'] == '0')])
    fund_overview.loc['灵活配置型基金', '封闭式基金'] = len(fund[(fund['FUND_TYPE'] == '35') & (fund['OPEN_CLOSE'] == '1')])
    return fund, total, fund_overview

def preload_stock_valuation(dates):
    """
    获取股票估值数据
    """
    stock_valuation_list = []
    star_stock_valuation_list = []
    for date in dates:
        print(date)
        stock_valuation_date = HBDB().read_stock_valuation_given_date(date)
        stock_valuation_list.append(stock_valuation_date)
        star_stock_valuation_date = HBDB().read_star_stock_valuation_given_date(date)
        star_stock_valuation_list.append(star_stock_valuation_date)
    stock_valuation = pd.concat(stock_valuation_list)
    stock_valuation.to_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/stock_valuation.hdf', key='table', mode='w')
    star_stock_valuation = pd.concat(star_stock_valuation_list)
    star_stock_valuation.to_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/star_stock_valuation.hdf', key='table', mode='w')
    return

def preload_index_cons():
    """
    获取指数成分股数据
    """
    index_dic = {
        'HS300': '3145',
        'ZZ500': '4978',
        'ZZ1000': '39144',
        'ZZ100': '4293',
        'SZ50': '46',
        'SZ100': '16898',
        'SZ180': '30',
        'JCDP': '3472',
        'JCZP': '3473',
        'JCXP': '3474',
        'JCDPJZ': '10055',
        'JCDPCZ': '10054',
        'JCZPJZ': '10057',
        'JCZPCZ': '10056',
        'JCXPJZ': '10059',
        'JCXPCZ': '10058',
    }
    index_cons_list = []
    for index in index_dic.keys():
        print(index)
        index_cons = HBDB().read_index_cons(index_dic[index])
        index_cons['INDEX'] = index
        index_cons_list.append(index_cons)
    index_cons = pd.concat(index_cons_list)
    index_cons.to_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/index_cons.hdf', key='table', mode='w')
    return


def fund_valuation(date, fund_zc_holding, fund_zc_holding_diff):
    """
    估值分析
    """
    total_zcmv = fund_zc_holding[['FUND_CODE', 'REPORT_DATE', 'MV_IN_NA']].groupby(['FUND_CODE', 'REPORT_DATE']).sum().reset_index()
    total_zcmv = total_zcmv[['REPORT_DATE', 'MV_IN_NA']].groupby(['REPORT_DATE']).mean().reset_index()
    # 交易日期
    # cal, trade_cal = get_cal_and_trade_cal('19000101', date)
    # cal.to_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/cal.hdf', key='table', mode='w')
    # trade_cal.to_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/trade_cal.hdf', key='table', mode='w')
    cal = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/cal.hdf', key='table')
    trade_cal = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/trade_cal.hdf', key='table')
    fund_zc_holding = fund_zc_holding.merge(cal[['TRADE_DATE', 'RECENT_TRADE_DATE']].rename(columns={'TRADE_DATE': 'REPORT_DATE'}), on=['REPORT_DATE'], how='left')
    fund_zc_holding_diff = fund_zc_holding_diff.merge(cal[['TRADE_DATE', 'RECENT_TRADE_DATE']].rename(columns={'TRADE_DATE': 'REPORT_DATE'}), on=['REPORT_DATE'], how='left')
    # todo: 港股估值数据暂时取不到
    # preload_stock_valuation(fund_zc_holding['RECENT_TRADE_DATE'].unique().tolist())
    stock_valuation = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/stock_valuation.hdf', key='table')
    star_stock_valuation = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/star_stock_valuation.hdf', key='table')
    stock_valuation = stock_valuation.rename(columns={'SECUCODE': 'TICKER_SYMBOL', 'TRADINGDAY': 'TRADE_DATE', 'TOTALMV': 'MARKET_VALUE', 'PE': 'PE(TTM)', 'PB': 'PB(LF)'})
    star_stock_valuation = star_stock_valuation.rename(columns={'SECUCODE': 'TICKER_SYMBOL', 'TRADINGDAY': 'TRADE_DATE', 'TOTALMV': 'MARKET_VALUE', 'PE': 'PE(TTM)', 'PB': 'PB(LF)'})
    stock_valuation = stock_valuation[['TRADE_DATE', 'TICKER_SYMBOL', 'MARKET_VALUE', 'PE(TTM)', 'PB(LF)']]
    star_stock_valuation = star_stock_valuation[['TRADE_DATE', 'TICKER_SYMBOL', 'MARKET_VALUE', 'PE(TTM)', 'PB(LF)']]
    stock_valuation = pd.concat([stock_valuation, star_stock_valuation]).sort_values(['TRADE_DATE', 'TICKER_SYMBOL'])
    fund_zc_holding = fund_zc_holding.merge(stock_valuation.rename(columns={'TRADE_DATE': 'RECENT_TRADE_DATE'}), on=['RECENT_TRADE_DATE', 'TICKER_SYMBOL'], how='left')
    pe_zc = fund_zc_holding.dropna(subset=['PE(TTM)'])
    pe_zc_weight = pe_zc[['FUND_CODE', 'REPORT_DATE', 'HOLDING_MARKET_VALUE']].groupby(['FUND_CODE', 'REPORT_DATE']).sum().reset_index().rename(columns={'HOLDING_MARKET_VALUE': 'TOTAL_HOLDING_MARKET_VALUE'})
    pe_zc = pe_zc.merge(pe_zc_weight, on=['FUND_CODE', 'REPORT_DATE'], how='left')
    pe_zc['WEIGHTED_PE(TTM)'] = pe_zc['PE(TTM)'] * pe_zc['HOLDING_MARKET_VALUE'] / pe_zc['TOTAL_HOLDING_MARKET_VALUE']
    pe_zc = pe_zc[['FUND_CODE', 'REPORT_DATE', 'WEIGHTED_PE(TTM)']].groupby(['FUND_CODE', 'REPORT_DATE']).sum().reset_index()
    pb_zc = fund_zc_holding.dropna(subset=['PB(LF)'])
    pb_zc_weight = pb_zc[['FUND_CODE', 'REPORT_DATE', 'HOLDING_MARKET_VALUE']].groupby(['FUND_CODE', 'REPORT_DATE']).sum().reset_index().rename(columns={'HOLDING_MARKET_VALUE': 'TOTAL_HOLDING_MARKET_VALUE'})
    pb_zc = pb_zc.merge(pb_zc_weight, on=['FUND_CODE', 'REPORT_DATE'], how='left')
    pb_zc['WEIGHTED_PB(LF)'] = pb_zc['PB(LF)'] * pb_zc['HOLDING_MARKET_VALUE'] / pb_zc['TOTAL_HOLDING_MARKET_VALUE']
    pb_zc = pb_zc[['FUND_CODE', 'REPORT_DATE', 'WEIGHTED_PB(LF)']].groupby(['FUND_CODE', 'REPORT_DATE']).sum().reset_index()
    pe_zc['MARK'] = np.nan
    pe_zc.loc[(pe_zc['WEIGHTED_PE(TTM)'] > 0) & (pe_zc['WEIGHTED_PE(TTM)'] <= 30), 'MARK'] = 'low'
    pe_zc.loc[(pe_zc['WEIGHTED_PE(TTM)'] > 30) & (pe_zc['WEIGHTED_PE(TTM)'] <= 50), 'MARK'] = 'middle'
    pe_zc.loc[(pe_zc['WEIGHTED_PE(TTM)'] > 50) | (pe_zc['WEIGHTED_PE(TTM)'] <= 0), 'MARK'] = 'high'
    pe_zc_count = pe_zc[['FUND_CODE', 'REPORT_DATE', 'MARK']].groupby(['REPORT_DATE', 'MARK']).count().reset_index().rename(columns={'FUND_CODE': 'COUNT'})
    pe_zc_count_sum = pe_zc[['FUND_CODE', 'REPORT_DATE']].groupby(['REPORT_DATE']).count().reset_index().rename(columns={'FUND_CODE': 'COUNT_SUM'})
    pe_zc_count = pe_zc_count.merge(pe_zc_count_sum, on=['REPORT_DATE'], how='left')
    pe_zc_count['COUNT_RATIO'] = pe_zc_count['COUNT'] / pe_zc_count['COUNT_SUM']
    pb_zc['MARK'] = np.nan
    pb_zc.loc[(pb_zc['WEIGHTED_PB(LF)'] > 5) | (pb_zc['WEIGHTED_PB(LF)'] <= 0), 'MARK'] = 'high'
    pb_zc['MARK'] = pb_zc['MARK'].fillna('low')
    pb_zc_count = pb_zc[['FUND_CODE', 'REPORT_DATE', 'MARK']].groupby(['REPORT_DATE', 'MARK']).count().reset_index().rename(columns={'FUND_CODE': 'COUNT'})
    pb_zc_count_sum = pb_zc[['FUND_CODE', 'REPORT_DATE']].groupby(['REPORT_DATE']).count().reset_index().rename(columns={'FUND_CODE': 'COUNT_SUM'})
    pb_zc_count = pb_zc_count.merge(pb_zc_count_sum, on=['REPORT_DATE'], how='left')
    pb_zc_count['COUNT_RATIO'] = pb_zc_count['COUNT'] / pb_zc_count['COUNT_SUM']
    # 估值变化
    fund_zc_holding_diff = fund_zc_holding_diff.merge(stock_valuation.rename(columns={'TRADE_DATE': 'RECENT_TRADE_DATE'}), on=['RECENT_TRADE_DATE', 'TICKER_SYMBOL'], how='left')
    pe_zc_diff = fund_zc_holding_diff.dropna(subset=['PE(TTM)'])
    # pe_zc_diff['PE(TTM)_DIFF'] = pe_zc_diff['MV_IN_NA_DIFF'] / 100.0 * pe_zc_diff['PE(TTM)']
    # pe_zc_diff = pe_zc_diff[['FUND_CODE', 'REPORT_DATE', 'PE(TTM)_DIFF']].groupby(['FUND_CODE', 'REPORT_DATE']).sum().reset_index()
    # pe_zc_diff = pe_zc_diff[['REPORT_DATE', 'PE(TTM)_DIFF']].groupby(['REPORT_DATE']).mean().reset_index()
    pe_zc_diff['MV_IN_NA_DIFF'] = pe_zc_diff['MV_IN_NA_DIFF'] / 100.0
    pe_zc_diff['ABS_MV_IN_NA_DIFF'] = pe_zc_diff['MV_IN_NA_DIFF'].abs()
    pe_zc_diff_weight = pe_zc_diff[['FUND_CODE', 'REPORT_DATE', 'ABS_MV_IN_NA_DIFF']].groupby(['FUND_CODE', 'REPORT_DATE']).sum().reset_index().rename(columns={'ABS_MV_IN_NA_DIFF': 'TOTAL_ABS_MV_IN_NA_DIFF'})
    pe_zc_diff = pe_zc_diff.merge(pe_zc_diff_weight, on=['FUND_CODE', 'REPORT_DATE'], how='left')
    pe_zc_diff['WEIGHTED_PE(TTM)_DIFF'] = pe_zc_diff['PE(TTM)'] * pe_zc_diff['MV_IN_NA_DIFF'] / pe_zc_diff['TOTAL_ABS_MV_IN_NA_DIFF']
    pe_zc_diff = pe_zc_diff[['FUND_CODE', 'REPORT_DATE', 'WEIGHTED_PE(TTM)_DIFF']].groupby(['FUND_CODE', 'REPORT_DATE']).sum().reset_index()
    pe_zc_diff = pe_zc_diff[['REPORT_DATE', 'WEIGHTED_PE(TTM)_DIFF']].groupby(['REPORT_DATE']).mean().reset_index()
    # 核心资产估值溢价：基金重仓股 / 非基金重仓股的PEPB中位数之比
    fund_zc_holding['IS_ZC'] = 1
    fund_holding = stock_valuation[stock_valuation['TRADE_DATE'].isin(fund_zc_holding['RECENT_TRADE_DATE'].unique().tolist())]
    fund_holding = fund_holding.rename(columns={'TRADE_DATE': 'RECENT_TRADE_DATE'}).merge(fund_zc_holding[['RECENT_TRADE_DATE', 'TICKER_SYMBOL', 'IS_ZC']], on=['RECENT_TRADE_DATE', 'TICKER_SYMBOL'], how='left')
    fund_holding['IS_ZC'] = fund_holding['IS_ZC'].fillna(0)
    fund_holding = fund_holding.merge(fund_zc_holding[['RECENT_TRADE_DATE', 'REPORT_DATE']].drop_duplicates(), on=['RECENT_TRADE_DATE'], how='left')
    pe_quantile = fund_holding[['REPORT_DATE', 'IS_ZC', 'PE(TTM)']].groupby(['REPORT_DATE', 'IS_ZC']).quantile().reset_index()
    pe_quantile = pe_quantile.pivot(index='REPORT_DATE', columns='IS_ZC', values='PE(TTM)')
    pe_quantile['RATIO'] = pe_quantile[1] / pe_quantile[0]
    pb_quantile = fund_holding[['REPORT_DATE', 'IS_ZC', 'PB(LF)']].groupby(['REPORT_DATE', 'IS_ZC']).quantile().reset_index()
    pb_quantile = pb_quantile.pivot(index='REPORT_DATE', columns='IS_ZC', values='PB(LF)')
    pb_quantile['RATIO'] = pb_quantile[1] / pb_quantile[0]
    return total_zcmv, pe_zc_count, pb_zc_count, pe_zc_diff, pe_quantile, pb_quantile

def fund_sector(fund_zc_holding):
    """
    板块分析
    """
    # 上市板块
    fund_zc_holding['SECTOR'] = fund_zc_holding['TICKER_SYMBOL'].apply(lambda x: '主板-上海' if x[:2] == '60' else '主板-深圳' if x[:2] == '00' else '创业板-深圳'if x[:2] == '30' else '科创版-上海' if x[:2] == '68' else '主板-香港')
    fund_zc_holding_sector = fund_zc_holding[['REPORT_DATE', 'FUND_CODE', 'SECTOR', 'TICKER_SYMBOL']].groupby(['REPORT_DATE', 'FUND_CODE', 'SECTOR']).count().reset_index().rename(columns={'TICKER_SYMBOL': 'COUNT'})
    fund_zc_holding_sector = fund_zc_holding_sector[['REPORT_DATE', 'SECTOR', 'COUNT']].groupby(['REPORT_DATE', 'SECTOR']).sum().reset_index()
    fund_zc_holding_sector = fund_zc_holding_sector.pivot(index='REPORT_DATE', columns='SECTOR', values='COUNT').fillna(0.0)
    fund_zc_holding_sector = fund_zc_holding_sector.apply(lambda x: x / x.sum(), axis=1)
    return fund_zc_holding_sector

def fund_theme():
    """
    主题分析
    """
    # 大类行业
    fund_theme = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/fund_theme.hdf', key='table')
    fund_theme = fund_theme.rename(columns={'jjdm': 'FUND_CODE', 'jsrq': 'REPORT_DATE', 'zclb': 'IS_ZC', 'zblx': 'THEME',
                                            'zgpszb': 'MV_IN_NA', 'jsqbd': 'MV_IN_NA_DIFF', 'tlpj': 'HOMO_AVG'})
    fund_theme['IS_ZC'] = fund_theme['IS_ZC'].astype(int)
    fund_theme = fund_theme.replace({'TMT': 'TMT', 'ZZ': '制造', 'ZQ': '周期', 'DJR': '大金融', 'XF': '消费', 'QT': '其他'})
    fund_theme = fund_theme[fund_theme['IS_ZC'] == 1]
    fund_theme = fund_theme[['REPORT_DATE', 'THEME', 'MV_IN_NA']].groupby(['REPORT_DATE', 'THEME']).mean().reset_index()
    fund_theme = fund_theme.pivot(index='REPORT_DATE', columns='THEME', values='MV_IN_NA').fillna(0.0)
    fund_theme = fund_theme.apply(lambda x: x / x.sum(), axis=1)
    return fund_theme

def fund_industry(fund_zc_holding):
    """
    行业分析
    """
    fund_industry = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/fund_industry.hdf', key='table')
    fund_industry = fund_industry.rename(columns={'jjdm': 'FUND_CODE', 'jsrq': 'REPORT_DATE', 'zclb': 'IS_ZC', 'hyhfbz': 'INDUSTRY_VERSION',
                                                  'fldm': 'INDUSTRY_ID', 'flmc': 'INDUSTRY_NAME', 'zzjbl': 'MV_IN_NA', 'hyzjzbjbd': 'MV_IN_NA_DIFF', 'hyzjzbltlpj': 'HOMO_AVG'})
    fund_industry['IS_ZC'] = fund_industry['IS_ZC'].astype(int)
    fund_industry['INDUSTRY_VERSION'] = fund_industry['INDUSTRY_VERSION'].astype(int)
    fund_industry = fund_industry[fund_industry['INDUSTRY_VERSION'] == 2]
    fund_industry = fund_industry[fund_industry['IS_ZC'] == 1]
    fund_industry = fund_industry[['REPORT_DATE', 'INDUSTRY_NAME', 'MV_IN_NA']].groupby(['REPORT_DATE', 'INDUSTRY_NAME']).mean().reset_index()
    fund_industry = fund_industry.pivot(index='REPORT_DATE', columns='INDUSTRY_NAME', values='MV_IN_NA')

    stock_industry = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/stock_industry.hdf', key='table')
    stock_industry = stock_industry.rename(columns={'zqdm': 'TICKER_SYMBOL', 'flmc': 'INDUSTRY_NAME', 'fldm': 'INDUSTRY_ID',
                                                    'fljb': 'INDUSTRY_TYPE', 'hyhfbz': 'INDUSTRY_VERSION',
                                                    'qsrq': 'BEGIN_DATE', 'jsrq': 'END_DATE', 'sfyx': 'IS_NEW'})
    stock_industry['END_DATE'] = stock_industry['END_DATE'].fillna(20990101)
    stock_industry['BEGIN_DATE'] = stock_industry['BEGIN_DATE'].astype(str)
    stock_industry['END_DATE'] = stock_industry['END_DATE'].astype(int).astype(str)
    stock_industry['INDUSTRY_VERSION'] = stock_industry['INDUSTRY_VERSION'].astype(int)
    stock_industry['INDUSTRY_TYPE'] = stock_industry['INDUSTRY_TYPE'].astype(int)
    stock_industry = stock_industry[stock_industry['INDUSTRY_VERSION'] == 2]
    stock_industry = stock_industry[stock_industry['INDUSTRY_TYPE'] == 2]
    fund_zc_holding = fund_zc_holding.merge(stock_industry[['TICKER_SYMBOL', 'INDUSTRY_NAME', 'BEGIN_DATE', 'END_DATE']], on=['TICKER_SYMBOL'], how='left')
    fund_zc_holding = fund_zc_holding[(fund_zc_holding['REPORT_DATE'] >= fund_zc_holding['BEGIN_DATE']) & (fund_zc_holding['REPORT_DATE'] < fund_zc_holding['END_DATE'])]
    fund_zc_holding = fund_zc_holding[['REPORT_DATE', 'FUND_CODE', 'INDUSTRY_NAME', 'MV_IN_NA']].groupby(['REPORT_DATE', 'FUND_CODE', 'INDUSTRY_NAME']).sum().reset_index()
    fund_zc_holding = fund_zc_holding[['REPORT_DATE', 'INDUSTRY_NAME', 'MV_IN_NA']].groupby(['REPORT_DATE', 'INDUSTRY_NAME']).mean().reset_index()
    fund_zc_holding = fund_zc_holding.pivot(index='REPORT_DATE', columns='INDUSTRY_NAME', values='MV_IN_NA')
    return fund_zc_holding

def fund_mv(fund_zc_holding):
    """
    市值分析
    """
    index_cons = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/index_cons.hdf', key='table')
    index_cons = index_cons.rename(columns={'SECUCODE': 'TICKER_SYMBOL', 'ENDDATE': 'END_DATE'})
    index_cons['END_DATE'] = index_cons['END_DATE'].apply(lambda x: x[:10].replace('-', ''))
    index_cons = index_cons[index_cons['INDEX'].isin(['HS300', 'ZZ500', 'ZZ1000'])]
    cal = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/cal.hdf', key='table')
    fund_zc_holding = fund_zc_holding[fund_zc_holding['REPORT_DATE'] >= index_cons['END_DATE'].min()]
    fund_zc_mv = fund_zc_holding.merge(cal[['TRADE_DATE', 'RECENT_TRADE_DATE']].rename(columns={'TRADE_DATE': 'REPORT_DATE'}), on=['REPORT_DATE'], how='left')
    fund_zc_mv = fund_zc_mv.merge(index_cons[['TICKER_SYMBOL', 'END_DATE', 'INDEX']].rename(columns={'END_DATE': 'RECENT_TRADE_DATE'}), on=['TICKER_SYMBOL', 'RECENT_TRADE_DATE'], how='left')
    fund_zc_mv['INDEX'] = fund_zc_mv['INDEX'].fillna('非成分股')
    fund_zc_mv_count = fund_zc_mv[['REPORT_DATE', 'FUND_CODE', 'INDEX', 'TICKER_SYMBOL']].groupby(['REPORT_DATE', 'FUND_CODE', 'INDEX']).count().reset_index().rename(columns={'TICKER_SYMBOL': 'COUNT'})
    fund_zc_mv_count = fund_zc_mv_count[['REPORT_DATE', 'INDEX', 'COUNT']].groupby(['REPORT_DATE', 'INDEX']).sum().reset_index()
    fund_zc_mv_count = fund_zc_mv_count.pivot(index='REPORT_DATE', columns='INDEX', values='COUNT').fillna(0.0)
    fund_zc_mv_count = fund_zc_mv_count.apply(lambda x: x / x.sum(), axis=1)

    index_cons = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/index_cons.hdf', key='table')
    index_cons = index_cons.rename(columns={'SECUCODE': 'TICKER_SYMBOL', 'ENDDATE': 'END_DATE'})
    index_cons['END_DATE'] = index_cons['END_DATE'].apply(lambda x: x[:10].replace('-', ''))
    index_cons = index_cons[index_cons['INDEX'].isin(['SZ50', 'ZZ100', 'SZ180', 'HS300'])]
    cal = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/cal.hdf', key='table')
    fund_zc_holding = fund_zc_holding[fund_zc_holding['REPORT_DATE'] >= index_cons['END_DATE'].min()]
    fund_zc_wmv = fund_zc_holding.merge(cal[['TRADE_DATE', 'RECENT_TRADE_DATE']].rename(columns={'TRADE_DATE': 'REPORT_DATE'}), on=['REPORT_DATE'], how='left')
    fund_zc_wmv_count = fund_zc_wmv[['REPORT_DATE', 'FUND_CODE', 'TICKER_SYMBOL']].groupby(['REPORT_DATE', 'FUND_CODE']).count().reset_index().rename(columns={'TICKER_SYMBOL': 'COUNT'})
    fund_zc_wmv_count = fund_zc_wmv_count[['REPORT_DATE', 'COUNT']].groupby(['REPORT_DATE']).sum().reset_index()
    for index in ['SZ50', 'ZZ100', 'SZ180', 'HS300']:
        index_cons_index = index_cons[index_cons['INDEX'] == index]
        fund_zc_wmv_index = fund_zc_wmv.merge(index_cons_index[['TICKER_SYMBOL', 'END_DATE', 'INDEX']].rename(columns={'END_DATE': 'RECENT_TRADE_DATE'}), on=['TICKER_SYMBOL', 'RECENT_TRADE_DATE'], how='left')
        fund_zc_wmv_index = fund_zc_wmv_index.dropna(subset=['INDEX'])
        fund_zc_wmv_index_count = fund_zc_wmv_index[['REPORT_DATE', 'FUND_CODE', 'TICKER_SYMBOL']].groupby(['REPORT_DATE', 'FUND_CODE']).count().reset_index().rename(columns={'TICKER_SYMBOL': index})
        fund_zc_wmv_index_count = fund_zc_wmv_index_count[['REPORT_DATE', index]].groupby(['REPORT_DATE']).sum().reset_index()
        fund_zc_wmv_count = fund_zc_wmv_count.merge(fund_zc_wmv_index_count, on=['REPORT_DATE'], how='left')
        fund_zc_wmv_count[index] = fund_zc_wmv_count[index] / fund_zc_wmv_count['COUNT']
    return fund_zc_mv_count, fund_zc_wmv_count

def fund_style(fund_zc_holding):
    """
    风格分析
    """
    index_cons = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/index_cons.hdf', key='table')
    index_cons = index_cons.rename(columns={'SECUCODE': 'TICKER_SYMBOL', 'ENDDATE': 'END_DATE'})
    index_cons['END_DATE'] = index_cons['END_DATE'].apply(lambda x: x[:10].replace('-', ''))
    index_cons = index_cons[index_cons['INDEX'].isin(['JCDPJZ', 'JCDPCZ', 'JCZPJZ', 'JCZPCZ', 'JCXPJZ', 'JCXPCZ'])]
    cal = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/cal.hdf', key='table')
    fund_zc_holding = fund_zc_holding[fund_zc_holding['REPORT_DATE'] >= index_cons['END_DATE'].min()]
    fund_zc_style = fund_zc_holding.merge(cal[['TRADE_DATE', 'RECENT_TRADE_DATE']].rename(columns={'TRADE_DATE': 'REPORT_DATE'}), on=['REPORT_DATE'], how='left')
    fund_zc_style = fund_zc_style.merge(index_cons[['TICKER_SYMBOL', 'END_DATE', 'INDEX']].rename(columns={'END_DATE': 'RECENT_TRADE_DATE'}), on=['TICKER_SYMBOL', 'RECENT_TRADE_DATE'], how='left')
    wind_mark = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/stock_style.hdf', key='table')
    wind_mark = wind_mark.rename(columns={'ticker': 'TICKER_SYMBOL', 'trade_date': 'TRADE_DATE', 'type': 'IS_ZC',
                                          'cap_score': 'CAP_SCORE', 'vcg_score': 'VCG_SCORE', 'category': 'CATEGORY'})
    wind_mark = wind_mark[wind_mark['IS_ZC'] == 'main']
    fund_zc_style = fund_zc_style.merge(wind_mark[['TICKER_SYMBOL', 'TRADE_DATE', 'CATEGORY']].rename(columns={'TRADE_DATE': 'RECENT_TRADE_DATE'}), on=['TICKER_SYMBOL', 'RECENT_TRADE_DATE'], how='left')
    fund_zc_style['INDEX'] = fund_zc_style['INDEX'].astype(str)
    fund_zc_style['CATEGORY'] = fund_zc_style['CATEGORY'].astype(str)
    fund_zc_style['MARK'] = fund_zc_style.apply(lambda x: '价值' if x['INDEX'][-2:] == 'JZ' else '成长' if x['INDEX'][-2:] == 'CZ'
                                                          else '价值' if x['CATEGORY'][-3:] == '价值型' else '成长' if x['CATEGORY'][-3:] == '成长型'
                                                          else '平衡', axis=1)
    fund_zc_style_count = fund_zc_style[['REPORT_DATE', 'FUND_CODE', 'TICKER_SYMBOL']].groupby(['REPORT_DATE', 'FUND_CODE']).count().reset_index().rename(columns={'TICKER_SYMBOL': 'COUNT'})
    fund_zc_style_count = fund_zc_style_count[['REPORT_DATE', 'COUNT']].groupby(['REPORT_DATE']).sum().reset_index()
    for m in ['价值', '成长', '平衡']:
        fund_zc_style_mark = fund_zc_style[fund_zc_style['MARK'] == m]
        fund_zc_style_mark_count = fund_zc_style_mark[['REPORT_DATE', 'FUND_CODE', 'TICKER_SYMBOL']].groupby(['REPORT_DATE', 'FUND_CODE']).count().reset_index().rename(columns={'TICKER_SYMBOL': m})
        fund_zc_style_mark_count = fund_zc_style_mark_count[['REPORT_DATE', m]].groupby(['REPORT_DATE']).sum().reset_index()
        fund_zc_style_count = fund_zc_style_count.merge(fund_zc_style_mark_count, on=['REPORT_DATE'], how='left')
        fund_zc_style_count[m] = fund_zc_style_count[m] / fund_zc_style_count['COUNT']

    fund_zc_style['MARK2'] = fund_zc_style.apply(lambda x: '大盘价值' if x['INDEX'] == 'JCDPJZ' else '大盘成长' if x['INDEX'] == 'JCDPCZ'
                                                      else '中盘价值' if x['INDEX'] == 'JCZPJZ' else '中盘成长' if x['INDEX'] == 'JCZPCZ'
                                                      else '小盘价值' if x['INDEX'] == 'JCXPJZ' else '小盘成长' if x['INDEX'] == 'JCXPCZ'
                                                      else '大盘价值' if x['CATEGORY'] == '大盘价值型' else '大盘成长' if x['CATEGORY'] == '大盘成长型' else '大盘平衡' if x['CATEGORY'] == '大盘均衡型'
                                                      else '中盘价值' if x['CATEGORY'] == '中盘价值型' else '中盘成长' if x['CATEGORY'] == '中盘成长型' else '中盘平衡' if x['CATEGORY'] == '中盘均衡型'
                                                      else '小盘价值' if x['CATEGORY'] == '小盘价值型' else '小盘成长' if x['CATEGORY'] == '小盘成长型' else '小盘平衡' if x['CATEGORY'] == '小盘均衡型'
                                                      else np.nan, axis=1)
    fund_zc_style = fund_zc_style.dropna(subset=['MARK2'])
    fund_zc_style2_count = fund_zc_style[['REPORT_DATE', 'FUND_CODE', 'TICKER_SYMBOL']].groupby(['REPORT_DATE', 'FUND_CODE']).count().reset_index().rename(columns={'TICKER_SYMBOL': 'COUNT'})
    fund_zc_style2_count = fund_zc_style2_count[['REPORT_DATE', 'COUNT']].groupby(['REPORT_DATE']).sum().reset_index()
    for m in ['大盘价值', '大盘成长', '大盘平衡', '中盘价值', '中盘成长', '中盘平衡', '小盘价值', '小盘成长', '小盘平衡']:
        fund_zc_style_mark = fund_zc_style[fund_zc_style['MARK2'] == m]
        fund_zc_style_mark_count = fund_zc_style_mark[['REPORT_DATE', 'FUND_CODE', 'TICKER_SYMBOL']].groupby(['REPORT_DATE', 'FUND_CODE']).count().reset_index().rename(columns={'TICKER_SYMBOL': m})
        fund_zc_style_mark_count = fund_zc_style_mark_count[['REPORT_DATE', m]].groupby(['REPORT_DATE']).sum().reset_index()
        fund_zc_style2_count = fund_zc_style2_count.merge(fund_zc_style_mark_count, on=['REPORT_DATE'], how='left')
        fund_zc_style2_count[m] = fund_zc_style2_count[m] / fund_zc_style2_count['COUNT']
    return fund_zc_style_count, fund_zc_style2_count

def fund_barra(fund_zc_holding):
    """
    Barra风格分析
    """
    barra = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/barra_style_exposure.hdf', key='table')
    barra = barra.rename(columns={'ticker': 'TICKER_SYMBOL', 'trade_date': 'TRADE_DATE'})
    factor_list = [factor for factor in list(barra.columns) if factor != 'TICKER_SYMBOL' and factor != 'TRADE_DATE']
    cal = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/cal.hdf', key='table')
    fund_zc_holding = fund_zc_holding[fund_zc_holding['REPORT_DATE'] >= barra['TRADE_DATE'].min()]
    fund_zc_holding = fund_zc_holding.merge(cal[['TRADE_DATE', 'RECENT_TRADE_DATE']].rename(columns={'TRADE_DATE': 'REPORT_DATE'}), on=['REPORT_DATE'], how='left')
    fund_zc_holding = fund_zc_holding.merge(barra.rename(columns={'TRADE_DATE': 'RECENT_TRADE_DATE'}), on=['RECENT_TRADE_DATE', 'TICKER_SYMBOL'], how='left')
    fund_zc_holding_weight = fund_zc_holding[['REPORT_DATE', 'FUND_CODE', 'MV_IN_NA']].groupby(['REPORT_DATE', 'FUND_CODE']).sum().reset_index().rename(columns={'MV_IN_NA': 'TOTAL_MV_IN_NA'})
    fund_zc_holding = fund_zc_holding.merge(fund_zc_holding_weight, on=['REPORT_DATE', 'FUND_CODE'], how='left')
    fund_zc_holding_barra_list = []
    for factor in factor_list:
        fund_zc_holding['WEIGHTED_{}'.format(factor)] = fund_zc_holding[factor] * fund_zc_holding['MV_IN_NA'] / fund_zc_holding['TOTAL_MV_IN_NA']
        fund_zc_holding_barra = fund_zc_holding[['FUND_CODE', 'REPORT_DATE', 'WEIGHTED_{}'.format(factor)]].groupby(['FUND_CODE', 'REPORT_DATE']).sum().reset_index()
        fund_zc_holding_barra = fund_zc_holding_barra[['REPORT_DATE', 'WEIGHTED_{}'.format(factor)]].groupby(['REPORT_DATE']).mean()
        fund_zc_holding_barra_list.append(fund_zc_holding_barra)
    fund_zc_holding_barra = pd.concat(fund_zc_holding_barra_list, axis=1).reset_index()
    return fund_zc_holding_barra

def stock_holding(fund_zc_holding):
    """
    持股变动
    """
    stock_industry = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/stock_industry.hdf', key='table')
    stock_industry = stock_industry.rename(columns={'zqdm': 'TICKER_SYMBOL', 'flmc': 'INDUSTRY_NAME', 'fldm': 'INDUSTRY_ID',
                                                    'fljb': 'INDUSTRY_TYPE', 'hyhfbz': 'INDUSTRY_VERSION',
                                                    'qsrq': 'BEGIN_DATE', 'jsrq': 'END_DATE', 'sfyx': 'IS_NEW'})
    stock_industry['END_DATE'] = stock_industry['END_DATE'].fillna(20990101)
    stock_industry['BEGIN_DATE'] = stock_industry['BEGIN_DATE'].astype(str)
    stock_industry['END_DATE'] = stock_industry['END_DATE'].astype(int).astype(str)
    stock_industry['INDUSTRY_VERSION'] = stock_industry['INDUSTRY_VERSION'].astype(int)
    stock_industry['INDUSTRY_TYPE'] = stock_industry['INDUSTRY_TYPE'].astype(int)
    stock_industry = stock_industry[stock_industry['INDUSTRY_VERSION'] == 2]
    stock_industry = stock_industry[stock_industry['INDUSTRY_TYPE'] == 1]
    fund_zc_holding = fund_zc_holding.merge(stock_industry[['TICKER_SYMBOL', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'BEGIN_DATE', 'END_DATE']], on=['TICKER_SYMBOL'], how='left')
    fund_zc_holding = fund_zc_holding[(fund_zc_holding['REPORT_DATE'] >= fund_zc_holding['BEGIN_DATE']) & (fund_zc_holding['REPORT_DATE'] < fund_zc_holding['END_DATE'])]
    fund_zc_holding = fund_zc_holding.drop(['BEGIN_DATE', 'END_DATE'], axis=1)
    industry_theme = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/industry_theme.hdf', key='table')
    industry_theme = industry_theme.rename(columns={'fldm': 'INDUSTRY_ID', 'hybh': 'THEME_ID', 'hyzt': 'THEME_NAME',
                                                    'qsrq': 'BEGIN_DATE', 'jsrq': 'END_DATE'})
    industry_theme['END_DATE'] = industry_theme['END_DATE'].fillna(20990101)
    industry_theme['BEGIN_DATE'] = industry_theme['BEGIN_DATE'].astype(str)
    industry_theme['END_DATE'] = industry_theme['END_DATE'].astype(int).astype(str)
    fund_zc_holding = fund_zc_holding.merge(industry_theme[['INDUSTRY_ID', 'THEME_NAME', 'BEGIN_DATE', 'END_DATE']], on=['INDUSTRY_ID'], how='left')
    fund_zc_holding = fund_zc_holding[(fund_zc_holding['REPORT_DATE'] >= fund_zc_holding['BEGIN_DATE']) & (fund_zc_holding['REPORT_DATE'] < fund_zc_holding['END_DATE'])]
    fund_zc_holding = fund_zc_holding.drop(['BEGIN_DATE', 'END_DATE'], axis=1)
    fund_zc_holding = fund_zc_holding.sort_values(['REPORT_DATE', 'INDUSTRY_NAME', 'MV_IN_NA'], ascending=[True, True, False]).drop_duplicates(['REPORT_DATE', 'INDUSTRY_NAME', 'TICKER_SYMBOL'])
    fund_zc_holding = fund_zc_holding.groupby(['REPORT_DATE', 'INDUSTRY_NAME']).head(3)
    return fund_zc_holding

def fund_holding_analysis(date):
    """
    公募基金持仓分析
    """
    # 基金池
    # fund, total, fund_overview = fund_info(date)
    # fund.to_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/fund.hdf', key='table', mode='w')
    # fund = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/fund.hdf', key='table')
    # 基金持仓
    # fund_holding = HBDB().read_fund_holding_given_codes(fund['FUND_CODE'].unique().tolist())
    # fund_holding.to_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/fund_holding.hdf', key='table', mode='w')
    fund_holding = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/fund_holding.hdf', key='table')
    # fund_holding_diff = HBDB().read_fund_holding_diff_given_codes(fund['FUND_CODE'].unique().tolist())
    # fund_holding_diff.to_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/fund_holdingHBDB().read_fund_holding_given_codes(fund['FUND_CODE'].unique().tolist())_diff.hdf', key='table', mode='w')
    fund_holding_diff = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/fund_holding_diff.hdf', key='table')
    fund_holding = fund_holding.rename(columns={'jjdm': 'FUND_CODE', 'jsrq': 'REPORT_DATE', 'zqdm': 'TICKER_SYMBOL', 'zqmc': 'SEC_SHORT_NAME',
                                                'ccsz': 'HOLDING_MARKET_VALUE', 'ccsl': 'HOLDING_AMOUNT', 'zjbl': 'MV_IN_NA'})
    fund_holding['REPORT_DATE'] = fund_holding['REPORT_DATE'].astype(str)
    fund_holding_diff = fund_holding_diff.rename(columns={'jjdm': 'FUND_CODE', 'jsrq': 'REPORT_DATE', 'zqdm': 'TICKER_SYMBOL', 'zqmc': 'SEC_SHORT_NAME',
                                                          'zclb': 'IS_ZC', 'zgblbd': 'MV_IN_NA_DIFF', 'sfsqzcg': 'IS_LAST_ZC'})
    fund_holding_diff['REPORT_DATE'] = fund_holding_diff['REPORT_DATE'].astype(str)
    fund_holding_diff['IS_ZC'] = fund_holding_diff['IS_ZC'].astype(int)
    fund_holding_diff['IS_LAST_ZC'] = fund_holding_diff['IS_LAST_ZC'].astype(int)
    # 基金重仓
    fund_zc_holding = fund_holding.sort_values(['FUND_CODE', 'REPORT_DATE', 'MV_IN_NA'], ascending=[True, True, False]).groupby(['FUND_CODE', 'REPORT_DATE']).head(10)
    fund_zc_holding_diff = fund_holding_diff[fund_holding_diff['IS_ZC'] == 1]
    # 估值变化
    # fund_valuation(date, fund_zc_holding, fund_zc_holding_diff)
    # 行业变化
    fund_theme()
    fund_industry(fund_zc_holding)
    fund_mv(fund_zc_holding)
    fund_style(fund_zc_holding)
    fund_barra(fund_zc_holding)
    stock_holding(fund_zc_holding)
    return

if __name__ == "__main__":
    analysis_date = '20211231'
    fund_holding_analysis(analysis_date)



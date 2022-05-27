# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


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

def get_industry_stock():
    # stock_industry = HBDB().read_stock_industry()
    # stock_industry.to_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/stock_industry.hdf', key='table', mode='w')
    stock_industry = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/stock_industry.hdf', key='table')
    stock_industry = stock_industry.rename(columns={'zqdm': 'TICKER_SYMBOL', 'flmc': 'INDUSTRY_NAME', 'fldm': 'INDUSTRY_ID', 'fljb': 'INDUSTRY_TYPE', 'hyhfbz': 'INDUSTRY_VERSION', 'qsrq': 'BEGIN_DATE', 'jsrq': 'END_DATE', 'sfyx': 'IS_NEW'})
    stock_industry['END_DATE'] = stock_industry['END_DATE'].fillna(20990101)
    stock_industry['BEGIN_DATE'] = stock_industry['BEGIN_DATE'].astype(str)
    stock_industry['END_DATE'] = stock_industry['END_DATE'].astype(int).astype(str)
    stock_industry['INDUSTRY_VERSION'] = stock_industry['INDUSTRY_VERSION'].astype(int)
    stock_industry['INDUSTRY_TYPE'] = stock_industry['INDUSTRY_TYPE'].astype(int)
    stock_industry['IS_NEW'] = stock_industry['IS_NEW'].astype(int)
    stock_industry = stock_industry[stock_industry['INDUSTRY_VERSION'] == 2]
    stock_industry = stock_industry[stock_industry['INDUSTRY_TYPE'] == 1]
    stock_industry = stock_industry[['INDUSTRY_NAME', 'TICKER_SYMBOL', 'BEGIN_DATE', 'END_DATE', 'IS_NEW']]
    return stock_industry

def main(index_list, report_date, industry_name):
    report_dates = sorted([i + j for i in [str(int(report_date[:4]) - 2), str(int(report_date[:4]) - 1), str(int(report_date[:4]))] for j in ['0331', '0630', '0930', '1231']])
    report_dates = [date for date in report_dates if date <= report_date][-5:]
    cal = get_cal_and_trade_cal('20050101', report_date)[0]
    report_trade_dates = [cal[cal['TRADE_DATE'] == date]['RECENT_TRADE_DATE'].values[0] for date in report_dates]
    industry_stock = get_industry_stock()
    industry_stock = industry_stock[industry_stock['INDUSTRY_NAME'] == industry_name]
    industry_stock = industry_stock[industry_stock['IS_NEW'] == 1]

    finance_data_list = []
    for date in report_dates:
        print(date)
        finance_data_date = HBDB().read_finance_data_given_date(date)
        finance_data_list.append(finance_data_date)
    finance_data = pd.concat(finance_data_list)
    finance_data.to_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/finance_data.hdf', key='table', mode='w')
    finance_data = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/finance_data.hdf', key='table')
    finance_data = finance_data.loc[finance_data['TICKER_SYMBOL'].str.len() == 6]
    finance_data = finance_data.loc[finance_data['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6'])]
    finance_data = finance_data[['END_DATE', 'PUBLISH_DATE', 'TICKER_SYMBOL'] + index_list].rename(columns={'END_DATE': 'REPORT_DATE'})
    finance_data = finance_data.sort_values(['TICKER_SYMBOL', 'REPORT_DATE', 'PUBLISH_DATE']).drop_duplicates(['TICKER_SYMBOL', 'REPORT_DATE'], keep='last')
    finance_data = finance_data.merge(cal[['TRADE_DATE', 'RECENT_TRADE_DATE']].rename(columns={'TRADE_DATE': 'REPORT_DATE'}), on=['REPORT_DATE'], how='left')

    stock_data_list = []
    for date in report_trade_dates:
        print(date)
        stock_data_date = HBDB().read_stock_market_value_given_date(date)
        stock_data_list.append(stock_data_date)
    stock_data = pd.concat(stock_data_list)
    stock_data.to_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/market_value.hdf', key='table', mode='w')
    stock_data = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/market_value.hdf', key='table')
    stock_data = stock_data.loc[stock_data['TICKER_SYMBOL'].str.len() == 6]
    stock_data = stock_data.loc[stock_data['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6'])]
    stock_data = stock_data[['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'MARKET_VALUE', 'NEG_MARKET_VALUE']]
    stock_data = finance_data.rename(columns={'RECENT_TRADE_DATE': 'TRADE_DATE'}).merge(stock_data, on=['TRADE_DATE', 'TICKER_SYMBOL'], how='left')
    stock_data = stock_data[stock_data['TICKER_SYMBOL'].isin(industry_stock['TICKER_SYMBOL'].unique().tolist())]
    # stock_data = stock_data.merge(industry_stock[['TICKER_SYMBOL', 'BEGIN_DATE', 'END_DATE']], on=['TICKER_SYMBOL'], how='left')
    # stock_data = stock_data[(stock_data['BEGIN_DATE'] < stock_data['REPORT_DATE']) & (stock_data['END_DATE'] > stock_data['REPORT_DATE'])]

    total_ticker = len(industry_stock[industry_stock['IS_NEW'] == 1])
    use_ticker = len(stock_data[stock_data['REPORT_DATE'] == report_date])

    stock_data_weight = stock_data[['REPORT_DATE', 'MARKET_VALUE']].groupby('REPORT_DATE').sum().reset_index().rename(columns={'MARKET_VALUE': 'TOTAL_MARKET_VALUE'})
    stock_data = stock_data.merge(stock_data_weight, on=['REPORT_DATE'], how='left')
    industry_data_list = []
    for index in index_list:
        stock_data['{}_WEIGHTED'.format(index)] = stock_data[index] * stock_data['MARKET_VALUE'] / stock_data['TOTAL_MARKET_VALUE']
        industry_data = stock_data[['REPORT_DATE', '{}_WEIGHTED'.format(index)]].groupby('REPORT_DATE').sum().rename(columns={'{}_WEIGHTED'.format(index): index})
        industry_data_list.append(industry_data)
    industry_data = pd.concat(industry_data_list, axis=1)
    industry_data[index_list] = industry_data[index_list] / 100.0
    industry_data.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), industry_data.index)
    industry_data['行业名称'] = industry_name
    industry_data = industry_data[['行业名称'] + index_list]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    for index in index_list:
        ax.plot(industry_data.index, industry_data[index].values, label=index)
    plt.legend()
    plt.title('{0}盈利指标变动（已出报告数/应出报告数：{1}/{2})'.format(industry_name, use_ticker, total_ticker))
    plt.savefig('D:/Git/hbshare/hbshare/fe/xwq/data/industry/{0}.png'.format(industry_name))
    return industry_data


if __name__ == '__main__':
    report_date = '20211231'
    index_list = ['ROE_TTM', 'ROA_TTM', 'ROIC_TTM', 'NET_PROFIT_RATIO_TTM', 'GROSS_INCOME_RATIO_TTM', 'EBIT_ASSET_RATIO_TTM']
    industry_stock = get_industry_stock()
    industry_name_list = industry_stock[industry_stock['IS_NEW'] == 1]['INDUSTRY_NAME'].unique().tolist()
    result_list = []
    for industry_name in industry_name_list:
        result = main(index_list, report_date, industry_name)
        result_list.append(result)
    result = pd.concat(result_list)
    result.to_excel('D:/Git/hbshare/hbshare/fe/xwq/data/industry/data.xlsx')
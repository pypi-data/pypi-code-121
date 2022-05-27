# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
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

# company_list = ['阿里巴巴-SW', '京东集团-SW', '凯莱英', '美团-W', '腾讯控股']
# holding_list = []
# for company in company_list:
#     holding = pd.read_excel('C:/Users/wenqian.xu/Desktop/JGCG/{}机构持股.xlsx'.format(company), sheet_name='file', index_col=0).reset_index().drop('index', axis=1)
#     holding = holding.dropna(subset=['机构名称'])
#     holding = holding[['类型', '持仓市值']].groupby(['类型']).sum().reset_index()
#     holding['持仓市值占比'] = holding['持仓市值'] / holding['持仓市值'].sum()
#     holding['公司'] = company
#     holding_list.append(holding)
# holding = pd.concat(holding_list)
# holding = holding[['类型', '持仓市值占比']].groupby(['类型']).mean().reset_index()
# holding.to_excel('C:/Users/wenqian.xu/Desktop/JGCG/机构持股.xlsx')

# holding_change_total = get_cal_and_trade_cal('20210315', '20220315')[0][['TRADE_DATE']].rename(columns={'TRADE_DATE': '变动日期'})
# company_list = ['阿里巴巴-SW', '京东集团-SW', '凯莱英', '美团-W', '腾讯控股']
# holding_change_list = []
# for company in company_list:
#     holding_change = pd.read_excel('C:/Users/wenqian.xu/Desktop/JGCG/{}异动分析.xlsx'.format(company), sheet_name='file', index_col=0).reset_index().drop('Unnamed: 1', axis=1)
#     cg_change = holding_change[['变动日期', '类型', '持股变动(股)']].groupby(['变动日期', '类型']).sum().reset_index().rename(columns={'持股变动(股)': '持股变动(股)_{}'.format(company)})
#     sz_change = holding_change[['变动日期', '类型', '市值变动']].groupby(['变动日期', '类型']).sum().reset_index().rename(columns={'市值变动': '市值变动_{}'.format(company)})
#     holding_change = cg_change.merge(sz_change, on=['变动日期', '类型'], how='left')
#     holding_change = holding_change[holding_change['类型'] == '国际'].drop('类型', axis=1)
#     holding_change['变动日期'] = holding_change['变动日期'].apply(lambda x: x.replace('/', ''))
#     holding_change_total = holding_change_total.merge(holding_change, on=['变动日期'], how='left')
# holding_change_total.to_excel('C:/Users/wenqian.xu/Desktop/JGCG/异动分析.xlsx')

# holding_change_total = get_cal_and_trade_cal('20210315', '20220315')[0][['TRADE_DATE']].rename(columns={'TRADE_DATE': '变动日期'})
# company_list = ['阿里巴巴-SW', '京东集团-SW', '凯莱英', '美团-W', '腾讯控股']
# holding_change_list = []
# for company in company_list:
#     holding_change = pd.read_excel('C:/Users/wenqian.xu/Desktop/JGCG/{}异动分析.xlsx'.format(company), sheet_name='file', index_col=0).reset_index().drop('Unnamed: 1', axis=1)
#     holding_change = holding_change[['变动日期', '类型', '变动占总股数比']].groupby(['变动日期', '类型']).sum().reset_index().rename(columns={'变动占总股数比': '变动占总股数比_{}'.format(company)})
#     holding_change = holding_change[holding_change['类型'] == '国际'].drop('类型', axis=1)
#     holding_change['变动日期'] = holding_change['变动日期'].apply(lambda x: x.replace('/', ''))
#     holding_change_total = holding_change_total.merge(holding_change, on=['变动日期'], how='left')
# holding_change_total.to_excel('C:/Users/wenqian.xu/Desktop/JGCG/异动分析.xlsx')
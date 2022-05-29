# -*- coding: UTF-8 -*-
# Author: Hu Min
# Date: 2022-05-19
import pandas as pd
from pandas import json_normalize
import logging
import logging.config
from yqdata.utils.opensearch import get_client
import json
from basic import trade_calendar
import time

'''
因子库获取函数。使用多进程加快速度。
使用了tushareSDK获取了一些简单的数据，请先提前设置好tushare的token。
'''
def get_finance_factor(ts_code='', bar_count=None, start_date=None, end_date=None, factors=''):
    """
    获取财务因子
    :param ts_code: 股票代码
    :param bar_count: 查询数量
    :param start_date: 开始日期 (YYYYMMDD)
    :param end_date: 结束日期 (YYYYMMDD)
    :factors: 查询因子
    :return:
    """
    logging.debug("get factor values, ts_code: %s, bar_count: %s, start_date: %s, end_date: %s, factors: %s" % (ts_code, bar_count, start_date, end_date, factors))
    query = []
    if end_date is None:
        logging.error("end_date is None")
        return None
    if bar_count is None and start_date is None:
        logging.error("bar_count and start_date can not be None at the same time")
        return None
    if bar_count is not None and end_date is not None:
        cal_df = trade_calendar()
        end_index = pd.Index(cal_df['cal_date']).get_loc(end_date)
        trade_df = cal_df.loc[cal_df['is_open'] == 1]
        last_trade_day = cal_df.at[end_index, 'pretrade_date']
        trade_df = trade_df.reset_index(drop=True)
        last_trade_index = pd.Index(trade_df['cal_date']).get_loc(last_trade_day)
        if last_trade_index > bar_count:
            start_date = trade_df.at[last_trade_index - bar_count + 1, 'cal_date']
    if start_date is not None and end_date is not None:
        query.append({"range": {"date": {"gte":  start_date, "lte":  end_date}}})
    elif start_date is not None and end_date is None:
        query.append({"range": {"date": {"gte":  start_date}}})
    elif start_date is None and end_date is not None:
        query.append({"range": {"date": {"lte":  end_date}}})
    if ts_code != '':
        codes_term = []
        for code in ts_code.split(','):
            codes_term.append({"term": {"ts_code.keyword":  code }})
        query.append({"bool": {"should": codes_term}})


    if factors != '' and isinstance (factors ,str):
        factors = factors + ',ts_code,date'
        factors = [x.strip() for x in factors.split(',')]

    logging.debug("query: %s" % query)
    return get_client().search_by_condition(index='youngquant_factor_finance', must=query, size=1000000, fields=factors, sort='ts_code.keyword,date.keyword:asc')

if __name__ == '__main__':
    # print(get_finance_factor(ts_code='300902.SZ', start_date='20191203', end_date='20210102', factors='ts_code,pe,pb'))
    start = time.time()
    print(get_finance_factor(ts_code='000502.SZ,600530.SH,000425.SZ', bar_count= 50, end_date='20210102', factors='pe_ratio_ttm,pcf_ratio_ttm'))
    end1 = time.time()
    print(end1-start)
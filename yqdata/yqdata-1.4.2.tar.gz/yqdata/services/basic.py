# -*- coding: UTF-8 -*-
# Author: Hu Min
# Date: 2021-11-30
import pandas as pd
from pandas import json_normalize
import logging
import logging.config
from yqdata.utils.opensearch import get_client
import json

def daily_basic(ts_code='', trade_date = '', start_date=None, end_date=None, fields=''):
    """
    获取每日指标数据
    :param ts_code: 股票代码
    :param trade_date: 交易日期 
    :param start_date: 开始日期 (YYYYMMDD)
    :param end_date: 结束日期 (YYYYMMDD)
    :return:
    """
    logging.debug("get daily basic, ts_code: %s, trade_date: %s, start_date: %s, end_date: %s", ts_code, trade_date, start_date, end_date)
    query = []
    if ts_code != '':
        query.append({"match": {"ts_code.keyword":  ts_code }})
    if trade_date != '':
        query.append({"match": {"trade_date": trade_date}})
    if start_date is not None and end_date is not None:
        query.append({"range": {"trade_date": {"gte":  start_date, "lte":  end_date}}})
    elif start_date is not None and end_date is None:
        query.append({"range": {"trade_date": {"gte":  start_date}}})
    elif start_date is None and end_date is not None:
        query.append({"range": {"trade_date": {"lte":  end_date}}})

    if fields != '' and isinstance (fields ,str):
        fields = [x.strip() for x in fields.split(',')]

    return get_client().search_by_condition(index='daily_basic', must=query, size=100000, fields=fields)

def trade_calendar():
    """
    获取交易日历
    :return:
    """
    query = []
    
    return get_client().search_by_condition(index='youngquant_calendar', must=query, size=100000, fields=['is_open','cal_date','pretrade_date'], sort='cal_date.keyword:asc')

if __name__ == '__main__':
    # print(daily_basic(ts_code='300902.SZ', start_date='20191203', end_date='20210102', fields='ts_code,pe,pb'))
    print(trade_calendar())
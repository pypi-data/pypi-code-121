# -*- coding: UTF-8 -*-
# Author: Hu Min
# Date: 2021-11-30
import pandas as pd
from pandas import json_normalize
import logging
import logging.config
from yqdata.utils.opensearch import get_client
import json

def stock_list(ts_code='', is_hs=None, market=None, list_status=None, exchange=None, fields=None):
    """
    获取股票列表
    :param ts_code: str 股票代码
    :param is_hs: str 是否沪深港通标的，N否 H沪股通 S深股通
    :param market: str 股票市场 （主板/创业板/科创板/CDR/北交所）
    :param list_status: str 上市状态 L上市 D退市 P暂停上市，默认是L
    :param exchange: str 交易所 SSE上交所 SZSE深交所 BSE北交所
    :param fields: str
    :return:
    """
    query = []
    if ts_code != '':
        query.append({"match": {"ts_code.keyword":  ts_code }})
    if is_hs is not None:
        query.append({"match": {"is_hs.keyword":  is_hs }})
    if market is not None:
        query.append({"match": {"market.keyword":  market }})
    if list_status is not None:
        query.append({"match": {"list_status.keyword":  list_status }})
    if exchange is not None:
        query.append({"match": {"exchange.keyword":  exchange }})

    if fields != '' and isinstance (fields ,str):
        fields = [x.strip() for x in fields.split(',')]

    return get_client().search_by_condition(index='stock_basic', must=query, size=100000, fields=fields)

def get_income(ts_code, ann_date=None, f_ann_date=None, period=None, report_type=None, comp_type=None, end_type=None,
           start_date=None, end_date=None, fields=None):
    """
    获取财务分析数据
    :param ts_code: str 股票代码
    :param ann_date: str 公告日期（YYYYMMDD格式）
    :param f_ann_date: str 发布日期（YYYYMMDD格式）
    :param period: str 报告期（每个季度最后一天的日期，比如20171231表示年报）
    :param report_type: str 报告类型：
    :param comp_type: str   公司类型：（1一般工商业2银行3保险4证券）
    :param end_type: str 报告期编码（1~4表示季度，e.g. 4表示年报）
    :param start_date: str 报告期开始日期（YYYYMMDD格式）
    :param end_date: str 报告期结束日期（YYYYMMDD格式）
    :param fields: str
    :return:
    """
    query = []
    if ts_code != '':
        query.append({"match": {"ts_code.keyword":  ts_code }})
    if start_date is not None and end_date is not None:
        query.append({"range": {"ann_date": {"gte":  start_date, "lte":  end_date}}})
    elif start_date is not None and end_date is None:
        query.append({"range": {"ann_date": {"gte":  start_date}}})
    elif start_date is None and end_date is not None:
        query.append({"range": {"ann_date": {"lte":  end_date}}})

    if fields != '' and isinstance (fields ,str):
        fields = [x.strip() for x in fields.split(',')]

    return get_client().search_by_condition(index='income', must=query, size=100000, fields=fields)

def get_balance_sheet(ts_code, ann_date=None, f_ann_date=None, period=None, report_type=None, comp_type=None, end_type=None,
           start_date=None, end_date=None, fields=None):
    """
    获取上市公司资产负债表
    :param ts_code: str 股票代码
    :param ann_date: str 公告日期（YYYYMMDD格式）
    :param f_ann_date: str 发布日期（YYYYMMDD格式）
    :param period: str 报告期（每个季度最后一天的日期，比如20171231表示年报）
    :param report_type: str 报告类型：
    :param comp_type: str   公司类型：（1一般工商业2银行3保险4证券）
    :param end_type: str 报告期编码（1~4表示季度，e.g. 4表示年报）
    :param start_date: str 报告期开始日期（YYYYMMDD格式）
    :param end_date: str 报告期结束日期（YYYYMMDD格式）
    :param fields: str
    :return:
    """
    query = []
    if ts_code != '':
        query.append({"match": {"ts_code.keyword":  ts_code }})
    if start_date is not None and end_date is not None:
        query.append({"range": {"ann_date": {"gte":  start_date, "lte":  end_date}}})
    elif start_date is not None and end_date is None:
        query.append({"range": {"ann_date": {"gte":  start_date}}})
    elif start_date is None and end_date is not None:
        query.append({"range": {"ann_date": {"lte":  end_date}}})

    if fields != '' and isinstance (fields ,str):
        fields = [x.strip() for x in fields.split(',')]

    return get_client().search_by_condition(index='balancesheet', must=query, size=100000, fields=fields)

def get_cashflow(ts_code, ann_date=None, f_ann_date=None, period=None, report_type=None, comp_type=None, end_type=None,
           start_date=None, end_date=None, fields=None):
    """
    获取上市公司现金流量表
    :param ts_code: str 股票代码
    :param ann_date: str 公告日期（YYYYMMDD格式）
    :param f_ann_date: str 发布日期（YYYYMMDD格式）
    :param period: str 报告期（每个季度最后一天的日期，比如20171231表示年报）
    :param report_type: str 报告类型：
    :param comp_type: str   公司类型：（1一般工商业2银行3保险4证券）
    :param end_type: str 报告期编码（1~4表示季度，e.g. 4表示年报）
    :param start_date: str 报告期开始日期（YYYYMMDD格式）
    :param end_date: str 报告期结束日期（YYYYMMDD格式）
    :param fields: str
    :return:
    """
    query = []
    if ts_code != '':
        query.append({"match": {"ts_code.keyword":  ts_code }})
    if start_date is not None and end_date is not None:
        query.append({"range": {"ann_date": {"gte":  start_date, "lte":  end_date}}})
    elif start_date is not None and end_date is None:
        query.append({"range": {"ann_date": {"gte":  start_date}}})
    elif start_date is None and end_date is not None:
        query.append({"range": {"ann_date": {"lte":  end_date}}})

    if fields != '' and isinstance (fields ,str):
        fields = [x.strip() for x in fields.split(',')]

    return get_client().search_by_condition(index='cashflow', must=query, size=100000, fields=fields)

def get_express(ts_code, ann_date=None, start_date=None, end_date=None, period=None, fields=''):
    """
    获取上市公司业绩快报
    :param ts_code: str 股票代码
    :param ann_date: str 公告日期（YYYYMMDD格式）
    :param start_date: str 公告日期（YYYYMMDD格式）
    :param end_date: str 公告日期（YYYYMMDD格式）
    :param period: str 报告期（每个季度最后一天的日期，比如20171231表示年报）
    :param fields: str
    """
    query = []
    if ts_code != '':
        query.append({"match": {"ts_code.keyword":  ts_code }})
    if start_date is not None and end_date is not None:
        query.append({"range": {"ann_date": {"gte":  start_date, "lte":  end_date}}})
    elif start_date is not None and end_date is None:
        query.append({"range": {"ann_date": {"gte":  start_date}}})
    elif start_date is None and end_date is not None:
        query.append({"range": {"ann_date": {"lte":  end_date}}})

    if fields != '' and isinstance (fields ,str):
        fields = [x.strip() for x in fields.split(',')]

    return get_client().search_by_condition(index='express', must=query, size=100000, fields=fields)

def get_fina_indicator(ts_code, ann_date=None, start_date=None, end_date=None, period=None, fields=''):
    """
    获取上市公司财务指标
    :param ts_code: str 股票代码
    :param ann_date: str 公告日期（YYYYMMDD格式）
    :param start_date: str 公告日期（YYYYMMDD格式）
    :param end_date: str 公告日期（YYYYMMDD格式）
    :param period: str 报告期（每个季度最后一天的日期，比如20171231表示年报）
    :param fields: str
    """
    query = []
    if ts_code != '':
        query.append({"match": {"ts_code.keyword":  ts_code }})
    if start_date is not None and end_date is not None:
        query.append({"range": {"ann_date": {"gte":  start_date, "lte":  end_date}}})
    elif start_date is not None and end_date is None:
        query.append({"range": {"ann_date": {"gte":  start_date}}})
    elif start_date is None and end_date is not None:
        query.append({"range": {"ann_date": {"lte":  end_date}}})

    if fields != '' and isinstance (fields ,str):
        fields = [x.strip() for x in fields.split(',')]

    return get_client().search_by_condition(index='fina_indicator', must=query, size=100000, fields=fields)

def get_fina_audit(ts_code, ann_date=None, start_date=None, end_date=None, period=None, fields=''):
    """
    获取上市公司财务审计意见
    :param ts_code: str 股票代码
    :param ann_date: str 公告日期（YYYYMMDD格式）
    :param start_date: str 公告日期（YYYYMMDD格式）
    :param end_date: str 公告日期（YYYYMMDD格式）
    :param period: str 报告期（每个季度最后一天的日期，比如20171231表示年报）
    :param fields: str
    """
    query = []
    if ts_code != '':
        query.append({"match": {"ts_code.keyword":  ts_code }})
    if start_date is not None and end_date is not None:
        query.append({"range": {"ann_date": {"gte":  start_date, "lte":  end_date}}})
    elif start_date is not None and end_date is None:
        query.append({"range": {"ann_date": {"gte":  start_date}}})
    elif start_date is None and end_date is not None:
        query.append({"range": {"ann_date": {"lte":  end_date}}})

    if fields != '' and isinstance (fields ,str):
        fields = [x.strip() for x in fields.split(',')]

    return get_client().search_by_condition(index='fina_audit', must=query, size=100000, fields=fields)

def get_dividend(ts_code=None, ann_date=None, record_date=None, ex_date=None, imp_ann_date=None, fields=''):
    """
    获取股票分红信息
    :param ts_code: str 股票代码
    :param ann_date: str 公告日期（YYYYMMDD格式）
    :param record_date: str 股权登记日（YYYYMMDD格式）
    :param ex_date: str 除权除息日（YYYYMMDD格式）
    :param imp_ann_date: str 红股上市日（YYYYMMDD格式）
    :param fields: str
    """
    query = []
    if ts_code != '':
        query.append({"match": {"ts_code.keyword":  ts_code }})
    if ann_date is not None:
        query.append({"match": {"ann_date.keyword":  ann_date }})
    if record_date is not None:
        query.append({"match": {"record_date.keyword":  record_date }})
    if ex_date is not None:
        query.append({"match": {"ex_date.keyword":  ex_date }})
    if imp_ann_date is not None:
        query.append({"match": {"imp_ann_date.keyword":  imp_ann_date }})

    if fields != '' and isinstance (fields ,str):
        fields = [x.strip() for x in fields.split(',')]

    return get_client().search_by_condition(index='dividend', must=query, size=100000, fields=fields)

def get_fina_mainbz_p(ts_code, start_date=None, end_date=None, fields=''):
    """
    获取上市公司主营业务构成
    :param ts_code: str 股票代码
    :param start_date: str 公告日期（YYYYMMDD格式）
    :param end_date: str 公告日期（YYYYMMDD格式）
    :param fields: str
    """
    query = []
    if ts_code != '':
        query.append({"match": {"ts_code.keyword":  ts_code }})
    if start_date is not None and end_date is not None:
        query.append({"range": {"end_date": {"gte":  start_date, "lte":  end_date}}})
    elif start_date is not None and end_date is None:
        query.append({"range": {"end_date": {"gte":  start_date}}})
    elif start_date is None and end_date is not None:
        query.append({"range": {"end_date": {"lte":  end_date}}})

    if fields != '' and isinstance (fields ,str):
        fields = [x.strip() for x in fields.split(',')]

    return get_client().search_by_condition(index='fina_mainbz', must=query, size=100000, fields=fields)

if __name__ == '__main__':
    print(stock_list(fields=''))
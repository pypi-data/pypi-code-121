# -*- coding: UTF-8 -*-
# Author: Hu Min
# Date: 2021-11-30
import pandas as pd
from pandas import json_normalize
import logging
import logging.config
from yqdata.utils.opensearch import get_client

def sw_list(index_code='', index_name='', level='L1', src='SW2014', fields=''):
    """
    获取申万行业分类，可以获取申万2014年版本（28个一级分类，104个二级分类，227个三级分类）和2021年本版（31个一级分类，134个二级分类，346个三级分类）列表信息
    :param level:
    :param src:
    """
    logging.debug("get sw list, level: %s, src: %s" % (level, src))
    query = []
    if level == 'L1':
        query.append({"match":{"level.keyword":level}})
    if index_code != '':
        query.append({"match":{"index_code.keyword":index_code}})
    if index_name != '':
        query.append({"match":{"industry_name.keyword":index_name}})

    if fields != '' and isinstance (fields ,str):
        fields = [x.strip() for x in fields.split(',')]

    return get_client().search_by_condition(index='index_classify', must=query, size=100000, fields=fields)

def sw_detail(index_code='', ts_code='', end_date=None):
    """
    申万行业成分
    :param index_code:
    :param ts_code:
    """
    logging.debug("get sw detail, index_code: %s, ts_code: %s" % (index_code, ts_code))
    query = []
    if index_code != '':
        query.append({"match":{"index_code.keyword":index_code}})
    if ts_code != '':
        query.append({"match":{"con_code.keyword":ts_code}})
    if end_date is not None:
        query.append({"range": {"in_date": {"lte":  end_date}}})

    return get_client().search_by_condition(index='index_member', must=query, size=100000)

def concept_list(src = 'ts'):
    """获取概念股分类，目前只有ts一个来源
    :param src:
    """
    logging.debug("get concept list")
    return get_client().search(index='concept', body={"size":1000000,"query":{"bool":{"must":[{"match":{"src":src}}],"must_not":[],"should":[]}}})

def concept_detail(id=None, ts_code=None):
    """获取概念股分类明细数据
    :param src:
    """
    logging.debug("get concept detail, id: %s, ts_code: %s" % (id, ts_code))
    if ts_code is None and id is not None:
        return get_client().search(index='concept_detail', body={"size":1000000,"query":{"bool":{"must":[{"match":{"id":id}}],"must_not":[],"should":[]}}})
    if id is None and ts_code is not None:
        return get_client().search(index='concept_detail', body={"size":1000000,"query":{"bool":{"must":[{"match":{"ts_code.keyword":ts_code}}],"must_not":[],"should":[]}}})
    return None

if __name__ == '__main__':
    print(sw_detail(index_code='801230.SI', end_date='20170101'))

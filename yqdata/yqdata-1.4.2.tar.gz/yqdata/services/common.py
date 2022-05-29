# -*- coding: UTF-8 -*-
# Author: Hu Min
# Date: 2021-11-30
import pandas as pd
from pandas import json_normalize
import logging
import logging.config
from yqdata.utils.opensearch import get_client
import json

def query(index, body):
    """
    查询
    :param index: 索引
    :param body: 查询条件
    :param size: 查询结果数量
    :return:
    """
    client = get_client()
    result = client.search(index=index, body=body)
    return result
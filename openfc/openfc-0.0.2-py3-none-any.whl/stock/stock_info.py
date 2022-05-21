#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Desc: 股票基本信息
'''
import json
import warnings
import requests
import pandas as pd
import os
from io import BytesIO
'''上海证券交易所-股票列表'''
URL_SH = 'http://query.sse.com.cn/security/stock/getStockListData.do'
'''深圳证券交易所-股票列表'''
URL_SZ = 'http://www.szse.cn/api/report/ShowReport'
'''北京证券交易所-股票列表'''
URL_BJ = 'http://www.bse.cn/nq/listedcompany.html'


# China
def stock_info_cn_sh_list(indicator: str = "A") -> pd.DataFrame:
    """
    上海证券交易所-股票列表
    A = "主板A股": "1"; B = "主板B股": "2"; C = "科创板": "8"
    :param indicator: choice of A/B/C
    :type indicator: str
    :return: indicator date result
    :rtype: pandas.DataFrame
    """
    indicator_map = {"A": "1", "B": "2", "C": "8"}
    headers = {
        "Host":
        "query.sse.com.cn",
        "Pragma":
        "no-cache",
        "Referer":
        "http://www.sse.com.cn/assortment/stock/list/share/",
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    }
    params = {
        "jsonCallBack": "jsonpCallback66942",
        "isPagination": "true",
        "stockCode": "",
        "csrcCode": "",
        "areaName": "",
        "stockType": indicator_map[indicator],
        "pageHelp.cacheSize": "1",
        "pageHelp.beginPage": "1",
        "pageHelp.pageSize": "2000",
        "pageHelp.pageNo": "1",
        "pageHelp.endPage": "11",
        "_": "1589881387934",
    }
    r = requests.get(URL_SH, params=params, headers=headers)
    text_data = r.text
    json_data = json.loads(text_data[text_data.find("{"):-1])
    temp_df = pd.DataFrame(json_data["result"])
    temp_df.columns = [
        '-',
        '公司简称',
        '-',
        '-',
        '-',
        '-',
        '-',
        '-',
        '-',
        '简称',
        '代码',
        '-',
        '-',
        '公司代码',
        '-',
        '上市日期',
    ]
    temp_df = temp_df[[
        '公司代码',
        '公司简称',
        '代码',
        '简称',
        '上市日期',
    ]]
    temp_df['上市日期'] = pd.to_datetime(temp_df['上市日期']).dt.date
    return temp_df


def stock_info_cn_sz_list(indicator: str = "A") -> pd.DataFrame:
    '''
    获取深圳证券交易所股基本信息 
    A = A股列表, B = B股列表, CDR = CDR列表, AB = AB股列表
    :param indicator: choice of A/B/AB
    :type indicator: str
    :return: indicator date result
    :rtype: pandas.DataFrame
    '''
    indicator_map = {"A": "tab1", "B": "tab2", "CDR": "tab3", "AB": "tab4"}
    params = {
        "SHOWTYPE": "xlsx",
        "CATALOGID": "1110",
        "TABKEY": indicator_map[indicator],
        "random": "0.6935816432433362",
    }
    r = requests.get(URL_SZ, params=params)

    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        temp_df = pd.read_excel(BytesIO(r.content))
        # temp_df.to_excel('a.xlsx')

    if len(temp_df) > 10:
        if indicator == "A":
            temp_df["A股代码"] = (temp_df["A股代码"].astype(str).str.split(
                ".",
                expand=True).iloc[:, 0].str.zfill(6).str.replace("000nan", ""))
            temp_df = temp_df[[
                "板块",
                "A股代码",
                "A股简称",
                "A股上市日期",
                "A股总股本",
                "A股流通股本",
                "所属行业",
            ]]
        elif indicator == "B":
            temp_df["B股代码"] = (temp_df["B股代码"].astype(str).str.split(
                ".",
                expand=True).iloc[:, 0].str.zfill(6).str.replace("000nan", ""))
            temp_df = temp_df[[
                "板块",
                "B股代码",
                "B股简称",
                "B股上市日期",
                "B股总股本",
                "B股流通股本",
                "所属行业",
            ]]
        elif indicator == "AB":
            temp_df["A股代码"] = (temp_df["A股代码"].astype(str).str.split(
                ".",
                expand=True).iloc[:, 0].str.zfill(6).str.replace("000nan", ""))
            temp_df["B股代码"] = (temp_df["B股代码"].astype(str).str.split(
                ".",
                expand=True).iloc[:, 0].str.zfill(6).str.replace("000nan", ""))
            temp_df = temp_df[[
                "板块",
                "A股代码",
                "A股简称",
                "A股上市日期",
                "B股代码",
                "B股简称",
                "B股上市日期",
                "所属行业",
            ]]
    # print(temp_df)
    return temp_df


def stock_info_cn_list() -> pd.DataFrame:
    from openfc import db
    import time

    all_df = pd.DataFrame()
    last_update_time, all_df = db.db_load('stock_info_all')

    # update time within 24H
    if time.time() - last_update_time > 60 * 60 * 24:
        all_df = pd.DataFrame()
        stock_sh = stock_info_cn_sh_list(indicator="A")
        stock_sh = stock_sh[["公司代码", "公司简称"]]

        stock_sz = stock_info_cn_sz_list(indicator="A")
        stock_sz = stock_sz[["A股代码", "A股简称"]]
        stock_sz.columns = ["公司代码", "公司简称"]

        stock_kc = stock_info_cn_sh_list(indicator="C")
        stock_kc = stock_kc[["公司代码", "公司简称"]]

        all_df = pd.concat([all_df, stock_sz], ignore_index=True)
        all_df = pd.concat([all_df, stock_sh], ignore_index=True)
        all_df = pd.concat([all_df, stock_kc], ignore_index=True)
        all_df.columns = ["code", "name"]

        db.db_save('stock_info_all', all_df)
        print("stock_info_all load form net")
    else:
        print("stock_info_all load form db, last update time = {}".format(
            last_update_time))
        pass

    return all_df


def socket_info_get_name_by_code():
    pass


def socket_info_get_code_by_name():
    pass


if __name__ == "__main__":
    pass

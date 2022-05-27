#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
import requests
import datetime
import showlog
import time
import json


def add_spread(
        cookie: str,
        cb_id: str = None,
        cc_id: str = None,
        cost: float = 0,
        force_chapter: int = 1,
        force_desktop: str = '2',
        is_batch: str = '1',
        name: str = None,
        page_name: str = None,
        num: int = 1,
        page: str = 'read',
        _type: int = 2
) -> json:
    """
    快应用：获取推广链接
    :param cookie: cookie
    :param cb_id: 书籍id
    :param cc_id: 章节id
    :param cost: 推广成本
    :param force_chapter: 强关章节
    :param force_desktop: 强加设置（1：不设置强加；2：主动加桌）
    :param is_batch: 批量链接（0：不生成批量；1：生成批量链接）
    :param name: "2021-06-26 16:42:01" # 渠道名称，默认为时间
    :param page_name: 章节名称，格式为：书籍名+章节名称，例如："《护身高手在校园》第四章 遭围堵"
    :param num: 批量链接条数
    :param page:
    :param _type:
    """
    url = 'https://open.yuewen.com/api/QuickSpread/addSpread'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Cookie": cookie,
        "Host": "open.yuewen.com",
        "Origin": "https://open.yuewen.com",
        "Referer": "https://open.yuewen.com/new/library",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
    }
    if name is None:
        name = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {
        'cbid': cb_id,
        'ccid': cc_id,
        'cost': cost,
        'force_chapter': force_chapter,
        'force_desktop': force_desktop,
        'isBatch': is_batch,
        'name': name,
        'num': num,
        'page': page,
        'page_name': page_name,
        'type': _type
    }
    while True:
        try:
            response = requests.request(
                method='POST',
                url=url,
                headers=headers,
                json=data
            )
            return response.json()
        except:
            showlog.warning(':( 请求发生了错误，将在1秒后重试，可能是网络超时了...')
            time.sleep(1)

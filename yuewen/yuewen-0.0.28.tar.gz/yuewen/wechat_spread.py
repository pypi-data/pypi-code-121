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
import json
import time


def add_h5_spread(
        cookie: str,
        bottom_qr: int = 1,
        cb_id: str = None,
        cc_id: str = None,
        channel_type: int = 1,
        cost: float = 0,
        force_chapter: int = 1,
        force_style: str = '3',
        name: str = None,
        page_name: str = None
) -> json:
    """
    微信分销：获取H5链接
    :param cookie: cookie
    :param bottom_qr: 底部关注引导（0：关闭 1：开启）
    :param cb_id: 书籍id
    :param cc_id: 章节id
    :param channel_type: 内外推类别（1:微信外推广 2:微信内推广）
    :param cost: 推广成本
    :param force_chapter: 强关章节
    :param force_style: 关注选项：3:强制关注,2:主动关注,1:不设置强关
    :param name: "2021-06-26 16:42:01" # 渠道名称，默认为时间
    :param page_name: 章节名称，格式为：书籍名+章节名称，例如："《护身高手在校园》第四章 遭围堵"
    """
    url = 'https://open.yuewen.com/api/wechatspread/addH5Spread'
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
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }
    if name is None:
        name = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {
        'bottom_QR': bottom_qr,
        'cbid': cb_id,
        'ccid': cc_id,
        'channel_type': channel_type,
        'cost': cost,
        'force_chapter': force_chapter,
        'force_style': force_style,
        'name': name,
        'page_name': page_name
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

#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
import requests
from .yuewen import switch_app
import showlog
import time


def get_left_resource(
        cookie: str,
        resource_type: int = 1,
        app_id: str = None,  # 按照app_id切换（优先）
        app_name: str = None,  # 按照app_name切换
        time_out: int = 5
):
    """
    微信分销：推广运营-营销道具-道具发放（获取余量）

    resource_type：
        1：书券
        3：满赠优惠券
        4：满减购物券
    成功返回：{'status': True, 'code': 0, 'msg': '操作成功', 'data': 3955}
    """
    switch_res = switch_app(
        cookie=cookie,
        app_id=app_id,
        app_name=app_name,
        time_out=time_out
    )
    if switch_res['status'] is False:
        return switch_res
    else:
        pass
    url = f'https://open.yuewen.com/api/WechatActivity/getLeftResource?type={resource_type}'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "open.yuewen.com",
        "Referer": "https://open.yuewen.com/new/promotion/Marketingprops",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X -1_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    }
    while True:
        try:
            response = requests.request(
                method='GET',
                url=url,
                headers=headers,
                timeout=time_out
            )
            response_json = response.json()
            return response_json
        except:
            showlog.warning(':( 请求发生了错误，将在1秒后重试，可能是网络超时了...')
            time.sleep(1)


def resource_send_submit(
        cookie: str,
        open_id: str = None,
        num: str = '1',  # 发放数量
        desc: str = '活动',  # 发放原因
        resource_type: int = 1,  # 道具类型
        expire: int = 7,  # 有效期(天)
        app_id: str = None,  # 按照app_id切换（优先）
        app_name: str = None,  # 按照app_name切换
        time_out: int = 5
):
    """
    微信分销：推广运营-营销道具-道具发放-自助发放-单用户发放

    resource_type：
        1：书券
        3：满赠优惠券
        4：满减购物券

    成功返回：{'status': True, 'code': 0, 'msg': '操作成功', 'data': ''}
    """
    switch_res = switch_app(
        cookie=cookie,
        app_id=app_id,
        app_name=app_name,
        time_out=time_out
    )
    if switch_res['status'] is False:
        return switch_res
    else:
        pass
    url = 'https://open.yuewen.com/api/WechatActivity/resourceSendSubmit'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Cookie": cookie,
        "Host": "open.yuewen.com",
        "Origin": "https://open.yuewen.com",
        "Referer": "https://open.yuewen.com/new/promotion/Marketingprops",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X -1_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    }
    data = {
        "openid": open_id,
        "num": num,
        "desc": desc,
        "type": resource_type,
        "expire": expire
    }
    while True:
        try:
            response = requests.request(
                method='POST',
                url=url,
                headers=headers,
                json=data,
                timeout=time_out
            )
            response_json = response.json()
            return response_json
        except:
            showlog.warning(':( 请求发生了错误，将在1秒后重试，可能是网络超时了...')
            time.sleep(1)

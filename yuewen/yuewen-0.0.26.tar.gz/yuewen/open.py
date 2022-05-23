#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
import lazysdk
import hashlib
import time

default_start_time = 1262275200  # 2010-01-01 00:00:00


class Basics:
    """
    支持的阅文产品：
    coop_type 业务类型
            1：微信分销
            9：陌香快应用（共享包）
            11：快应用（独立包）
    """
    def __init__(
            self,
            email: str,
            app_secret: str,
            coop_type: int = 1,
            version: int = 1
    ):
        self.email = email
        self.version = version
        self.app_secret = app_secret
        self.coop_type = coop_type

    def make_sign(
            self,
            data: dict
    ):
        """
        签名算法，快应用和公众号的相同
        """
        keys = list(data.keys())
        keys.sort()  # 升序排序
        data_str = self.app_secret
        for key in keys:
            if key == 'sign':
                pass
            else:
                value = data.get(key)
                key_value = '%s%s' % (key, value)
                data_str += key_value
        d5 = hashlib.md5()
        d5.update(data_str.encode(encoding='UTF-8'))
        return d5.hexdigest().upper()

    def get_app_list(
            self,
            start_time: int = default_start_time,  # 2010-01-01 00:00:00
            end_time: int = None,  # 当前时间
            page: int = 1
    ):
        """
        获取产品列表
        coop_type 业务类型
            1：微信分销
            9：陌香快应用（共享包）
            11：快应用（独立包）
        """
        if end_time is None:
            end_time = int(time.time())
        url = 'https://open.yuewen.com/cpapi/wxRecharge/getapplist'
        data = {
            'email': self.email,  # 必填
            'version': self.version,  # 必填
            'timestamp': int(time.time()),  # 必填
            'start_time': start_time,
            'end_time': end_time,
            'page': page,
            'coop_type': self.coop_type
        }
        sign = self.make_sign(data=data)
        data['sign'] = sign
        response = lazysdk.lazyrequests.lazy_requests(
            url=url,
            method='GET',
            params=data,
            return_json=True
        )
        return response

    def query_user_info(
            self,
            start_time: int,  # 查询起始时间戳
            end_time: int,  # 查询结束时间戳（开始结束时间间隔不能超过7天）
            app_flags: str,  # 产品标识（可从后台公众号设置 > 授权管理获取），可传多个，至多不超过100个，用英文逗号分隔。必须是微信分销对应的appflags
            page: int = 1,  # 分页，默认为1
            openid: str = None,  # 用户ID
            next_id: str = None,  # 上一次查询返回的next_id，分页大于1时必传
    ):
        """
        获取用户信息
        注：
            1.此接口有调用频率限制，相同查询条件每分钟仅能请求一次
            2.单页返回 100 条数据
        """
        if self.coop_type == 1:
            url = 'https://open.yuewen.com/cpapi/WxUserInfo/QueryUserInfo'
        elif self.coop_type == 9:
            url = 'https://open.yuewen.com/cpapi/WxUserInfo/QuickAppQueryUserInfo'
        elif self.coop_type == 11:
            url = 'https://open.yuewen.com/cpapi/WxUserInfo/QuickAppFbQueryUserInfo'
        else:
            return
        data = {
            'email': self.email,  # 必填
            'version': self.version,  # 必填
            'timestamp': int(time.time()),  # 必填
            'start_time': start_time,
            'end_time': end_time,
            'page': page,
            'appflags': app_flags
        }
        if openid is not None:
            data['openid'] = openid
        if next_id is not None:
            data['next_id'] = next_id
        sign = self.make_sign(data=data)
        data['sign'] = sign
        response = lazysdk.lazyrequests.lazy_requests(
            url=url,
            method='GET',
            params=data,
            return_json=True
        )
        return response

    def query_charge_log(
            self,
            start_time: int = default_start_time,  # 2010-01-01 00:00:00
            end_time: int = None,  # 当前时间
            page: int = 1,
            app_flags: str = None,  # 不传时获取所有，传入时以逗号分隔
            openid: str = None,
            guid: str = None,
            order_id: str = None,
            order_status: int = None,
            last_min_id: int = None,
            last_max_id: int = None,
            total_count: int = None,
            last_page: int = None
    ):
        """
        获取充值记录
        """
        if end_time is None:
            end_time = int(time.time())
        data = {
            'email': self.email,  # 必填
            'version': self.version,  # 必填
            'timestamp': int(time.time()),  # 必填
            'start_time': start_time,
            'end_time': end_time,
            'page': page,
            'coop_type': self.coop_type
        }

        if int(self.coop_type) == 1:
            url = 'https://open.yuewen.com/cpapi/wxRecharge/querychargelog'
        elif int(self.coop_type) == 9:
            url = 'https://open.yuewen.com/cpapi/wxRecharge/quickappchargelog'
        elif int(self.coop_type) == 11:
            url = 'https://open.yuewen.com/cpapi/wxRecharge/quickappchargelog'
        else:
            return

        if app_flags is not None:
            data['appflags'] = app_flags
        if openid is not None:
            data['openid'] = openid
        if guid is not None:
            data['guid'] = guid
        if order_id is not None:
            data['order_id'] = order_id
        if order_status is not None:
            data['order_status'] = order_status
        if last_min_id is not None:
            data['last_min_id'] = last_min_id
        if last_max_id is not None:
            data['last_max_id'] = last_max_id
        if total_count is not None:
            data['total_count'] = total_count
        if last_page is not None:
            data['last_page'] = last_page
        sign = self.make_sign(data=data)
        data['sign'] = sign  # 必填
        response = lazysdk.lazyrequests.lazy_requests(
            url=url,
            method='GET',
            params=data,
            return_json=True
        )
        return response

    def query_consume_log(
            self,
            start_time: int = default_start_time,  # 2010-01-01 00:00:00
            end_time: int = None,  # 当前时间
            page: int = 1,
            app_flag: str = None,  # 不传时获取所有，传入时以逗号分隔
            openid: str = None,
            guid: str = None
    ):
        """
        获取消费记录
        返回：
        {
            'code': 0,
            'data': {
                'list': [

                ],
                'page': 1,
                'total_count': 0
            },
            'msg': '成功'
        }
        """
        if end_time is None:
            end_time = int(time.time())
        data = {
            'email': self.email,  # 必填
            'version': self.version,  # 必填
            'timestamp': int(time.time()),  # 必填
            'start_time': start_time,
            'end_time': end_time,
            'page': page,
            'coop_type': self.coop_type
        }

        if int(self.coop_type) == 1:
            url = 'https://open.yuewen.com/cpapi/WxConsume/QueryConsumeLog'
        elif int(self.coop_type) == 9:
            url = 'https://open.yuewen.com/cpapi/WxConsume/QuickAppQueryConsumeLog'
        elif int(self.coop_type) == 11:
            url = 'https://open.yuewen.com/cpapi/WxConsume/QuickAppQueryConsumeLog'
        else:
            return

        if app_flag is not None:
            data['appflag'] = app_flag
        if openid is not None:
            data['openid'] = openid
        if guid is not None:
            data['guid'] = guid
        sign = self.make_sign(data=data)
        data['sign'] = sign  # 必填
        response = lazysdk.lazyrequests.lazy_requests(
            url=url,
            method="GET",
            params=data,
            return_json=True
        )
        return response

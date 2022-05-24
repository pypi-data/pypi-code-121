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


def app_list(
        base_info: dict = None,
        email: str = None,
        app_secret: str = None,
        coop_type: int = 1,
        version: int = 1,
        start_time: int = default_start_time,  # 2010-01-01 00:00:00
        end_time: int = None,  # 当前时间
        page: int = 1,
        get_all: bool = False  # 是否获取所有数据
):
    """
    获取app列表
    :param base_info: 基本信息，包含email、app_secret、coop_type、version；
    :param email: 邮箱
    :param app_secret: 密钥
    :param coop_type: 合作类型，默认为1；
    :param version: 接口版本，默认版本为1；

    :param start_time: 开始时间，时间戳格式；
    :param end_time: 结束时间，时间错格式；
    :param page: 页码，默认值为1，从第1页获取；
    :param get_all: 是否获取所有数据，为False不获取全部数据，只获取指定页；为True获取全部数据，获取全部页；
    """
    # ------------------- 初始化实例 -------------------
    if email is None:
        email = base_info.get('email')
    if app_secret is None:
        app_secret = base_info.get('app_secret')
    if coop_type is None:
        coop_type = base_info.get('coop_type')
    if version is None:
        version = base_info.get('version')
    local_basic = Basics(
        email=email,
        app_secret=app_secret,
        coop_type=coop_type,
        version=version
    )
    # ------------------- 初始化实例 -------------------
    if get_all is False:
        return local_basic.get_app_list(
            start_time=start_time,
            end_time=end_time,
            page=page,
        )
    else:
        temp_page = 1
        temp_data_total_count = 0
        app_all = list()
        while True:
            app_list_response = local_basic.get_app_list(
                start_time=start_time,
                end_time=end_time,
                page=page
            )
            if app_list_response.get('code') == 0:
                data = app_list_response.get('data')
                # data_page = data.get('page')
                total_count = data.get('total_count')
                data_list = data.get('list')

                app_all.extend(data_list)
                temp_data_total_count += len(data_list)
                if temp_data_total_count >= total_count:
                    return app_all
                else:
                    temp_page += 1
            else:
                return app_all


def query_consume_log(
        base_info: dict = None,
        email: str = None,
        app_secret: str = None,
        coop_type: int = 1,
        version: int = 1,
        start_time: int = default_start_time,  # 2010-01-01 00:00:00
        end_time: int = None,  # 当前时间
        page: int = 1,
        app_flag: str = None,  # 不传时获取所有，传入时以逗号分隔
        openid: str = None,
        guid: str = None
):
    """
    获取消费记录
    :param base_info: 基本信息，包含email、app_secret、coop_type、version；
    :param email: 邮箱
    :param app_secret: 密钥
    :param coop_type: 合作类型，默认为1；
    :param version: 接口版本，默认版本为1；

    :param start_time: 开始时间，时间戳格式；
    :param end_time: 结束时间，时间错格式；
    :param page: 页码，默认值为1，从第1页获取；
    :param app_flag: 不传时获取所有，传入时以逗号分隔
    :param openid: 不传时获取所有，传入时以逗号分隔
    :param guid: 不传时获取所有，传入时以逗号分隔
    """
    # ------------------- 初始化实例 -------------------
    if email is None:
        email = base_info.get('email')
    if app_secret is None:
        app_secret = base_info.get('app_secret')
    if coop_type is None:
        coop_type = base_info.get('coop_type')
    if version is None:
        version = base_info.get('version')
    local_basic = Basics(
        email=email,
        app_secret=app_secret,
        coop_type=coop_type,
        version=version
    )
    # ------------------- 初始化实例 -------------------
    return local_basic.query_consume_log(
        start_time=start_time,
        end_time=end_time,
        page=page,
        app_flag=app_flag,
        openid=openid,
        guid=guid
    )

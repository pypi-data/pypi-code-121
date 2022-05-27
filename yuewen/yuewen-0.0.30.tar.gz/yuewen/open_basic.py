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
"""
模块介绍：
    1、阅文平台的开放接口封装的sdk，方便快速使用；
    2、目前支持的产品类型为：微信分销、快应用，需要注意coop_type一定要填写正确；
    3、生成验证密钥的必要参数是：email、app_secret、coop_type、version，这些参数在Basics类的__init__中有详细的定义；
    
使用方法：
    Basics类封装了生成签名的方法和基础接口的调用方法，使用类之前要实例化，然后调用即可；
"""


class Basics:
    """
    基础类，用来实现基本的功能，单个账号的情况下可以直接使用，多账号的情况下建议使用外部的快捷方法。
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
        """
        :param email: 【必填】邮箱
        :param app_secret: 【必填】密钥
        :param coop_type: 业务类型：1-微信分销，9-陌香快应用（共享包），11-快应用（独立包）
        :param version: 接口版本号，默认为1
        """
        self.email = email
        self.version = version
        self.app_secret = app_secret
        self.coop_type = coop_type

    def make_sign(
            self,
            data: dict = None
    ) -> str:
        """
        签名算法，快应用和公众号的相同
        :param data: 需要制作签名的数据
        """
        if data is None:
            data = {}
        keys = list(data.keys())
        keys.sort()  # 升序排序
        data_str = self.app_secret
        for key in keys:
            if key == 'sign':
                # 忽略sign字段
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
            start_time: int = default_start_time,
            end_time: int = None,
            page: int = 1,
            coop_type: int = None
    ):
        """
        获取产品列表
        :param start_time: 查询起始时间戳，查询时间段内更新的产品
        :param end_time: 查询结束时间戳，不传默认取 24 小时内更新的产品
        :param page: 分页，默认为 1
        :param coop_type: 业务类型，默认为 1 微信分销

        返回值：
            接口字段 类型 说明
            page Int 查询的页码
            total_count Int 查询结果集数量
            list Array 结果集数组
            app_name String 产品名称
            appflag String 产品标识
        """
        if end_time is None:
            end_time = int(time.time())
        url = 'https://open.yuewen.com/cpapi/wxRecharge/getapplist'
        data = {
            'email': self.email,
            'version': self.version,
            'timestamp': int(time.time()),
            'start_time': start_time,
            'end_time': end_time,
            'page': page
        }
        if coop_type is None:
            data['coop_type'] = self.coop_type
        else:
            data['coop_type'] = coop_type
        sign = self.make_sign(data=data)
        data['sign'] = sign
        response = lazysdk.lazyrequests.lazy_requests(
            url=url,
            method='GET',
            params=data,
            return_json=True
        )
        return response

    def query_consume_log(
            self,
            start_time: int = None,
            end_time: int = None,
            page: int = 1,
            app_flag: str = None,  # 不传时获取所有，传入时以逗号分隔
            openid: str = None,
            guid: str = None
    ):
        """
        获取消费记录
        注：
            1.此接口有调用频率限制，相同查询条件每分钟仅能请求一次
            2.单页返回 100 条数据

        :param start_time: 查询起始时间戳（近支持最近半年的消费记录查询、时间跨度不能超过一个月），默认值为180天以前
        :param end_time: 查询结束时间戳
        :param page: 分页，默认为 1
        :param app_flag: 产品标识（可从后台公众号设置 > 授权管理获取）
        :param openid: 用户 ID（openid、guid 必传其一）
        :param guid: 阅文用户 ID

        微信分销 返回值：
            接口字段 类型 说明
            page Int 查询的页码
            maxPage Int 查询的页数
            appflag String 产品标识
            openid String 用户 ID
            order_id String 订单号
            totalAmount Int 消费有价币总金额
            freeAmount Int 消费免费币总金额
            consumeTime Long 时间戳（毫秒）
            cbid Long 订阅书籍 id
            book_name String 书籍名称
            ccid Long 章节 id
            chapter_name String 章节名称

        快应用 返回值：
            接口字段 类型 说明
            page Int 查询的页码
            total_count Int 查询的页数
            openid String 用户 ID
            orderid String 订单号
            worth_amount Int 消费有价币总金额
            free_amount Int 消费免费币总金额
            consume_time Long 时间戳（毫秒）
            cbid Long 订阅书籍 id
            book_name String 书籍名称
            ccid Long 章节 id
            chapter_name String 章节名称

        返回结构：
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
        if start_time is None:
            start_time = int(time.time()) - (180 * 86400)
        data = {
            'email': self.email,  # 必填
            'version': self.version,  # 必填
            'timestamp': int(time.time()),  # 必填
            'start_time': start_time,
            'end_time': end_time,
            'page': page,
            # 'coop_type': self.coop_type
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

    def query_user_info(
            self,
            app_flags: str,
            start_time: int = None,
            end_time: int = None,
            page: int = 1,
            openid: str = None,
            next_id: str = None,
    ):
        """
        获取用户信息
        注：
            1.此接口有调用频率限制，相同查询条件每分钟仅能请求一次
            2.单页返回 100 条数据

        :param app_flags: 产品标识（可从后台公众号设置 > 授权管理获取），可传多个，至多不超过100个，用英文逗号分隔。必须是微信分销对应的appflags
        :param start_time: 查询起始时间戳
        :param end_time: 查询结束时间戳（开始结束时间间隔不能超过 7 天）
        :param page: 分页，默认为 1
        :param openid: 用户ID
        :param next_id: 上一次查询返回的next_id，分页大于1时必传

        微信分销 返回值：
            接口字段 类型 说明
            page Int 查询的页码
            next_id String 下一页 id
            total_count Int 查询的结果集数量
            appflag String 产品标识
            openid String 用户 ID
            charge_amount Int 累计充值金额
            charge_num Int 累计充值次数
            create_time String 注册时间
            guid Int 阅文用户 id
            is_subscribe Int 是否关注
            nickname String 用户昵称
            sex Int 用户性别
            source String 用户来源
            subscribe_time String 最近关注时间
            vip_end_time String 包年结束时间
            seq_time String 用户染色时间 （快应用分销返回）
            channel_id Int 推广链接 ID（用户染色来源）
            channel_name String 推广链接名称（用户染色来源）
            book_id Long 推广书籍 ID（用户染色来源）
            book_name String 推广书籍名称（用户染色来源）
            update_time String 更新时间

        快应用 返回值：
            接口字段 类型 说明
            page Int 查询的页码
            next_id String 下一页 id
            total_count Int 查询结果集数量
            appflag String 产品标识
            app_name String 产品名称
            openid String 用户 ID
            charge_amount Int 累计充值金额
            charge_num Int 累计充值次数
            guid Int 阅文用户 id
            reg_time String 用户注册时间
            seq_time String 用户染色时间 （快应用分销返回）
            channel_id Int 推广链接 ID（用户染色来源）
            channel_name String 推广链接名称（用户染色来源）
            book_id Long 推广书籍 ID（用户染色来源）
            book_name String 推广书籍名称（用户染色来源）
            manufacturer String 用户设备品牌
        """
        if start_time is None:
            start_time = int(time.time()) - 7 * 86400
        if end_time is None:
            end_time = int(time.time())

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

    def get_novel_info_by_cbid(
            self,
            app_flags: str,
            cbid: int,
    ):
        """
        获取书籍信息
        注：
            1.此接口有调用频率限制，相同查询条件每分钟仅能请求一次

        :param app_flags: 【必填】
            对于微信分销：产品标识（可从后台公众号设置 > 授权管理获取），可传多个，至多不超过100个，用英文逗号分隔。必须是微信分销对应的appflags
            对于快应用：产品标识，必须是快应用对应的 appflags
        :param cbid: 【必填】作品唯一标识

        返回值：
            接口字段 类型 说明
            cbid Long 作品唯一标识
            title String 书名
            author_name String 作者名称
            all_words Int 作品当前全部正文章节的字数
            update_time String 最近一个章节的更新时间
            charge_chapter Int 收费起始章节
        """
        url = 'https://open.yuewen.com/cpapi/wxNovel/getNovelInfoByCbid'
        data = {
            'email': self.email,  # 必填
            'version': self.version,  # 必填
            'timestamp': int(time.time()),  # 必填
            'cbid': cbid,
            'appflags': app_flags
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

    def get_free_chapter_list_by_cbid(
            self,
            app_flags: str,
            cbid: int,
    ):
        """
        获取书籍免费章节列表
        注：
            1.此接口有调用频率限制，相同查询条件每分钟仅能请求一次

        :param app_flags: 【必填】产品标识（可从后台公众号设置 > 授权管理获取），可传多个，至多不超过100个，用英文逗号分隔。必须是微信分销对应的appflags
        :param cbid: 【必填】作品唯一标识

        返回值：
            接口字段 类型 说明
            cbid Long 作品唯一标识
            chapter_list Array 章节列表
            ccid Int 章节 id
            chapter_seq Int 章节序号
            chapter_title String 章节名
        """
        url = 'https://open.yuewen.com/cpapi/wxNovel/getFreeChapterListByCbid'
        data = {
            'email': self.email,  # 必填
            'version': self.version,  # 必填
            'timestamp': int(time.time()),  # 必填
            'cbid': cbid,
            'appflags': app_flags
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

    def add_h5_spread(
            self,
            app_flags: str,
            cbid: int,
            ccid: int,
            name: str,
            channel_type: int,
            force_style: int,
            bottom_QR: int,
            force_chapter: str,
            cost: float = 0.00
    ):
        """
        生成小说推广链接（适用于微信分销）
        注：
            1.此接口有调用频率限制，相同查询条件每分钟仅能请求一次

        :param app_flags: 【必填】产品标识（可从后台公众号设置 > 授权管理获取），可传多个，至多不超过100个，用英文逗号分隔。必须是微信分销对应的appflags
        :param cbid: 【必填】作品唯一标识
        :param ccid: 【必填】章节 id
        :param name: 【必填】渠道名称
        :param channel_type: 推广类型 1 外部 2 内部
        :param force_style: 强关设置 1 不设置强关 2 主动关注 3 强制关注
        :param bottom_QR: 底部关注 1 是 2 否
        :param force_chapter: 强关章节序号
        :param cost: 推广成本(保留小数点后两位)

        返回值：
            接口字段 类型 说明
            cbid Long 作品唯一标识
            chapter_list Array 章节列表
            ccid Int 章节 id
            chapter_seq Int 章节序号
            chapter_title String 章节名
        """
        url = 'https://open.yuewen.com/cpapi/wxNovel/AddH5Spread'
        data = {
            'email': self.email,  # 必填
            'version': self.version,  # 必填
            'timestamp': int(time.time()),  # 必填
            'appflags': app_flags,
            'cbid': cbid,
            'ccid': ccid,
            'name': name,
            'channel_type': channel_type,
            'force_style': force_style,
            'bottom_QR': bottom_QR,
            'force_chapter': force_chapter,
            'cost': cost
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

    def add_page_spread(
            self,
            app_flags: str,
            name: str,
            channel_type: int,
            page_type: int,
            cost: float = 0.00
    ):
        """
        生成小说推广链接（适用于微信分销）
        注：
            1.此接口有调用频率限制，相同查询条件每分钟仅能请求一次

        :param app_flags: 【必填】产品标识（可从后台公众号设置 > 授权管理获取），可传多个，至多不超过100个，用英文逗号分隔。必须是微信分销对应的appflags
        :param name: 【必填】渠道名称
        :param channel_type: 推广类型 1 外部 2 内部
        :param page_type:
            1 书城首页,
            2 排行榜(自动)
            3 排行榜(男生)
            4 排行榜(女生)
            5 充值页
            6 最近阅读(列表)
            7 限免专区
            8 签到页面
            9 个人中心
            10 置顶公众号引导
        :param cost: 推广成本(保留小数点后两位)

        返回值：
            接口字段 类型 说明
            channel_url String 页面推广链接
        """
        url = 'https://open.yuewen.com/cpapi/wxNovel/addPageSpread'
        data = {
            'email': self.email,  # 必填
            'version': self.version,  # 必填
            'timestamp': int(time.time()),  # 必填
            'appflags': app_flags,
            'name': name,
            'channel_type': channel_type,
            'page_type': page_type,
            'cost': cost
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

    def add_quick_spread(
            self,
            app_flags: str,
            cbid: int,
            ccid: int,
            name: str,
            force_chapter: str,
            force_desktop: str,
            cost: float = 0.00
    ):
        """
        创建小说推广链接（适用于快应用）
        注：
            1.此接口有调用频率限制，相同查询条件每分钟仅能请求一次

        :param app_flags: 【必填】产品标识，必须是后台或接口对应的 appflags
        :param cbid: 作品唯一标识
        :param ccid: 章节 id
        :param name: 【必填】渠道名称
        :param force_chapter: 强关章节序号
        :param force_desktop: 1 不主动加桌 , 2 主动加桌
        :param cost: 推广成本(保留小数点后两位)

        返回值：
            接口字段 类型 说明
            hap_url String hap 小说推广链接
            h5_url String h5 小说推广链接
            url_id Int 链接 id
        """
        url = 'https://open.yuewen.com/cpapi/wxNovel/addQuickSpread'
        data = {
            'email': self.email,
            'version': self.version,
            'timestamp': int(time.time()),
            'appflags': app_flags,
            'cbid': cbid,
            'ccid': ccid,
            'name': name,
            'force_chapter': force_chapter,
            'force_desktop': force_desktop,
            'cost': cost
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

    def add_recharge_template(
            self,
            app_flags: str,
            activity_name: str,
            activity_theme: int,
            recharge_amount: float,
            gift_amount: int,
            recharge_count: int,
            start_time: int,
            end_time: int,
            display: int,
            time_is_show: int,
            name: str,
            channel_type: int
    ):
        """
        创建模板充值活动
        注：
            1.此接口有调用频率限制，相同查询条件每分钟仅能请求一次

        :param app_flags: 【必填】产品标识（可从后台公众号设置 > 授权管理获取），可传多个，至多不超过100个，用英文逗号分隔。必须是微信分销对应的appflags
        :param activity_name: 【必填】活动名称
        :param activity_theme: 活动主题
            1 默认风格
            2 男生风格
            3 女生风格
            4 教师节
            5 中秋节
            6 周末风格
            7 国庆节
            8 重阳节
            9 万圣节
            10 双十一
            11 双十二
            12 圣诞节
            13 元旦
            16 春节
            17 元宵节
            18 情人节
            19 春季踏青
            20 劳动节
            21 端午节
            23 女神节
            24 七夕
        :param recharge_amount: 充值金额
        :param gift_amount: 赠送金额，不传默认为 0
        :param recharge_count: 充值次数，仅可传 1 or 2 or 3
        :param start_time: 活动开始时间（时间戳）
        :param end_time: 活动结束时间（时间戳）
        :param display:
            活动展示位，多个以,分隔
                1 阅读页 banner
                2 客服消息
                3 首页 banner
                4 活动中心
        :param time_is_show: 活动时间是否展示 1 展示 0 不展示
        :param name: 渠道名称
        :param channel_type: 推广类型：1 外部 2 内部，若 name 传值 channel_type 必 传

        返回值：
            接口字段 类型 说明
            url String 活动链接
            channel_url String 页面推广链接
        """
        url = 'https://open.yuewen.com/cpapi/wxActivity/addRechargeTemplate'
        data = {
            'email': self.email,  # 必填
            'version': self.version,  # 必填
            'timestamp': int(time.time()),  # 必填
            'appflags': app_flags,
            'activity_name': activity_name,
            'activity_theme': activity_theme,
            'recharge_amount': recharge_amount,
            'gift_amount': gift_amount,
            'recharge_count': recharge_count,
            'start_time': start_time,
            'end_time': end_time,
            'display': display,
            'time_is_show': time_is_show,
            'name': name,
            'channel_type': channel_type
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

    def query_charge_log(
            self,
            coop_type: int = None,
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
        注：
            1.此接口有调用频率限制，相同查询条件每分钟仅能请求一次
            2.单页返回 100 条数据
            3.查询的时间段不能超过 24 小时
        :param coop_type: 业务类型，必传 11
        :param start_time: 查询起始时间戳
        :param end_time: 查询结束时间戳
        :param page: 分页，默认为 1
        :param app_flags: 产品标识（可从后台获取），不传时查询商户帐号下有权限的所有产品订单；可传多个，用英文逗号分隔
        :param openid: 用户 ID，传此字段时必传对应的 appflags
        :param guid: 阅文用户 ID，传此字段时必传对应的 appflags
        :param order_id: 微信或支付宝订单号
        :param order_status: 订单状态：1 待支付、2 已支付
        :param last_min_id: 上一次查询返回的 min_id，分页大于 1 时必传
        :param last_max_id: 上一次查询返回的 max_id，分页大于 1 时必传
        :param total_count: 上一次查询返回的 total_count，分页大于 1 时必传
        :param last_page: 上一次查询返回的 page，分页大于 1 时必传

        返回值：
            接口字段 类型 说明
            page Int 查询的页码
            total_count Int 查询结果集数量
            min_id Long 最小 Id 用于分页查询
            max_id Long 最大 Id 用于分页查询
            list Array 结果集数组
            app_name String 产品名称
            amount String 充值金额
            order_channel Int 支付渠道：1 支付宝、2 微信
            order_id String 支付订单号
            order_time String 下单时间
            order_status Int 订单状态：1 待支付、2 已支付
            order_type Int 订单类型：1 充值、2 包年
            openid String 用户 ID
            user_name String 用户昵称
            reg_time String 用户注册时间
            seq_time String 用户染色时间
            channel_id Int 推广链接 ID
            channel_name String 推广链接名称
            book_id Long 书籍 ID
            book_name String 书籍名称
        """
        if end_time is None:
            end_time = int(time.time())
        if coop_type is None:
            coop_type = self.coop_type
        data = {
            'email': self.email,  # 必填
            'version': self.version,  # 必填
            'timestamp': int(time.time()),  # 必填
            'start_time': start_time,
            'end_time': end_time,
            'page': page,
            'coop_type': coop_type
        }

        if int(coop_type) == 1:
            url = 'https://open.yuewen.com/cpapi/wxRecharge/querychargelog'
        elif int(coop_type) == 9:
            url = 'https://open.yuewen.com/cpapi/wxRecharge/quickappchargelog'
        elif int(coop_type) == 11:
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

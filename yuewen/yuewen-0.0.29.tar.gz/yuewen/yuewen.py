#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
import requests
import showlog
import json
import time
import re


def get_menu_response(
        cookie: str,
        time_out: int = 5
):
    """
    包含账号信息及子账号列表的菜单信息
    """
    url = 'https://open.yuewen.com/api/account/getMenu'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "open.yuewen.com",
        "Referer": "https://open.yuewen.com/new/dashboard",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    }
    while True:
        try:
            response = requests.request(
                method='GET',
                url=url,
                headers=headers,
                timeout=time_out
            )
            return response.json()
        except:
            showlog.warning(':( 请求发生了错误，将在1秒后重试，可能是网络超时了...')
            time.sleep(1)


def get_menu(
        cookie: str,
        key_name: bool = False,  # 将app名称作为key返回结果
        key_app_id: bool = False,  # 将app_id名称作为key返回结果
        make_list: bool = False,  # 将结果按照list形式返回
        time_out: int = 5
):
    """
    增加对快应用获取的兼容
    注意：在最上层获取coop_id的时候可能会不准确
    coop_id：合作方式代码，1：微信分销，9：陌香快应用（共享包），11：快应用（独立包）
    """
    res = dict()
    temp_list = list()
    menu_response = get_menu_response(
        cookie=cookie,
        time_out=time_out
    )
    if menu_response.get('status') is True:
        data = menu_response.get('data')

        res['email'] = data.get('email')
        res['is_authoriztion'] = data.get('is_authoriztion')
        top = data.get('top')
        for coop_id, coop_info in top.items():
            res['coop_name'] = coop_info.get('name')  # 合作方式名称
            res['coop_id'] = int(coop_id)  # 合作方式id
            coop_apps = coop_info.get('children')  # 合作产品字典
            if make_list is False:
                if key_name is False:
                    res['status'] = True
                    res['code'] = 0
                    res['msg'] = 'ok'
                    res['data'] = coop_apps
                elif key_name is True and key_app_id is False:
                    data_children2 = dict()
                    for key, value in coop_apps.items():
                        value_0 = value.split('|')[0]
                        data_children2[value_0] = key
                    res['status'] = True
                    res['code'] = 0
                    res['msg'] = 'ok'
                    res['data'] = data_children2
            else:
                res['status'] = True
                res['code'] = 0
                res['msg'] = 'ok'
                if len(coop_apps) > 0:
                    for key, value in coop_apps.items():
                        value_0 = value.split('|')[0]
                        temp_list.append({'app_id': key, 'app_name': value_0, 'coop_id': coop_id})
                    res['data'] = temp_list
                else:
                    res['data'] = []
    else:
        res.update(menu_response)
    return res


def switch_app(
        cookie: str,
        app_id: str = None,  # 按照app_id切换（优先）
        app_name: str = None,  # 按照app_name切换
        coop_id: int = None,
        time_out: int = 5
):
    """
    切换app
    """
    res = dict()
    if app_id is not None:
        if coop_id is not None:
            pass
        else:
            menu_res = get_menu(cookie=cookie, key_app_id=True)
            if menu_res['code'] == 0:
                coop_id = menu_res.get('coop_id')
            else:
                return menu_res
    elif app_name is not None:
        menu_res = get_menu(cookie=cookie, key_name=True)
        if menu_res['code'] == 0:
            menu_data = menu_res.get('data')
            app_id = menu_data.get(app_name)
            coop_id = menu_res.get('coop_id')
        else:
            return menu_res
    else:
        res['status'] = True
        res['code'] = 0
        res['msg'] = 'ok，未做任何操作'
        return res
    url = 'https://open.yuewen.com/api/account/switchApp'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Cookie": cookie,
        "Host": "open.yuewen.com",
        "Origin": "https://open.yuewen.com",
        "Referer": "https://open.yuewen.com/new/dashboard",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    }
    data = {
        "coopid": str(coop_id),
        "appid": str(app_id)
    }
    while True:
        try:
            response = requests.request(
                method='POST',
                url=url,
                headers=headers,
                data=json.dumps(data),
                timeout=time_out
            )
            response_json = response.json()
            response_json['app_id'] = app_id
            response_json['coop_id'] = coop_id
            return response_json
        except:
            showlog.warning(':( 请求发生了错误，将在1秒后重试，可能是网络超时了...')
            time.sleep(1)


def adreport_ocean(
        cookie: str,
        app_id: str = None,  # 按照app_id切换（优先）
        app_name: str = None,  # 按照app_name切换
        time_out: int = 5
):
    """
    [广告回传]-[巨量引擎]（页面数据，包含app_flag、触点链接地址）
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

    url = ' https://open.yuewen.com/api/adreport/ocean?site=2'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "open.yuewen.com",
        "Referer": "https://open.yuewen.com/new/putMonitor/bytedanceBack",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
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
            response_json['coop_id'] = switch_res.get('coop_id')
            return response_json
        except:
            showlog.warning(':( 请求发生了错误，将在1秒后重试，可能是网络超时了...')
            time.sleep(1)


def wechat_info(
        cookie: str,
        app_id: str = None,  # 按照app_id切换（优先）
        app_name: str = None,  # 按照app_name切换
        time_out: int = 5
):
    """
    [公众号-快应用设置]-[授权管理]
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

    url = 'https://open.yuewen.com/api/wechat/wechatInfo'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "open.yuewen.com",
        "Referer": "https://open.yuewen.com/new/wechat/authorization",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
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
            response_json['coop_id'] = switch_res.get('coop_id')
            return response_json
        except:
            showlog.warning(':( 请求发生了错误，将在1秒后重试，可能是网络超时了...')
            time.sleep(1)


def get_app_info_simple(
        cookie: str,
        app_id: str = None,  # 按照app_id切换（优先）
        app_name: str = None,  # 按照app_name切换
        time_out: int = 5
):
    """
    获取子产品信息，只返回最简单的信息
    """
    res = list()
    menu_res = get_menu(
        cookie=cookie,
        make_list=True,
        time_out=time_out
    )
    if menu_res['status'] is True:
        coop_id = menu_res['coop_id']
        app_list = menu_res['data']
    else:
        return menu_res

    if app_id is None and app_name is None:
        # 不指定任何子账号，获取所有账号的数据
        task_list = app_list
    else:
        task_list = [{'app_id': app_id, 'app_name': app_name}]

    for task in task_list:
        task_app_id = task.get('app_id')
        task_app_name = task.get('app_name')
        switch_res = switch_app(
            cookie=cookie,
            app_id=task_app_id,
            app_name=task_app_name,
            time_out=time_out
        )
        if switch_res['status'] is False:
            return switch_res
        else:
            temp_dict = dict()
            temp_dict['coop_id'] = coop_id
            if str(coop_id) == '1':
                # 微信分销
                wechat_info_res = wechat_info(
                    cookie=cookie,
                    app_id=task_app_id,
                    app_name=task_app_name,
                    time_out=time_out
                )
                if wechat_info_res['status'] is True:
                    wechat_info_data = wechat_info_res['data']
                    if wechat_info_data['bindStatus'] is True:
                        # 已授权
                        wechatInfo = wechat_info_data['wechatInfo']
                        wechatInfo.pop('permission')
                        temp_dict['data'] = wechatInfo
                        temp_dict['app_id'] = task_app_id
                        temp_dict['app_name'] = task_app_name
                        temp_dict['app_flag'] = wechatInfo.get('appflag')
                    else:
                        # 未授权，提示：以下配置将在公众号审核通过后生效
                        temp_dict['app_id'] = task_app_id
                        temp_dict['app_name'] = task_app_name
                    res.append(temp_dict)

                else:
                    return wechat_info_res
            else:
                # 快应用
                adreport_ocean_res = adreport_ocean(
                    cookie=cookie,
                    app_id=task_app_id,
                    app_name=task_app_name,
                    time_out=time_out
                )
                if adreport_ocean_res['status'] is True:
                    adreport_ocean_data = adreport_ocean_res['data']
                    quick_app_url = adreport_ocean_data['callback_url']
                    app_flag = re.search('appflag=(.*?)&', quick_app_url, re.S).group(1)
                    temp_dict['app_id'] = task_app_id
                    temp_dict['app_name'] = task_app_name
                    temp_dict['app_flag'] = app_flag
                    res.append(temp_dict)
                else:
                    return adreport_ocean_res
    return {'status': True, 'code': 0, 'msg': 'ok', 'data': res}


def wechat_message_service_message_list(
        cookie: str,
        page: int = 1,
        app_id: str = None,  # 按照app_id切换（优先）
        app_name: str = None,  # 按照app_name切换
        time_out: int = 5
):
    """
    获取微信消息客服消息列表
    [推广运营]-[消息推送]-[客服消息]
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

    url = 'https://open.yuewen.com/api/WechatMessage/serviceMessageList?p=%s&title=&start_time=&end_time=&status=' % page
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "open.yuewen.com",
        "Referer": "https://open.yuewen.com/new/promotion/messagePush/customerService",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    }
    while True:
        try:
            response = requests.request(
                method='POST',
                url=url,
                headers=headers,
                timeout=time_out
            )
            response_json = response.json()
            return response_json
        except:
            showlog.warning(':( 请求发生了错误，将在1秒后重试，可能是网络超时了...')
            time.sleep(1)


def edit_kf_msg(
        cookie: str,
        message_id: str,
        app_id: str = None,  # 按照app_id切换（优先）
        app_name: str = None,  # 按照app_name切换
        time_out: int = 5
):
    """
    获取客服消息详情
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

    url = 'https://open.yuewen.com/api/WechatMessage/editkfmsg?id=%s' % message_id
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "open.yuewen.com",
        "Referer": "https://open.yuewen.com/new/promotion/messagePush/customerService",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
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


def cms_upload_img_batch(
        file_dir: str,
        cookie: str,
        app_id: str = None,  # 按照app_id切换（优先）
        app_name: str = None,  # 按照app_name切换
        time_out: int = 5,
        _type: int = 2  # 图片类型 1:书城Banner,2:图文消息
):
    """
    支持 微信公众号
    图片素材 本地上传
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
    url = 'https://open.yuewen.com/api/Cms/uploadImgBatch'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "open.yuewen.com",
        "Origin": "https://open.yuewen.com",
        "Referer": "https://open.yuewen.com/new/wechat/pictureManager",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0"
    }
    files = [
        ('file0', (open(file_dir, 'rb')))
    ]
    payload = {'type': _type}
    while True:
        try:
            response = requests.request(
                method='POST',
                url=url,
                headers=headers,
                files=files,
                data=payload,
                timeout=time_out
            )
            response_json = response.json()
            return response_json
        except:
            showlog.warning(':( 请求发生了错误，将在1秒后重试，可能是网络超时了...')
            time.sleep(1)


def cms_cp_image(
        cookie: str,
        app_id: str = None,  # 按照app_id切换（优先）
        app_name: str = None,  # 按照app_name切换
        time_out: int = 5
):
    """
    支持 微信公众号
    图片素材 查询
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

    url = 'https://open.yuewen.com/api/Cms/cpImage?p=1&type=-1&status=-1'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "open.yuewen.com",
        "Referer": "https://open.yuewen.com/new/wechat/pictureManager",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0"
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


def get_callback_setting(
        cookie: str,
        app_id: str = None,  # 按照app_id切换（优先）
        app_name: str = None,  # 按照app_name切换
        time_out: int = 5,
        site: int = 3  # 3:巨量引擎
):
    """
    [广告回传]-[巨量引擎]（页面数据，包含app_flag、触点链接地址）
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

    menu_res = get_menu(cookie=cookie)
    coop_id = menu_res['coop_id']
    if coop_id == 1:
        # 公众号
        url = 'https://open.yuewen.com/api/adreport/getCallbackSetting?site=%s' % site
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Cookie": cookie,
            "Host": "open.yuewen.com",
            "Referer": "https://open.yuewen.com/new/putMonitor/bytedanceBack",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
        }
        while True:
            try:
                response = requests.get(
                    url=url,
                    headers=headers,
                    timeout=time_out
                )
                response_json = response.json()
                return response_json
            except:
                showlog.warning(':( 请求发生了错误，将在1秒后重试，可能是网络超时了...')
                time.sleep(1)
    else:
        url = 'https://open.yuewen.com/api/adreport/ocean?site=2'
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Cookie": cookie,
            "Host": "open.yuewen.com",
            "Referer": "https://open.yuewen.com/new/putMonitor/bytedanceBack",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
        }
        while True:
            try:
                response = requests.get(
                    url=url,
                    headers=headers,
                    timeout=time_out
                )
                response_json = response.json()
                return response_json
            except:
                showlog.warning(':( 请求发生了错误，将在1秒后重试，可能是网络超时了...')
                time.sleep(1)


def wechat_book_spread(
        cookie: str,
        app_id: str = None,  # 按照app_id切换（优先）
        app_name: str = None,  # 按照app_name切换
        time_out: int = 5,
        page: int = 1
):
    """
    获取作品书库，主要要进入子账号才能获取
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
    url = 'https://open.yuewen.com/api/wechatspread/bookSpread'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "open.yuewen.com",
        "Referer": "https://open.yuewen.com/new/library",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
    }
    data = {
        'cbid': '',
        'title': '',
        'page': page,
        'category1': '',
        'category2': -1,
        'category3': '',
        'isfinish': -1,
        'level': -1
    }
    while True:
        try:
            response = requests.request(
                method='GET',
                url=url,
                headers=headers,
                params=data
            )
            response_json = response.json()
            return response_json
        except:
            showlog.warning(':( 请求发生了错误，将在1秒后重试，可能是网络超时了...')
            time.sleep(1)


def wechat_chapter_spread(
        cookie: str,
        app_id: str = None,  # 按照app_id切换（优先）
        app_name: str = None,  # 按照app_name切换
        cb_id: str = None,
        time_out: int = 5):
    """
    获取书籍章节信息
    获取每章信息
    获取书籍章节ccid
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
    url = 'https://open.yuewen.com/api/wechatspread/chapterSpread?cbid=%s' % cb_id
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "open.yuewen.com",
        "Referer": "https://open.yuewen.com/new/library",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    }
    data = {
        "cbid": cb_id
    }
    while True:
        try:
            response = requests.post(
                url=url,
                headers=headers,
                data=data,
                timeout=5
            )
            return response.json()
        except:
            showlog.warning(':( 请求发生了错误，将在1秒后重试，可能是网络超时了...')
            time.sleep(1)


def statistics(
        cookie: str,
        app_id: str = None,  # 按照app_id切换（优先）
        app_name: str = None,  # 按照app_name切换
        time_out: int = 5,
        page: int = 1,
        start_date: str = '',
        end_date: str = ''
):
    """
    微信分销：总账号-数据统计-公众号汇总统计
    快应用：总账号-数据统计-快应用数据汇总
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

    # 判断账号类型
    get_menu_res = get_menu(
        cookie=cookie,
        time_out=time_out
    )
    coop_id = get_menu_res['coop_id']
    if str(coop_id) == 1:
        # 微信分销
        url = 'https://open.yuewen.com/api/statistics/wxfx?page=%s&type=1&startdate=%s&enddate=%s&appid=' % \
              (page, start_date, end_date)
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Cookie": cookie,
            "Host": "open.yuewen.com",
            "Referer": "https://open.yuewen.com/new/dataStatistics/publicAccountsData",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
        }
    else:
        # 快应用
        url = 'https://open.yuewen.com/api/Statistics/quickStatistics?p=%s&type=day&starttime=%s&endtime=%s&appid=' % \
              (page, start_date, end_date)
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Cookie": cookie,
            "Host": "open.yuewen.com",
            "Referer": "https://open.yuewen.com/new/dataStatistics/quickStatistics",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
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
            response_json['coop_id'] = coop_id
            return response_json
        except:
            showlog.warning(':( 请求发生了错误，将在1秒后重试，可能是网络超时了...')
            time.sleep(1)


def statistics_head(
        cookie: str,
        app_id: str = None,  # 按照app_id切换（优先）
        app_name: str = None,  # 按照app_name切换
        time_out: int = 5
):
    """
    微信分销：数据统计-充值统计（实时）
    快应用：数据统计-充值统计（实时）
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
    url = 'https://open.yuewen.com/api/Statistics/getHeadData?appid=%s' % app_id
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "open.yuewen.com",
        "Referer": "https://open.yuewen.com/new/dataStatistics/rechargeStatistics",
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


def get_promotion_list(
        cookie: str,
        app_id: str = None,  # 按照app_id切换（优先）
        app_name: str = None,  # 按照app_name切换
        coop_id: int = None,
        start_date: str = None,
        end_date: str = None,
        page: int = 1,
        time_out: int = 5
):
    """
    推广运营-作品推广
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
    if coop_id is None:
        coop_id = switch_res.get('coop_id')
    if coop_id == 1:
        url = 'https://open.yuewen.com/api/spread/getPromotionList'
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Cookie": cookie,
            "Host": "open.yuewen.com",
            "Referer": "https://open.yuewen.com/new/promotion/novalPromotion",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
            "sec-ch-ua": "\"Google Chrome\";v=\"93\", \" Not;A Brand\";v=\"99\", \"Chromium\";v=\"93\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        data = {
            'recycle': 0,
            'startdate': start_date,
            'enddate': end_date,
            'name': '',
            'id': '',
            'type': 0,
            'page': page,
            'channeltype': 1,
            'pagename': ''
        }
        while True:
            try:
                response = requests.request(
                    method='GET',
                    url=url,
                    headers=headers,
                    params=data
                )
                return response.json()
            except:
                showlog.warning(':( 请求发生了错误，将在1秒后重试，可能是网络超时了...')
                time.sleep(1)
    else:
        url = 'https://open.yuewen.com/api/QuickSpread/getPromotionList?recycle=0&' \
              'startdate=&enddate=&name=&id=&type=2&p=1&page_name='
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Cookie": cookie,
            "Host": "open.yuewen.com",
            "Referer": "https://open.yuewen.com/new/promotion/novalPromotion",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
            "sec-ch-ua": "\"Google Chrome\";v=\"93\", \" Not;A Brand\";v=\"99\", \"Chromium\";v=\"93\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        data = {
            'recycle': 0,
            'startdate': start_date,
            'enddate': end_date,
            'name': '',
            'id': '',
            'type': 2,
            'p': page,
            'page_name': ''
        }
        while True:
            try:
                response = requests.request(
                    method='GET',
                    url=url,
                    headers=headers,
                    params=data
                )
                return response.json()
            except:
                showlog.warning(':( 请求发生了错误，将在1秒后重试，可能是网络超时了...')
                time.sleep(1)

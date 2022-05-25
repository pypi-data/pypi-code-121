# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/11/4 11:00 上午
# Copyright (C) 2021 The lesscode Team

import threading

import tornado.options
from requests import post, get
from tornado.web import RequestHandler

from lesscode.db.redis.redis_helper import RedisHelper
from lesscode.utils.doc.interface_doc_handler import parser_swagger
from lesscode.web.business_exception import BusinessException
from lesscode.web.status_code import StatusCode
from tornado.options import define

define("route_prefix", default="", type=str, help="路由前缀")
tornado.options.options.route_prefix = ""


class RouterMapping(list):
    """
    RouterMapping 类用于存储访问路径"URL"与处理器之间对应关系集合
    直接继承list
    """

    _instance_lock = threading.Lock()

    def __init__(self):
        super(RouterMapping, self).__init__()
        # 存放类名、处理方法、url 的元祖集合 url为方法上指定路径
        self.dynamicMethods = []
        # 存放url与具体业务处理方法的映射关系（url，function）
        self.handlerMapping = []

    @classmethod
    def instance(cls):
        if not hasattr(RouterMapping, "_instance"):
            with RouterMapping._instance_lock:
                if not hasattr(RouterMapping, "_instance"):
                    RouterMapping._instance = RouterMapping()
        return RouterMapping._instance


def Handler(url: str, desc=""):
    """
    RequestHandler对应路径注册装饰器，完成处理类与url对应注册。
    :param prefix: 路由前缀
    :param url:
    :return:
    """
    route_prefix = tornado.options.options.route_prefix

    def wrapper(cls):
        # 验证是否为RequestHandler 子类，仅注册其子类
        if not issubclass(cls, RequestHandler):
            raise RuntimeError("Handler注释器只能装饰在RequestHandler子类上")
        # 通过类名查找对应该类下的所有注册方法信息
        res = [item for item in RouterMapping.instance().dynamicMethods
               if item[0] == cls.__name__]
        for item in res:
            # 处理类 RequestHandler 子类 使用时统一继承BaseHandler
            handler = item[1]
            # 全路径 Handler+Mapping 组合
            full_url = route_prefix + url + item[2]
            # 判断是否存在重复注册情况，重复情况直接抛出异常
            if [router for router in RouterMapping.instance() if full_url in router]:
                raise BusinessException(StatusCode.RESOURCE_EXIST(f'路由"{full_url}"'))
            # 存储URL与 RequestHandler 子类对应关系，用于提供给Tornado注册使用
            RouterMapping.instance().append((full_url, cls))
            # 存储URL与处理方法的对应关系，用于调用分发使用
            RouterMapping.instance().handlerMapping.append((full_url, handler))
            if tornado.options.options.rms_register_enable:
                client_name = item[3] if item[3] else tornado.options.options.application_name
                title = item[4] if item[4] else full_url
                en_name = item[5] if item[5] else full_url
                access = item[6] if item[6] else 0
                client_res = get(url=f"{tornado.options.options.rms_register_server}/upms/client/fetchall",
                                 params={"client_name": client_name}).json()
                if not client_res.get("data"):
                    post(url=f"{tornado.options.options.rms_register_server}/upms/client/insert",
                         json={"client_name": client_name})
                    client_res = get(url=f"{tornado.options.options.rms_register_server}/upms/client/fetchall",
                                     params={"client_name": client_name}).json()
                client_id = client_res.get("data")[0].get("id")
                resource_res = get(
                    url=f"{tornado.options.options.rms_register_server}/upms/resource/fetchall",
                    params={"client_name": client_name, "resource_type": 2, "url": full_url}).json()
                if not resource_res.get("data"):
                    res = post(url=f"{tornado.options.options.rms_register_server}/upms/resource/insert",
                               json={"client_id": client_id, "resource_type": 2, "url": full_url, "label": title,
                                     "en_name": en_name, "access": access}).json()
                    if res.get("status") == "00000":
                        print(f"add url={full_url} to rms success")
                    else:
                        print(f"add url={full_url} to rms fail")
        cls.__route_name__ = url
        try:
            parser_swagger(cls, desc)
        except:
            pass

        return cls

    return wrapper


def GetMapping(url: str = "", client_name: str = None, title: str = None, en_name: str = None, access: str = 1,
               interface_desc: str = ""):
    """
    用于类名、处理方法、url 的元祖集合注册处理，暂时GetMapping与PostMapping实现保持一致，预留入口为后期扩展提供支持。
    :param client_name:
    :param access:
    :param en_name:
    :param title:
    :param url:
    :return:
    """

    def wrapper(func):
        # 组合  类名、处理方法、url 的元祖 （url仅代表方法上Mapping装饰器的参数）
        path = url
        if not path:
            path = "/{}".format(func.__name__)
        RouterMapping.instance().dynamicMethods.append(
            (func.__qualname__.replace('.' + func.__name__, ''), func, path, client_name, title, en_name, access))
        func.__route_name__ = path
        func.__http_method__ = "get"
        try:
            parser_swagger(func, (title if title else "") + interface_desc)
        except:
            pass
        return func

    return wrapper


def PostMapping(url: str = "", client_name: str = None, title: str = None, en_name: str = None, access: str = 1,
                interface_desc: str = ""):
    """
    用于类名、处理方法、url 的元祖集合注册处理，暂时GetMapping与PostMapping实现保持一致，预留入口为后期扩展提供支持。
    :param client_name:
    :param access:
    :param en_name:
    :param title:
    :param url:
    :return:
    """

    def wrapper(func):
        # 组合  类名、处理方法、url 的元祖 （url仅代表方法上Mapping装饰器的参数）
        path = url
        if not path:
            path = "/{}".format(func.__name__)
        RouterMapping.instance().dynamicMethods.append(
            (func.__qualname__.replace('.' + func.__name__, ''), func, path, client_name, title, en_name, access))
        func.__route_name__ = path
        func.__http_method__ = "post"
        try:
            parser_swagger(func, (title if title else "") + interface_desc)
        except:
            pass

        return func

    return wrapper

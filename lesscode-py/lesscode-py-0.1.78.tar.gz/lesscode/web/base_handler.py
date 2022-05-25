# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/11/4 4:39 下午
# Copyright (C) 2021 The lesscode Team

import inspect
import json
import time
import types
from datetime import datetime
from decimal import Decimal
from typing import Optional, Awaitable, Any

from bson import ObjectId
from tornado import httputil
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from lesscode.web.status_code import StatusCode
from lesscode.web.business_exception import BusinessException
from lesscode.web.response_result import ResponseResult
from lesscode.web.router_mapping import RouterMapping


class BaseHandler(RequestHandler):
    """
    BaseHandler 类继承自RequestHandler 用于公共基础功能实现，所有均使用此类为基类，只有使用此类的Handler 会被自动加载
    """

    def __init__(self, application: "Application", request: httputil.HTTPServerRequest, **kwargs):
        """
        初始化方法，完成映射装配
        :param application:
        :param request:
        :param kwargs:
        """
        # 如果想要使用自定义响应，设置self.original为True
        self.start_time = int(round(time.time() * 1000))
        self.end_time = int(round(time.time() * 1000))
        self.original = False
        super().__init__(application, request, **kwargs)
        self.command_map = {}
        methods = self.methods()
        for i in range(len(methods)):
            method = getattr(self, methods[i])
            if getattr(method, "__http_method__", None):
                self.command_map[method.__name__] = method

    def methods(self):
        return (list(filter(
            lambda m: not m.startswith("__") and not m.startswith("_") and callable(getattr(self, m)) and
                      type(getattr(self, m, None)) == types.MethodType,
            self.__dir__())))

    async def get(self):
        """
        重写父类get请求处理方法，直接调用post方法统一处理
        :return:
        """
        await self.request_handler()

    async def post(self):
        """
        重写父类post请求方法，使其支持通过URL进行方法调用
        改造Tornado 调用处理方式，不在是一个url对应一个类处理，而是使用同实体处理放到一个类中
        通过不同的url指向不同处理方法
        :return:
        """
        await self.request_handler()

    async def options(self):
        """
        解决跨域验证请求
        HTTP的204(No Content)响应, 就表示执行成功, 但是没有数据
        :return:
        """
        self.set_status(204)
        self.finish()

    async def request_handler(self):
        # 通过url路径获取对应的处理方法
        res = [item for item in RouterMapping.instance().handlerMapping
               if item[0] == self.request.path]
        if res:
            # 元组中索引0 存放url，索引 1 存放处理方法对象，此处获取方法对象
            handler_method = res[0][1]
            # 最终整理后的请求参数集合
            params_list = []
            # 获取当前请求的Content-Type
            content_type = self.request.headers.get('Content-Type')
            # 当前请求参数
            arguments = {}
            query_arguments = self.request.query_arguments
            arguments.update(query_arguments)
            if content_type:
                if "application/json" in content_type:
                    request_body = self.request.body
                    if request_body:
                        body_arguments = json.loads(self.request.body.decode())
                        arguments.update(body_arguments)
                else:
                    body_arguments = self.request.body_arguments
                    arguments.update(body_arguments)
            # 获取处理方法的 参数签名
            signature = inspect.signature(handler_method)
            # parameterName 参数名称, parameter 参数对象
            for parameter_name, parameter in signature.parameters.items():
                # 如果参数是self 做特殊处理，传入本身
                if parameter_name == 'self':
                    params_list.append(self)
                else:
                    # 依据参数名称，获取请求参数值
                    argument_value = arguments.get(parameter_name)
                    # 分以下几种情况，第一种情况 未取得请求参数
                    if argument_value is None:
                        # 查看是否有默认值，如果有直接跳过即可
                        if parameter.default is not inspect.Parameter.empty:
                            params_list.append(parameter.default)
                            continue
                        else:
                            # 如果没有有默认值，要抛出异常 提示"请求缺少必要参数"
                            raise BusinessException(StatusCode.REQUIRED_PARAM_IS_EMPTY(parameter_name))
                    # 获取形参类型
                    parameter_type = parameter.annotation
                    # 形参类型为空，尝试获取形参默认值类型
                    if parameter_type is inspect.Parameter.empty:
                        # if parameter.default is inspect.Parameter.empty:
                        #     parameter_type = type(parameter.default)
                        # else:
                        parameter_type = type(parameter.default)
                    # # 获取实参类型
                    # argument_type = type(argument_value)
                    if isinstance(argument_value, list):  # 如果参数是集合类型要进行遍历并进行转码
                        if self.request.method == "GET":
                            if len(argument_value) == 1:
                                # 仅一个 直接存入
                                params_list.append(parse_val(argument_value[0], parameter_type))
                            else:
                                # 多个要使用集合存入
                                params_list.append([parse_val(v, parameter_type) for v in argument_value])
                        else:
                            params_list.append([parse_val(v, parameter_type) for v in argument_value])
                    else:
                        params_list.append(parse_val(argument_value, parameter_type))

            # 判断是否为异步非阻塞方法，true 则直接调用
            if inspect.iscoroutinefunction(handler_method):
                data = await handler_method(*params_list)
            else:
                # 阻塞方法异步调用
                data = await IOLoop.current().run_in_executor(None, handler_method, *params_list)
            self.end_time = int(round(time.time() * 1000))
            self.set_header("Api-Time", f"{self.end_time - self.start_time}ms")
            if data is not None:
                self.write(json.dumps(ResponseResult(data=data), ensure_ascii=False, cls=JSONEncoder))
        else:
            raise BusinessException(StatusCode.RESOURCE_NOT_FOUND)

    def set_default_headers(self):
        """ 设置header参数
            重写父类方法
        :return:
        """
        origin = self.request.headers.get("Origin")
        if origin:
            self.set_header("Access-Control-Allow-Origin", origin)
        else:
            self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Request-Id", self.request.headers.get("Request-Id", ""))
        self.set_header("Plugin-Running-Time", self.request.headers.get("Plugin-Running-Time", ""))
        self.set_header("Access-Control-Allow-Headers", "x-requested-with,Authorization,Can-read-cache,Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST,GET,PUT,DELETE,OPTIONS")
        self.set_header("Access-Control-Expose-Headers", "Access-Token")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        """
        RequestHandler 类中的抽象方法，此处为空实现，解决所有子类都需要继承ABC的问题
        :param chunk:
        :return:
        """
        pass

    def write_error(self, status_code: int, **kwargs) -> None:
        """ 统一处理异常信息返回
        重写父类错误信息函数，业务逻辑代码中引发的异常 在参数对象中exc_info 获取异常信息对象
        :param status_code:
        :param kwargs:
        :return:
        """
        error = kwargs["exc_info"]
        if isinstance(error[1], BusinessException):
            self.set_status(200)
            self.write(json.dumps(ResponseResult(status_code=error[1].status_code), ensure_ascii=False))
        else:
            # for line in traceback.format_exception(*kwargs["exc_info"]):
            #     self.write(line)
            self.write(json.dumps(ResponseResult(StatusCode.INTERNAL_SERVER_ERROR(error[1])), ensure_ascii=False))
        self.finish()

    def _request_summary(self):
        """ 设置请求日志记录格式
        重写父类方法。
        :return:
        """
        return "%s %s %s %s %s" % (
            self.request.method, self.request.path, self.request.arguments, self.request.remote_ip,
            self.request.headers["User-Agent"])

    def get_current_user(self) -> Any:
        """
        获取当前用户信息
        :return:
        """
        user_json = self.request.headers.get("User")
        if user_json:
            # TODO 未做加密
            user_info = json.loads(user_json)
            if user_info and isinstance(user_info, dict):
                user = User()
                for key in user_info:
                    if key == "roleIds" and user_info[key] and isinstance(user_info[key], str):
                        user_info[key] = json.loads(user_info[key])
                    setattr(user, key, user_info[key])

                return user
        return None

    def add_create_info(self, data):
        user: User = self.get_current_user()
        if user:
            data["create_user_id"] = user.id
            data["create_user_name"] = user.username
        data["create_time"] = datetime.now()

    def add_modify_info(self, data):
        user: User = self.get_current_user()
        if user:
            data["modify_user_id"] = user.id
            data["modify_user_name"] = user.username
        data["modify_time"] = datetime.now()


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, datetime):
            return str(o)
        elif isinstance(o, bytes):
            return str(o, encoding="utf-8")
        elif isinstance(o, set):
            return list(o)
        elif isinstance(o, Decimal):
            return str(o)
        return json.JSONEncoder.default(self, o)


class User:
    """
    用户对象类
    """

    def __init__(self):
        # '账号id',
        self.id = None
        # 用户名
        self.username = None
        # '密码',
        self.password = None
        # '显示名',
        self.display_name = None
        # 手机号,
        self.phone_no = None
        #  邮箱
        self.email = None
        # 组织机构id',
        self.org_id = None
        # '1正常（激活）；2未激活（管理员新增，首次登录需要改密码）； 3锁定（登录错误次数超限，锁定时长可配置）； 4休眠（长期未登录（字段，时长可配置），定时） 5禁用-账号失效；
        self.account_status = None
        # 角色id集合
        self.roleIds = None


# 解析param
def parse_val(val, val_type):
    # inspect.Parameter.empty <class 'NoneType'>
    # isinstance(parameter.annotation, )
    new_val = val
    if isinstance(val, bytes) or isinstance(val, bytearray):
        new_val = val.decode("utf-8")
    if isinstance(val, list):
        val_list = []
        for item in val:
            val_item = parse_val(item, None)
            val_list.append(val_item)
        if val_type == list:
            return val_list
        else:
            new_val = val_list
    if type(new_val) != val_type:
        if val_type == int:
            return int(new_val)
        elif val_type == str and isinstance(new_val, list):
            return new_val[0]
        elif val_type == dict:
            return json.loads(new_val)
        else:
            return new_val
    return new_val

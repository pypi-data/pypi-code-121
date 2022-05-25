#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
"""
@File    :   Event.py
@Time    :   2020/09/29 22:07:04
@Author  :   Tang Jing 
@Version :   1.0.0
@Contact :   yeihizhi@163.com
@License :   (C)Copyright 2020
@Desc    :   None
"""

# here put the import lib
import json
import logging
import functools
from multiprocessing.dummy import Array
import re
from types import FunctionType
from rest_framework.response import Response
from TDhelper.generic.classDocCfg import doc
from TDhelper.generic.dictHelper import createDictbyStr, findInDict
from TDhelper.network.http.REST_HTTP import GET, POST, PUT, DELETE, serializePostData
from TDhelper.generic.requier import R, InstanceCall
from TDhelper.generic.randGetValue import getValue

# code start


class Event:
    """
    if method need listen must have *args,**kwargs params. this params will recv results for this listen func  and results for trigger method .
    1.you can use kwargs['func_results'] get listen method's return.
    2.you can use kwargs['trigger_results'] get trigger method's return.
    """

    def __init__(self, event_uri, platformKey: str, secret=None, httpHeaders={}):
        event_uri = getValue(event_uri)
        self._event_uri = event_uri.rstrip("/") + "/" + "api/"
        self._platformKey = platformKey
        self._httpHeaders = httpHeaders
        self._httpHeaders["api-token"] = secret if secret else ""

    def Register(self, serviceClass=None):
        if not serviceClass:
            serviceClass = type(self)
        for k, v in serviceClass.__dict__.items():
            if isinstance(v, FunctionType):
                if not k.startswith("__"):
                    if not k.startswith("_"):
                        self._handleRegister(v)

    def _handleRegister(self, v):
        # todo register handle
        k = v.__qualname__.replace(".", "_").upper()
        config = v.__doc__
        config = doc(v.__doc__, "event")
        if config:
            config = re.sub(r"[\r|\n]", r"", config, count=0, flags=0).strip()
            try:
                config = json.loads(config, encoding="utf-8")
                try:
                    if config:
                        if "key" in config["handle"]:
                            k = config["handle"]["key"]
                        k = self._platformKey + "." + k
                        post_data = {
                            "name": config["handle"]["name"],
                            "key": k,
                            "plateformKey": self._platformKey,
                            "description": config["handle"]["description"],
                            "params": {},
                            "resultChecked": config["handle"]["resultChecked"],
                        }
                        params_str = {}
                        if "params" not in config["handle"]:
                            parmas_tmp = v.__wrapped__.__code__.co_varnames[
                                0 : v.__wrapped__.__code__.co_argcount
                            ]
                            for var_name in parmas_tmp:
                                if var_name.lower() == "args":
                                    params_str[var_name] = {"type": "<class 'tuple'>"}
                                elif var_name.lower() == "kwargs":
                                    params_str[var_name] = {"type": "<class 'dict'>"}
                                else:
                                    params_str[var_name] = {"type": "<class 'any'>"}
                            for var_name, var_value in v.__wrapped__.__annotations__.items():
                                params_str[var_name]["type"] = str(var_value)
                            if v.__wrapped__.__defaults__:
                                for i in range(len(parmas_tmp), 0, -1):
                                    if (
                                        parmas_tmp[i - 1] == "args"
                                        or parmas_tmp[i - 1] == "kwargs"
                                    ):
                                        continue
                                    offset = i - 2
                                    if offset >= 0:
                                        if offset < len(v.__wrapped__.__defaults__):
                                            params_str[parmas_tmp[i - 1]][
                                                "default"
                                            ] = v.__wrapped__.__defaults__[offset]
                                    else:
                                        break
                            post_data["params"] = params_str
                        else:
                            post_data["params"] = config["handle"]["params"]
                        #post_data = serializePostData(post_data)
                        state, body = POST(
                            self._event_uri + "handle/",
                            post_data=post_data,
                            http_headers=self._httpHeaders,
                            time_out=15,
                        )
                        if state == 200:
                            ret = body
                            if isinstance(body, bytes):
                                ret = json.loads(str(body, encoding="utf-8"))
                            if ret["state"] == 200:
                                logging.info("handle(%s) register SUCCESS" % k)
                                handleId = ret["msg"]["id"]
                                if "trigger" in config:
                                    self._triggerRegister(k, handleId, config["trigger"])
                            else:
                                logging.error(
                                    "register handle %s is error. %s" % (k, ret["msg"])
                                )
                        else:
                            logging.error("access register service failed.%s" % body)
                except Exception as e:
                    logging.error("register handle %s is error, %s" % (k, e))
            except:
                config = None
                logging.error("config is none.")

    def _triggerRegister(self, handle, handleId, config):
        # todo register trigger
        # , name: str, section: str, sync: bool = False, systemEvent: bool = False, handle: int = None
        try:
            for trigger_config in config:
                if "sync" not in trigger_config:
                    trigger_config["sync"] = False
                trigger_config["section"] = trigger_config["section"].upper()
                trigger_config["systemEvent"] = False
                trigger_config["handle"] = handleId
                post_data = serializePostData(trigger_config)
                state, body = POST(
                    self._event_uri + "handle/",
                    post_data=post_data,
                    http_headers=self._httpHeaders,
                    time_out=15,
                )
                if state != 200:
                    logging.error(
                        "%s register trigger %s failed. %s"
                        % (handle, trigger_config["section"], body)
                    )
                else:
                    logging.info(
                        "%s register trigger %s success."
                        % (handle, trigger_config["section"])
                    )
        except Exception as e:
            logging.error("%s register trigger error. %s" % (handle, e))


class Manager:
    def __init__(self, service_uri, platformKey: str, RPCInstance, event_secret=None):
        """
        event manager class.
        - Params:
        -   service_uri:<str>, event service url.
        -   platformKey:<str>, event platform key index.
        -   RPCInstance:<TDhelper.network.http.RPC>, RPC instace. then trigger handle type is rpc must use it.
        """
        self._event_service_uri = getValue(service_uri).rstrip("/") + "/api/"  # 事件服务地址
        self._event_httpHeaders = {}
        self._event_httpHeaders["api-token"] = event_secret if event_secret else ""
        self._event_cache = {}  # 事件缓存
        self._platform = platformKey
        self._getRemoteEventRelation()
        self._RPCInstance = RPCInstance
        self._RPC = {}

    def registerRPC(self, service_name):
        """
        register RPC service into event class.
        """
        self._RPC[service_name] = self._RPCInstance.handle(service_name)

    def _getRemoteEventRelation(self):
        if not self._event_cache:
            # 从服务器组里随机取一个地址.
            m_uri = (
                self._event_service_uri.rstrip("/")
                + "/"
                + "events/?plateform=%s" % self._platform
            )
            try:
                state, body = GET(
                    m_uri, http_headers=self._event_httpHeaders, time_out=15
                )
                if state == 200:
                    ret = json.loads(str(body, encoding="utf-8"))
                    if ret["state"] == 200:
                        self._event_cache = ret["msg"]
                else:
                    logging.error(
                        "access %s error. code(%s), body(%s)" % (m_uri, state, body)
                    )
            except Exception as e:
                logging.error(e)

    def monitor(self, eventKey=None):
        """
        to monitor an method.
        - Returns: <class 'tuple'>, will return the monitored methods handle result and trigger handle results.
        """

        def decorator(func):
            @functools.wraps(func)
            def wapper(*args, **kwargs):
                if eventKey:
                    _handleName = self._platform + "." + eventKey.upper()
                else:
                    _handleName = func.__qualname__.replace(".", "_").upper()
                ret = self.on(_handleName, "BEFORE", *args, **kwargs)
                kwargs["trigger_results"] = []
                kwargs["trigger_results"].append({"BEFORE": ret[1]["results"]})
                if ret[0]:
                    ret = func(*args, **kwargs)
                    # TODO checked results.
                    kwargs["master_func_results"] = ret
                    # to add func results mapping.
                    if _handleName not in self._event_cache:
                        return ret
                    if self._event_cache[_handleName]["resultChecked"]:
                        func_result_checked = self._checked_handle_result(
                            self._event_cache[_handleName]["resultChecked"], ret
                        )
                        if func_result_checked[0]:
                            func_result_checked = self.on(
                                _handleName, "SUCCESS", *args, **kwargs
                            )
                            kwargs["trigger_results"].append(
                                {"SUCCESS": func_result_checked[1]["results"]}
                            )
                            if not func_result_checked[0]:
                                ret = None
                        else:
                            func_result_checked = self.on(
                                _handleName, "FAILED", *args, **kwargs
                            )
                            kwargs["trigger_results"].append(
                                {"FAILED": func_result_checked[1]["results"]}
                            )
                            if not func_result_checked[0]:
                                ret = None
                    func_result_checked = self.on(
                        _handleName, "COMPLETE", *args, **kwargs
                    )
                    kwargs["trigger_results"].append(
                        {"COMPLETE": func_result_checked[1]["results"]}
                    )
                    if not func_result_checked[0]:
                        ret = None
                else:
                    ret = None
                if isinstance(ret, Response):
                    ret.data["trigger_results"] = kwargs["trigger_results"]
                    return ret
                return ret, kwargs["trigger_results"]

            return wapper

        return decorator

    def on(self, handle, event, *args, **kwargs):
        if not handle:
            raise Exception("webEvent.on handle is none.")
        m_event = handle.upper() + "." + event.upper()
        if handle not in self._event_cache:
            return True, {"results": "event trigger method is none."}
        if m_event in self._event_cache[handle]:
            default_state = self._event_cache[handle][m_event]["sync"]
        else:
            default_state = False
        try:
            if handle in self._event_cache:
                if m_event in self._event_cache[handle]:
                    func_results = []
                    for item in self._event_cache[handle][m_event]["trigger_handles"]:
                        callstate, call_result = self._call_router(
                            item, *args, **kwargs
                        )
                        if self._event_cache[handle][m_event]["sync"]:
                            ret = self._checked_handle_result(
                                item["checkedState"], call_result
                            )
                            if not ret[0]:
                                logging.error("%s call error." % item["callHandle"])
                                return False, {"results": call_result}
                        func_results.append(
                            {"trigger": item["callHandle"], "result": call_result}
                        )
                    return True, {"results": func_results}
                else:
                    logging.info("%s not have trigger." % m_event)
                    # this handle not have trigger relation. so return true.
                    return True, {"results": "%s not have trigger." % m_event}
            else:
                logging.error("%s can not found trigger handle." % m_event)
            return default_state, {
                "results": "%s can not found trigger handle." % m_event
            }
        except Exception as e:
            logging.error(e)
            return default_state, {"results": e}

    def _checked_handle_result(self, checkedConfig: dict, result):
        """
        checkedConfig example
        {
            "resultType":json/object/tuple,
            "key":"",
            "operator":"==",
            "value":True
        }
        """
        try:
            operator_dict = {
                "==": "__eq__",
                "<": "__lt__",
                "<=": "__le__",
                ">": "__gt__",
                ">=": "__ge__",
                "!=": "__ne__",
            }
            checkedConfig = json.loads(checkedConfig, encoding="utf-8")
            if "resultType" in checkedConfig:
                resultType = checkedConfig["resultType"].lower()
                if resultType == "json":
                    if isinstance(result, Response):
                        result = result.data
                    else:
                        if isinstance(result, bytes):
                            result = str(result, encoding="utf-8")
                            try:
                                result = json.loads(result, encoding="utf-8")
                            except:
                                result = {}
                    if checkedConfig["key"] not in result:
                        return (False, result)
                    else:
                        ret = InstanceCall(
                            result[checkedConfig["key"]],
                            operator_dict[checkedConfig["operator"]],
                            checkedConfig["value"],
                        )
                        return (ret, result)
                elif resultType == "object":
                    ret = InstanceCall(
                        result,
                        operator_dict[checkedConfig["operator"]],
                        checkedConfig["value"],
                    )
                    return (ret, result)
                elif resultType == "tuple":
                    if checkedConfig["key"] >= len(result):
                        return (False, result)
                    else:
                        ret = InstanceCall(
                            result[checkedConfig["key"]],
                            operator_dict[checkedConfig["operator"]],
                            checkedConfig["value"],
                        )
                        return (ret, result)
                else:
                    return (False, result)
            else:
                return (True, result)  # 当检查参数为空时表示不检查默认执行正常
        except Exception as e:
            logging.error(e)
            return (False, result)

    def _call_router(self, item, *args, **kwargs):
        """
        event trigger router
        """
        m_type = item["handleType"].upper()
        if m_type == "MICROSERVICES":
            return self._api_call(item, *args, **kwargs)
        elif m_type == "LOCATION":
            return self._location_call(item, *args, **kwargs)
        elif m_type == "RPC":
            return self._rpc_call(item, *args, **kwargs)
        else:
            logging.error("%s handle type is error." % item["key"])
            return False, "%s handle type is error." % item["key"]

    def _set_params_mapping(
        self, back_ret: dict, isLocation, key, relation, *args, **kwargs
    ):
        """
        set trigger func params mapping to handle's params.
        """
        if "key" in relation:
            if relation["key"]:
                m_key = relation["key"].split(".")
            else:
                m_key = None
        else:
            m_key = None
        if "sources" in relation:
            sources = relation["sources"]
        else:
            sources = None
        if not m_key:
            if "default" not in relation:
                value = None
            else:
                value = relation["default"]
        else:
            if not sources:
                if len(m_key) == 2:
                    if m_key[0].lower() == "args":
                        if int(m_key[1]) < len(args):
                            value = args[int(m_key[1])]
                        else:
                            if "default" not in relation:
                                value = None
                            else:
                                value = relation["default"]
                    elif m_key[0].lower() == "kwargs":
                        if m_key[1] in kwargs:
                            value = kwargs[m_key[1]]
                        else:
                            if "default" not in relation:
                                value = None
                            else:
                                value = relation["default"]
                    else:
                        if "default" not in relation:
                            value = None
                        else:
                            value = relation["default"]
                else:
                    if "default" not in relation:
                        value = None
                    else:
                        value = relation["default"]
                if isLocation:
                    if m_key:
                        if m_key[0] == "args":
                            back_ret["args"].append(value)
                        elif m_key[0] == "kwargs":
                            back_ret["kwargs"][key] = value
                        else:
                            back_ret["kwargs"][key] = value
                    else:
                        back_ret["kwargs"][key] = value
                else:
                    back_ret[key] = value
            else:
                if "master_func_results" in kwargs:
                    m_func_result = kwargs["master_func_results"]
                    if isinstance(m_func_result, Response):
                        m_func_result = m_func_result.data
                    if isinstance(m_func_result, (tuple, list)):
                        # master func results is Indexes type, mapping process
                        if key == "self":
                            value = m_func_result
                        else:
                            result_key = key.split(".")
                            if len(result_key) == 2:
                                if int(result_key[1]) < len(m_func_result):
                                    value = m_func_result[int(result_key[1])]
                                else:
                                    value = None
                            else:
                                value = None
                    elif isinstance(m_func_result, (dict,)):
                        if key == "self":
                            value = m_func_result
                        else:
                            result_key = key.split(".")
                            if len(result_key) == 2:
                                if result_key[1] in m_func_result:
                                    value = m_func_result[result_key[1]]
                                else:
                                    value = None
                            else:
                                value = None
                    else:
                        # master func results is object
                        if key == "self":
                            value = m_func_result
                        else:
                            result_key = key.split(".")
                            for i in range(1, len(result_key)):
                                m_func_result = getattr(m_func_result, result_key[i])
                            value = m_func_result
                    # mapping params
                    if isLocation:
                        if len(m_key) == 2:
                            if m_key[0].lower() == "args":
                                if int(m_key[1]) < len(back_ret["args"]):
                                    back_ret["args"][int(m_key[1])] = value
                                else:
                                    back_ret["kwargs"][m_key[0]] = value
                            else:
                                back_ret["kwargs"][m_key[0]] = value
                        else:
                            back_ret["kwargs"][m_key[0]] = value
                    else:
                        back_ret[m_key[0]] = value
        return back_ret

    def _generic_params(self, mapping: dict, isLocation=False, *args, **kwargs):
        """
        generic create params.
        - Params:
        -   mapping:<json>, params relation mapping.
        -   isLocation:<bool>, is location call, defalut(false).
        -   *args: <tuple>, original params.
        -   **kwargs: <dict>, original params.
        """
        ret = {}
        if isLocation:
            ret = {"args": [], "kwargs": {}}
        try:
            mapping = json.loads(mapping, encoding="utf-8")
        except Exception as e:
            logging.error(e)
            mapping = {}
        for k, v in mapping.items():
            self._set_params_mapping(ret, isLocation, k, v, *args, **kwargs)
        return ret

    def _location_call(self, item, *args, **kwargs):
        """
        location moudle call
        """
        extendPath = item["extendPath"]
        m_handle = item["callHandle"].split(".")
        m_params = item["params"]
        """
            params mapping example:
            {
                "param1":{
                    "key":"args.0",
                    "default": '',
                },
                "param2":{
                    "key":"kwargs.t",
                    "default":'',
                    "sources": true
                }
            }
        """
        m_checkedState = item["checkedState"]
        m_instance = R(extendPath)
        if m_instance:
            m_instance.Instance(m_handle[0])
            if m_params:
                params_ret = self._generic_params(m_params, True, *args, **kwargs)
                if params_ret:
                    return True, m_instance.Call(
                        m_handle[1], *tuple(params_ret["args"]), **params_ret["kwargs"]
                    )
                else:
                    return False, "%s call params mapping error." % item["callHandle"]
            else:
                return True, m_instance.Call(m_handle[1])
        else:
            return False, "%s call instance is none." % item["callHandle"]

    def _rpc_call(self, item, *args, **kwargs):
        """
        rpc service moudle call
        """
        m_handle = item["callHandle"].split(".") if item["callHandle"] else None
        m_key = item["key"]
        m_params = item["params"]
        if m_handle:
            if len(m_handle) == 2:
                m_service = m_handle[0]
                m_handle = m_handle[1]
                if m_service not in self._RPC:
                    self._RPC[m_service] = self._RPCInstance.handle(m_service)
                if m_service in self._RPC:
                    params_ret = self._generic_params(m_params, False, *args, **kwargs)
                    rpc_result = self._RPC[m_service].call(
                        item["callHandle"], **params_ret
                    )
                    if rpc_result["state"] == 200:
                        return True, rpc_result
                    else:
                        return False, rpc_result
                else:
                    return False, "can not found '%s' service." % m_service
            else:
                return (
                    False,
                    "handle formatter is error. formatter(serviceName.methodName)",
                )
        else:
            return False, "handle is none."

    def _api_call(self, item, *args, **kwargs):
        """
        RestFul api call
        """
        m_key = item["key"]
        m_handle = item["callHandle"]
        m_params = item["params"]
        m_method = item["method"]
        try:
            m_httpHeaders = json.loads(item["httpHeaders"], encoding="utf-8")
        except:
            m_httpHeaders = {}
        m_checkedState = item["checkedState"]
        if m_handle:
            if m_method:
                if m_params:
                    params_ret = self._generic_params(m_params, False, *args, **kwargs)
                    return self._restFul(
                        key=m_key,
                        method=m_method,
                        url=m_handle,
                        headers=m_httpHeaders,
                        post_data=params_ret,
                        time_out=15,
                    )
                else:
                    return self._restFul(
                        key=m_key,
                        method=m_method,
                        url=m_handle,
                        headers=m_httpHeaders,
                        time_out=15,
                    )
            else:
                logging.error("%s http method is none." % m_key)
                return False, "%s http method is none." % m_key
        else:
            logging.error("%s http handle is none." % m_key)
            return False, "%s http handle is none." % m_key

    def _restFul(
        self,
        key: str,
        method: str,
        url: str,
        headers: dict = None,
        post_data: dict = None,
        time_out: int = 5,
    ):
        method = method.upper()
        state = False
        body = None
        try:
            if method == u"GET":
                state, body = GET(
                    uri=url,
                    post_data=post_data,
                    http_headers=headers,
                    time_out=time_out,
                )
            elif method == u"POST":
                state, body = POST(
                    uri=url,
                    post_data=post_data,
                    http_headers=headers,
                    time_out=time_out,
                )
            elif method == u"PUT":
                state, body = PUT(
                    uri=url,
                    post_data=post_data,
                    http_headers=headers,
                    time_out=time_out,
                )
            elif method == u"DELETE":
                state, body = DELETE(
                    uri=url,
                    post_data=post_data,
                    http_headers=headers,
                    time_out=time_out,
                )
            else:
                logging.error("%s http method is error." % key)
                return False, "%s http method is error." % key
            if state == 200:
                return True, body
            else:
                return False, body
        except Exception as e:
            logging.error(e)
            return False, e

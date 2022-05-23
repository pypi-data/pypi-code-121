#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author : SandQuant
# @Email: data@sandquant.com

import configparser
import inspect
import os
import operator
import platform
import urllib.parse

import requests
import pandas as pd

from .error import *


class SandInvestClient:

    _ADDR = "https://api.sandquant.com"
    if platform.system() == 'Windows':
        _DIRNAME = os.getenv("USERPROFILE")
    elif platform.system() == 'Linux':
        _DIRNAME = os.getenv("PATH")
        if _DIRNAME is None:
            _DIRNAME = '/root'
    else:
        _DIRNAME = '/'
    _BASENAME = ".SandInvest"
    _PATH = os.path.join(_DIRNAME, _BASENAME)
    _LoginParams = ["ADDR", "ACCOUNT", "PASSWORD"]

    @classmethod
    def register(cls, account, password):
        _ACCOUNT, _PASSWORD = str(account), str(password)
        _params = dict(zip(cls._LoginParams, [cls._ADDR, _ACCOUNT, _PASSWORD]))
        cfg = configparser.ConfigParser()
        cfg.optionxform = str
        cfg.read_dict(dictionary={cls._BASENAME: _params})
        cfg.write(open(cls._PATH, "w"))
        print("Register Success!")

    @classmethod
    def unregister(cls):
        if os.path.exists(cls._PATH):
            os.remove(cls._PATH)
            print("Unregister Success!")
        else:
            try:
                raise RegisterError
            except RegisterError as err:
                print(err)

    @classmethod
    def auto_login(cls):
        cfg = configparser.ConfigParser()
        cfg.optionxform = str
        if os.path.exists(cls._PATH):
            cfg.read(cls._PATH)
            _params = dict(cfg[cls._BASENAME])
            os.environ.update(_params)
            try:
                cls.validate(_params)
            except Exception as err:
                print(err)
                os.remove(cls._PATH)
                try:
                    raise RegisterWrongError
                except RegisterWrongError as err:
                    print(err)
        else:
            try:
                raise LoginError
            except LoginError as err:
                print(err)
            # print("Missing Login Information")

    @classmethod
    def login(cls, account, password):
        _ACCOUNT, _PASSWORD = str(account), str(password)
        _params = dict(zip(cls._LoginParams, [cls._ADDR, _ACCOUNT, _PASSWORD]))
        os.environ.update(_params)
        cls.validate(_params)

    @classmethod
    def settings(cls):
        return {'account': os.getenv('ACCOUNT'), 'password': os.getenv('PASSWORD')}

    @classmethod
    def validate(cls, params):
        """Validate Login Params 验证登录参数"""
        params = {(_.lower(), __) for _, __ in params.items()}
        endpoint = urllib.parse.urljoin(os.getenv("ADDR"), inspect.getframeinfo(inspect.currentframe()).function)
        response = requests.get(endpoint, params=params)
        result = cls.parse_response(response)
        print(result)

    @classmethod
    def parse_response(cls, result: requests.Response):
        if result.status_code == 200:
            _result = result.json()
            result_type = _result.get('type')
            result_data = _result.get('data')
            if _istype(result_type, pd.DataFrame):
                return pd.DataFrame(result_data)
            if _istype(result_type, str):
                return result_data
            if _istype(result_type, list):
                return result_data
            if _istype(result_type, dict):
                return result_data

        elif result.status_code == 403:
            _error = result.json()['detail'][0]
            _error_msg = _error['msg']
            raise ValueError(_error_msg)

        elif result.status_code == 404:
            _error = result.json()['detail'][0]
            _error_loc = _error['loc'][1]
            _error_msg = _error['msg']
            raise AttributeError(f"{_error_loc} 参数错误，{_error_msg}")

        else:
            raise ClientError

    @classmethod
    def _headers(cls):
        """获取请求头"""
        return dict(zip(cls._LoginParams, operator.itemgetter(*cls._LoginParams)(os.environ)))

    def __init__(self):
        ...

    def __call__(self, func, **_params):
        _headers = self._headers()
        endpoint = urllib.parse.urljoin(os.getenv("ADDR"), func)
        response = requests.get(endpoint, params=_params, headers=_headers)
        result = self.parse_response(response)
        return result

    def __getattr__(self, func, **_params):
        return lambda **_params: self(func, **_params)


def _istype(_type, __type):
    """判断返回的数据类型"""
    return isinstance(eval(_type), __type)

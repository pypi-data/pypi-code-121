# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from functools import partial
import requests

from rainiee_data.base import upass


class DataApi:
    def __init__(self, token=None, timeout=6000):
        """
        Parameters
        ----------
        token: str
            API接口TOKEN，用于用户认证
        """
        self.__timeout = timeout
        self.__http_url = upass.get_host() + '/api/v1.0/{}'
        self.__token = token

    def query(self, api_name, method_type, req_param):
        headers = {
            'Authorization': 'JWT ' + self.__token,
            'Connection': 'close'
        }
        if method_type == 'POST':
            res = requests.post(self.__http_url.format(api_name), data=req_param, timeout=self.__timeout,
                                headers=headers)
        else:
            res = requests.get(self.__http_url.format(api_name), params=req_param, timeout=self.__timeout,
                               headers=headers)
        return json.loads(res.text)

    def __getattr__(self, name):
        return partial(self.query, api_name=name)

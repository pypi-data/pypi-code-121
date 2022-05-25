#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/3/2 15:22
# @Author  : Adyan
# @File    : function.py


import json
import re
import time
from datetime import datetime
from typing import Union

import pytz

cntz = pytz.timezone("Asia/Shanghai")
remap = {
    ord('\t'): '', ord('\f'): '',
    ord('\r'): '', ord('\n'): '',
}


class Fun:

    @classmethod
    def merge_dic(
            cls,
            dic: dict,
            lst: list
    ):
        """
        合并多个dict
        :param dic: dict - 主dict
        :param lst: list - 多个字典列表方式传入
        :return:
        """
        for d in lst:
            for k, v in d.items():
                if v:
                    dic[k] = v
        return dic

    @classmethod
    def del_html(cls, html: str):
        for i in re.findall(r"<(.*?)>", html):
            html = html.replace(f'<{i}>', '')
        return html.translate({**remap, ord(' '): ''})

    @classmethod
    def re_dict(
            cls,
            re_pattern: dict and list,
            string_,
    ) -> dict:
        if isinstance(re_pattern, dict):
            fun = lambda x, y: y if ' ' in x else y.replace(' ', '')
            return {
                key: cls.compute_res(
                    re_pattern=re.compile(scale),
                    string_=fun(scale, string_.translate(remap))
                )
                for key, scale in re_pattern.items()
            }
        if isinstance(re_pattern, list):
            dic = {}
            for index in range(len(re_pattern)):
                string = string_
                if isinstance(string_, list):
                    string = string_[index]
                if isinstance(string, int):
                    string = string_[string]
                dict2 = cls.re_dict(re_pattern[index], string)
                for k, v in dict2.items():
                    if k in dic.keys():
                        values = dic.get(k)
                        if values and v:
                            dict2[k] = [values, v]
                        if values and v is None:
                            dict2[k] = values
                dic = {**dic, **dict2}
            return dic

    @classmethod
    def compute_res(
            cls,
            re_pattern: re.Pattern,
            string_=None
    ):
        data = re_pattern.findall(string_)
        if data:
            try:
                return json.loads(data[0])
            except:
                return data[0]
        else:
            return None

    @classmethod
    def find(
            cls, target: str,
            dictData: dict,
    ):
        queue = [dictData]
        result = []
        while len(queue) > 0:
            data = queue.pop()
            for key, value in data.items():
                if key == target:
                    result.append(value)
                elif isinstance(value, dict):
                    queue.append(value)
        if result:
            return result[0]

    @classmethod
    def finds(
            cls, target: str,
            dictData: dict,
    ) -> list:
        queue = [dictData]
        result = []
        while len(queue) > 0:
            data = queue.pop()
            if isinstance(data, str):
                continue
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == target:
                        if value not in result:
                            result.insert(0, value)
                    queue.append(value)
            if isinstance(data, list):
                for dic in data:
                    queue.append(dic)
        if result:
            return result

    @classmethod
    def timeconvert(
            cls, times, timestamp=None,
            int_time=None

    ) -> Union[int, str]:
        remap = {
            ord('年'): '-', ord('月'): '-',
            ord('日'): ' ',
            ord('/'): '-',
            ord('.'): '-',
        }
        if isinstance(times, str):
            times = times.translate(remap)
        if int_time:
            return int(time.mktime(time.strptime(times, int_time)))
        if isinstance(times, str):
            times = int(time.mktime(time.strptime(times, "%Y-%m-%d %H:%M:%S")))
        if timestamp:
            times = times + timestamp
        return str(datetime.fromtimestamp(times, tz=cntz))

    @classmethod
    def is_None(
            cls, dic: dict,
    ) -> dict:
        """
        :param dic: dict
        :return: 返回字典中值是None的键值对
        """
        return {
            k: v
            for k, v in dic.items()
            if not v
        }

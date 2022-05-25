#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/26 11:50
# @Author  : Adyan
# @File    : proxy.py


import json
import logging
import random
import re
import time
from datetime import datetime

import requests

cache = {}
limit_times = [100]


def stat_called_time(func):
    def _called_time(*args, **kwargs):
        key = func.__name__
        if key in cache.keys():
            cache[key][0] += 1
        else:
            call_times = 1
            cache[key] = [call_times, time.time()]
        if cache[key][0] <= limit_times[0]:
            res = func(*args, **kwargs)
            cache[key][1] = time.time()
            return res
        else:
            print('请求次数限制')
            return None

    return _called_time


class ProxyMeta(type):
    def __new__(mcs, name, bases, attrs):
        attrs['__Crawl_Func__'] = []
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__Crawl_Func__'].append(k)

        return type.__new__(mcs, name, bases, attrs)


class GetProxy(metaclass=ProxyMeta):
    """
    :sample code:
        GetProxy(spider.proxy).get_proxies()
    """

    def __init__(self, proxy: dict):
        self.url = proxy.get('url')
        self.name = proxy.get('name')
        self.add_whitelist = proxy.get('add_whitelist')
        self.del_whitelist = proxy.get('del_whitelist')

    def get_proxies(self):
        """
        通过方法名调用方法，获取代理
        :param callfunc:
        :return:
        """
        proxies = []
        res = eval(f'self.{self.name}()')
        try:
            if isinstance(res, dict):
                return res
            for proxy in res:
                proxies.append(proxy)
        except Exception as e:
            print(f"{self.name}:{e}{res}")
        if proxies:
            return proxies

    @stat_called_time
    def jingling_ip(self):
        ip_list = []
        res = json.loads(requests.get(self.url).text)
        if not res.get("data"):
            msg = res.get('msg')
            if "限制" in msg:
                time.sleep(random.randint(1, 3))
            if '登' in msg:
                limit_times[0] += 1
                _ip = re.findall('(.*?)登', res.get("msg"))
                requests.get(self.add_whitelist % _ip[0], timeout=10)
            res = json.loads(requests.get(self.url).text)

        logging.info(f"{str(datetime.now())[:-7]}-{res}")
        print(f"{str(datetime.now())[:-7]}-{res}")

        if res.get("data"):
            for item in res.get("data"):
                ip_list.append("https://" + item['IP'])

        if ip_list:
            return ip_list
        else:
            return res

    @stat_called_time
    def taiyang_ip(self):
        ip_list = []
        res = json.loads(requests.get(self.url).text)
        if not res.get("data"):
            msg = res.get("msg")
            if '请2秒后再试' in msg:
                time.sleep(random.randint(2, 4))
                limit_times[0] += 1
            if '请将' in msg:
                _ip = msg.split("设")[0][2:]
                print(requests.get(self.add_whitelist % _ip).text)
            if '当前IP' in msg:
                _ip = msg.split("：")[1]
                print(requests.get(self.add_whitelist % _ip).text)
            res = json.loads(requests.get(self.url).text)

        logging.info(f"{str(datetime.now())[:-7]}-{res}")
        print(f"{str(datetime.now())[:-7]}-{res}")

        if res.get("data"):
            for item in res.get("data"):
                ip_list.append(f"https://{item['ip']}:{item['port']}")

        if ip_list:
            return ip_list
        else:
            return res

    @stat_called_time
    def zhima_ip(self):
        pass

    @stat_called_time
    def kuaidaili_ip(self):
        ip_list = []
        res = json.loads(requests.get(self.url).text)
        limit_times[0] += 1
        print(res)
        for item in res.get("data").get("proxy_list"):
            ip_list.append(f"https://{item}")
        if ip_list:
            return ip_list
        else:
            return res

    @stat_called_time
    def source_proxy(self):
        res = json.loads(requests.get(self.url).text)
        if not res.get("data"):
            msg = res.get("msg")
            if '请2秒后再试' in msg:
                limit_times[0] += 1
                time.sleep(random.randint(2, 4))
            res = json.loads(requests.get(self.url).text)

        logging.info(f"{str(datetime.now())[:-7]}-{res}")
        print(f"{str(datetime.now())[:-7]}-{res}")

        if res.get("data"):
            return res.get("data")
        else:
            return res

# if __name__ == '__main__':
#     print(ProxyGetter(
#         'https://tps.kdlapi.com/api/gettps/?orderid=903884027633888&num=1&pt=1&format=json&sep=1',
#         'kuaidaili_ip',
#         add_whitelist='https://dev.kdlapi.com/api/setipwhitelist?orderid=903884027633888&iplist=%s&signature=thl1n7lqhisfikvznxwl631bds413640',
#         # del_whitelist=proxy.get('del_whitelist')
#     ).get_proxies())

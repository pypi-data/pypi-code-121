# -*- coding: utf-8 -*-
# @Created : DOLW 
# @Time    : 2022/5/22 14:02
# @Project : feapder_utils
# @FileName: proxy_pool.py
# @Software: PyCharm
# Copyright (c) 2022 DOLW. All rights reserved.


# -*- coding: utf-8 -*-


import random

import feapder.utils.tools as tools
from feapder import setting
from feapder.db.redisdb import RedisDB

from feapder.utils.log import log
from feapder.utils.redis_lock import RedisLock

import json

import requests
import time
from urllib import parse
from feapder_utils.proxyPool.base_pool import ProxyPoolInterface, check_proxy


class ProxyItem(object):
    """单个代理对象"""

    # 代理标记
    proxy_tag_list = (-1, 0, 1)

    def __init__(
            self,
            proxies=None,
            **kwargs
    ):
        """
        :param proxies:
        """
        self.args_list = ['proxies', 'proxy_id', 'proxy_ip_port']
        # {"http": ..., "https": ...}
        self.proxies = proxies
        self.proxy_args = self.parse_proxies(self.proxies)
        self.proxy_ip = self.proxy_args["ip"]
        self.proxy_port = self.proxy_args["port"]
        self.proxy_ip_port = "{}:{}".format(self.proxy_ip, self.proxy_port)
        if self.proxy_args["user"]:
            self.proxy_id = "{user}:{password}@{ip}:{port}".format(**self.proxy_args)
        else:
            self.proxy_id = self.proxy_ip_port

        # 日志处理器
        self.logger = log

    def __str__(self):
        return f"<{self.__class__.__name__}>: " + json.dumps(
            self.to_dict(), indent=4, ensure_ascii=False
        )

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        data = {}
        for key, value in self.__dict__.items():
            if value is not None and key in self.args_list:
                data[key] = value
        return data

    def from_dict(cls, data):
        return cls.__init__(**data)

    def get_proxies(self):
        self.use_num += 1
        return self.proxies

    def is_valid(self, force=0, type=0):
        """
        检测代理是否有效
            1 有效
            2 延时使用
            0 无效 直接在代理池删除
        :param force:
        :param type:
        :return:
        """
        if self.use_num > self.max_proxy_use_num > 0:
            self.logger.debug("代理达到最大使用次数: {} {}".format(self.use_num, self.proxies))
            return 0
        if self.flag == -1:
            self.logger.debug("代理被标记 -1 丢弃 %s" % self.proxies)
            return 0
        if self.delay > 0 and self.flag == 1:
            if time.time() - self.flag_ts < self.delay:
                self.logger.debug("代理被标记 1 延迟 %s" % self.proxies)
                return 2
            else:
                self.flag = 0
                self.logger.debug("延迟代理释放: {}".format(self.proxies))
        if self.use_interval:
            if time.time() - self.use_ts < self.use_interval:
                return 2
        if not force:
            if time.time() - self.update_ts < self.check_interval:
                return 1
        if self.valid_timeout > 0:
            ok = check_proxy(
                proxies=self.proxies,
                type=type,
                timeout=self.valid_timeout,
                logger=self.logger,
            )
        else:
            ok = 1
        self.update_ts = time.time()
        return ok

    @classmethod
    def parse_proxies(self, proxies):
        """
        分解代理组成部分
        :param proxies:
        :return:
        """
        if not proxies:
            return {}
        if isinstance(proxies, (str, bytes)):
            proxies = json.loads(proxies)
        protocol = list(proxies.keys())
        if not protocol:
            return {}
        _url = proxies.get(protocol[0])
        if not _url.startswith("http"):
            _url = "http://" + _url
        _url_parse = parse.urlparse(_url)
        netloc = _url_parse.netloc
        if "@" in netloc:
            netloc_auth, netloc_host = netloc.split("@")
        else:
            netloc_auth, netloc_host = "", netloc
        ip, *port = netloc_host.split(":")
        port = port[0] if port else "80"
        user, *password = netloc_auth.split(":")
        password = password[0] if password else ""
        return {
            "protocol": protocol,
            "ip": ip,
            "port": port,
            "user": user,
            "password": password,
            "ip_port": "{}:{}".format(ip, port),
        }


class ProxyPool(ProxyPoolInterface):
    """
    访客用户池 不需要登陆
    """

    def __init__(
            self,
            redis_key,
            page_url=None,
            min_proxys=1,
            keep_alive=False,
            **kwargs
    ):
        """
        @param redis_key: proxy存放在redis中的key前缀
        @param page_url: 生产proxy的url
        @param min_proxys: 最小proxy数
        @param keep_alive: 是否保持常驻，以便proxy不足时立即补充
        """

        self._redisdb = RedisDB()

        self._tab_proxy_pool = "{redis_key}:h_{proxy_type}_pool".format(
            redis_key=redis_key, proxy_type="proxy"
        )
        self._page_url = page_url if page_url is not None else setting.PROXY_EXTRACT_API
        self._min_proxys = min_proxys
        self._keep_alive = keep_alive

        self._proxy_id = []
        # 计数 获取代理重试3次仍然失败 次数
        self.no_valid_proxy_times = 0
        self.check_valid = kwargs.get("check_valid", False)

    def _load_proxy_id(self):
        self._proxy_id = self._redisdb.hkeys(self._tab_proxy_pool)
        if self._proxy_id:
            random.shuffle(self._proxy_id)

    def _get_proxy_id(self):
        if not self._proxy_id:
            self._load_proxy_id()

        if self._proxy_id:
            return self._proxy_id.pop()

    def get_proxy_from_http(self):
        """
        可以重写
        """
        proxies_list = []
        response = requests.get(self._page_url, timeout=20)
        for line in response.text.split('\n'):
            line = line.strip()
            if not line:
                continue
            # 解析
            auth = ""
            if "@" in line:
                auth, line = line.split("@")
            #
            items = line.split(":")
            if len(items) < 2:
                continue

            ip, port, *protocol = items
            if not all([port, ip]):
                continue
            if auth:
                ip = "{}@{}".format(auth, ip)
            if not protocol:
                proxies = {
                    "https": "https://%s:%s" % (ip, port),
                    "http": "http://%s:%s" % (ip, port),
                }
            else:
                proxies = {protocol[0]: "%s://%s:%s" % (protocol[0], ip, port)}
            proxies_list.append(proxies)
        return proxies_list

    def add_proxy(self, proxy):
        log.debug("add {}".format(proxy))
        self._redisdb.hset(self._tab_proxy_pool, proxy.proxy_id, proxy.to_dict())

    def put_proxy_item(self, proxy_id):
        """
        添加 ProxyItem 到代理池
        :param proxy_item:
        :return:
        """
        return self._proxy_id.insert(0, proxy_id)

    def del_proxy(self, proxy_id: str):
        self._redisdb.hdel(self._tab_proxy_pool, proxy_id)
        self._load_proxy_id()

    def get_proxy(self, retry: int = 0, block=True):
        """
        Args:
            block: 无用户时是否等待

        Returns:

        """
        retry += 1
        if retry > 3:
            self.no_valid_proxy_times += 1
            return None
        if self.no_valid_proxy_times >= 5:
            # 解决bug: 当爬虫仅剩一个任务时 由于只有一个线程检测代理 而不可用代理又刚好很多（时间越长越多） 可能出现一直获取不到代理的情况
            # 导致爬虫烂尾
            try:
                self.reset_proxy_pool()
            except Exception as e:
                log.exception(e)
        try:
            proxy_id = self._get_proxy_id()
            if proxy_id:
                proxy_str = self._redisdb.hget(self._tab_proxy_pool, proxy_id)
                # 如果没取到proxy，可能是其他爬虫将此用户删除了，需要重刷新本地缓存的代理id
                if not proxy_str:
                    self._load_proxy_id()
                    return self.get_proxy(retry, block)
                proxy_item = ProxyItem(**eval(proxy_str))
                if proxy_item:
                    # 不检测
                    if not self.check_valid:
                        # 塞回去
                        self.put_proxy_item(proxy_item.proxy_id)
                        return proxy_item
                    else:
                        is_valid = proxy_item.is_valid()
                        if is_valid:
                            # 塞回去
                            self.put_proxy_item(proxy_item.proxy_id)
                            if is_valid == 1:
                                return proxy_item
                        else:
                            raise Exception(f'代理已经失效：{proxy_item.proxy_id}')
                    # 处理失效代理
            if not proxy_id and block:
                self._keep_alive = False
                with RedisLock(
                        key=self._tab_proxy_pool, lock_timeout=3600, wait_timeout=10
                ) as _lock:
                    if _lock.locked:
                        self.run()
                return self.get_proxy(retry, block)
        except Exception as e:
            log.exception(e)
            tools.delay_time(1)

        return self.get_proxy(retry, block)

    get = get_proxy

    def reset_proxy_pool(self, force: bool = False):
        """
        重置代理池
        :param force: 是否强制重置代理池
        :return:
        """
        log.warning('reset_proxy_pool')
        with RedisLock(
                key=self._tab_proxy_pool, lock_timeout=3600, wait_timeout=10
        ) as _lock:
            if _lock.locked and self.no_valid_proxy_times >= 5:
                self.no_valid_proxy_times = 0
                for item in self._proxy_id:
                    self.del_proxy(item)
                self._proxy_id.clear()
                self.run()

    def run(self):

        while True:
            try:
                now_user_count = self._redisdb.hget_count(self._tab_proxy_pool)
                need_user_count = self._min_proxys - now_user_count

                if need_user_count > 0:
                    log.debug(
                        "当前在线proxy数为 {} 小于 {}, 生产proxy".format(
                            now_user_count, self._min_proxys
                        )
                    )
                    try:
                        users = self.get_proxy_from_http()
                        log.debug(f"get_proxy_from_http 获得代理数：{len(users)}")
                        for item in users:
                            self.add_proxy(ProxyItem(item))
                    except Exception as e:
                        log.exception(e)
                else:
                    log.debug("当前proxy数为 {} 大于 {} 暂不生产".format(now_user_count, self._min_proxys))

                    if self._keep_alive:
                        tools.delay_time(10)
                    else:
                        break

            except Exception as e:
                log.exception(e)
                tools.delay_time(1)


if __name__ == '__main__':
    item = ProxyItem({"http": 'http://127.0.0.1:5515', "https": 'https://127.0.0.1:5515'})
    print(item.to_dict())
    print(item.proxy_id)

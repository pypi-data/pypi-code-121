# -*- coding: utf-8 -*-
# @Created : DOLW 
# @Time    : 2022/5/23 8:53
# @Project : feapder_utils
# @FileName: base_pool.py
# @Software: PyCharm
# Copyright (c) 2022 DOLW. All rights reserved.

import socket
import abc
from feapder.utils.log import log
import requests


class ProxyPoolInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_proxy_from_http(self, *args, **kwargs):
        """
        由hhttp获取代理
        Args:
            *args:
            **kwargs:

        Returns:

        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_proxy(self, *args, **kwargs):
        """
        添加代理
        Args:
            *args:
            **kwargs:

        Returns:

        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, block=True):
        """
        获取代理
        Args:
            block: 无用户时是否等待

        Returns:

        """
        raise NotImplementedError

    @abc.abstractmethod
    def del_proxy(self, *args, **kwargs):
        """
        删除代理
        Args:
            *args:
            **kwargs:

        Returns:

        """
        raise NotImplementedError

    @abc.abstractmethod
    def run(self):
        """
        维护一定数量的代理
        Returns:

        """
        raise NotImplementedError


def check_proxy(
        ip="",
        port="",
        proxies=None,
        type=0,
        timeout=5,
        logger=None,
        show_error_log=True,
):
    """
    代理有效性检查
    :param ip:
    :param port:
    :param type: 0:socket  1:requests
    :param timeout:
    :param logger:
    :return:
    """
    if not logger:
        logger = log
    ok = 0
    if type == 0 and ip and port:
        # socket检测成功 不代表代理一定可用 Connection closed by foreign host. 这种情况就不行
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk:
            sk.settimeout(timeout)
            try:
                # 必须检测 否则代理永远不刷新
                sk.connect((ip, int(port)))
                ok = 1
            except Exception as e:
                if show_error_log:
                    logger.debug("check proxy failed: {} {}:{}".format(e, ip, port))
            sk.close()
    else:
        if not proxies:
            proxies = {
                "http": "http://{}:{}".format(ip, port),
                "https": "https://{}:{}".format(ip, port),
            }
        try:
            r = requests.get(
                "http://www.baidu.com", proxies=proxies, timeout=timeout, stream=True
            )
            ok = 1
            r.close()
        except Exception as e:
            if show_error_log:
                logger.debug(
                    "check proxy failed: {} {}:{} {}".format(e, ip, port, proxies)
                )
    return ok

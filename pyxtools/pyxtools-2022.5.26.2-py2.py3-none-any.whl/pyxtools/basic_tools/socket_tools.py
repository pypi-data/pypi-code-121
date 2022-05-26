# -*- coding:utf-8 -*-
from __future__ import absolute_import

import logging
import socket

import requests

from .async_http_tool import async_request_get


def port_is_used(addr: str, port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((addr, int(port)))
            return True
    except Exception as e:
        logging.error(e)

    return False


def proxy_is_valid(proxy_url, url_tuple=None, timeout=10, async_mode=False):
    """

    :type async_mode: bool
    :param proxy_url: str, like "socks5://127.0.0.1:1080"
    :rtype: bool
    :type timeout: int
    :type url_tuple: None|tuple
    """
    if url_tuple is None:
        url_tuple = (
            "https://www.baidu.com/robots.txt",
            "https://www.qq.com/robots.txt",
            "http://www.hao123.com/robots.txt"
        )

    if len(url_tuple) == 1:
        async_mode = False

    if async_mode is False:
        # blocking mode
        proxies = {'http': proxy_url, 'https': proxy_url}

        def is_work(_url):
            try:
                response = requests.get(_url, proxies=proxies, timeout=timeout)
                return len(response.content) > 0
            except Exception as e:
                logging.error("Failed to connect to {}: {}".format(_url, e))
                return False

        result_list = [is_work(url) for url in url_tuple]

    else:
        # async_mode mode
        def response_func(content):
            return len(content) > 0

        raw_list = async_request_get(
            list(url_tuple), time_out=timeout, proxy=proxy_url, sema_count=5, response_callback=response_func
        )
        result_list = []
        for result in raw_list:
            if isinstance(result, bool):
                result_list.append(result)
            else:
                result_list.append(False)

    return result_list.count(True) >= len(result_list) / 2.0


def get_random_unopen_port(local_addr: str) -> int:
    """

    :param local_addr: ip to bind, 127.0.0.1
    :return: unopen port
    """
    with socket.socket() as sock:
        sock.bind((local_addr, 0))
        ip, port = sock.getsockname()
        return port

# -*- coding:utf-8 -*-
from __future__ import absolute_import

import logging
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


def simple_request_get(url):
    return requests.get(
        url,
        headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko)' +
                          ' Chrome/22.0.1216.0 Safari/537.2'
        },
        timeout=15).content


def proxy_request_get(url, proxy_addr, proxy_port):
    socks_url = "socks5://{}:{}".format(proxy_addr, proxy_port)
    proxies = {'http': socks_url, 'https': socks_url}
    return requests.get(
        url,
        headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko)' +
                          ' Chrome/22.0.1216.0 Safari/537.2'
        },
        proxies=proxies,
        timeout=15).content


def request_get_by_web_api(url, ):
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        "DNT": "1",
    }

    def get_response_from_codebeautify(_url):
        """
        https://codebeautify.org/source-code-viewer
        :param _url:
        :return:
        """
        headers = dict(default_headers)
        headers.update({
            "Accept": "text/plain, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://codebeautify.org",
            "Referer": "https://codebeautify.org/source-code-viewer",
        })
        return requests.post(
            "https://codebeautify.com/URLService",
            data={"path": _url},
            headers=headers,
            timeout=15).content

    return get_response_from_codebeautify(url)


def strong_request_get(url, proxy_addr="127.0.0.1", proxy_port=1080):
    try:
        return simple_request_get(url)
    except Exception as e:
        logger.error(e)
    try:
        return proxy_request_get(url, proxy_addr, proxy_port)
    except Exception as e:
        logger.error(e)
        return request_get_by_web_api(url)


def get_domain(url):
    """

    :rtype: str
    :type url: str
    """
    parsed_uri = urlparse(url)
    return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)


__all__ = ("strong_request_get", "simple_request_get", "proxy_request_get", "get_domain", "request_get_by_web_api")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/26 13:54
# @Author  : Adyan
# @File    : middleware.py


import logging
import random
import time

from requests import sessions
from scrapy import signals
from scrapy.core.downloader.handlers.http11 import TunnelError, TimeoutError
from scrapy.http import TextResponse
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.error import ConnectionRefusedError
from w3lib.http import basic_auth_header

from Utils.crawler.proxy import GetProxy


class Proxy(object):

    def __init__(self, settings, spider):
        self.settings = settings
        self.ip_list = []
        try:
            self.proxy = spider.proxy
            if self.proxy.get("name"):
                self.proxies = GetProxy(self.proxy)
        except:
            self.proxy = {}

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings, crawler.spider)

    def process_response(self, request, response, spider):
        if request.meta.get("isProxy"):
            start_time = request.meta.get('_start_time', time.time())
            logging.info(
                f'【代理{request.meta["proxy"][8:]}消耗时间{time.time() - start_time}】{request.url}'
            )
            del request.meta["proxy"]
        return response

    def process_request(self, request, spider):
        if self.proxy.get("name") and request.meta.get("isProxy"):
            request.meta.update({'_start_time': time.time()})
            if isinstance(self.ip_list, list):
                if len(self.ip_list) < 5:
                    while True:
                        proxies = self.proxies.get_proxies()
                        if proxies:
                            break
                    self.ip_list = proxies

                request.meta['download_timeout'] = 5
                ip_raw = random.choice(self.ip_list)
                self.ip_list.remove(ip_raw)
                request.meta["proxy"] = ip_raw
            else:
                logging.info('代理列表为空')

        if self.proxy.get("username") and request.meta.get("isProxy"):
            request.meta['proxy'] = f"http://{self.proxy.get('proxies')}"
            request.headers['Proxy-Authorization'] = basic_auth_header(
                self.proxy.get("username"),
                self.proxy.get("password")
            )

    def process_exception(self, request, exception, spider):
        if isinstance(exception, (TunnelError, TimeoutError, ConnectionRefusedError)):
            return request


class RequestsDownloader(object):

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    @defer.inlineCallbacks
    def process_request(self, request, spider):
        kwargs = request.meta.get("params")
        if kwargs:
            container = []
            out = defer.Deferred()
            reactor.callInThread(self._get_res, request, container, out, kwargs)
            yield out
            if len(container) > 0:
                defer.returnValue(container[0])

    def _get_res(self, request, container, out, kwargs):
        try:
            url = request.url
            method = kwargs.pop('method')
            r = sessions.Session().request(method=method, url=url, **kwargs)
            r.encoding = request.encoding
            text = r.content
            encoding = None
            response = TextResponse(url=r.url, encoding=encoding, body=text, request=request)
            container.append(response)
            reactor.callFromThread(out.callback, response)
        except Exception as e:
            err = str(type(e)) + ' ' + str(e)
            reactor.callFromThread(out.errback, ValueError(err))

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

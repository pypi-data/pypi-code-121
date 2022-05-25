#!/usr/bin/env python
# coding=utf-8

"""
Version: 0.1
Autor: zmf96
Email: zmf96@qq.com
Date: 2022-02-24 15:51:03
LastEditors: zmf96
LastEditTime: 2022-03-30 19:44:31
FilePath: /hotfinger/__init__.py
Description: 
"""

from cp_common.base import Plugin
from cp_common.utils import get_host_port_from_url

from .hotfinger import init, worker

__version__ = "0.1.3"

__all__ = ["PluginClass"]


class PluginClass(Plugin):
    usage = [
        {
            "name": "url_list",
            "type": "List[str]",
            "usage": 'Url列表，eg: ["http://baidu.com","http://bing.com"]',
        }
    ]
    plugin_name = "hotfinger"
    author = "example"
    version = __version__

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self):
        self.logger.info(self.kwargs)
        init()
        url_list = self.kwargs.get("url_list")
        for url in url_list:
            finger = worker(url)
            print(finger.fingers)
            host, port = get_host_port_from_url(url)
            hostinfo = host + ":" + port
            self.results.append(
                {
                    "port_info": {
                        "hostinfo": hostinfo,
                        "host": host,
                        "port": port,
                        "products": finger.fingers,
                    }
                }
            )

    @staticmethod
    def vaildator_args(kwargs):
        if "url_list" in kwargs and isinstance(kwargs["url_list"], list):
            return True
        return False

# -*- coding: utf8 -*-
import sys


class UtilUrl(object):
    """
    url处理工具类
    """

    @staticmethod
    def get_url(from_url, cur_url):
        """
        拼接完整的url
        Args:
            from_url:源url
            cur_url:要处理的url，可能是完整的url，也可能是以/、?等开始的不完整的url
        """
        if cur_url.startswith('http'):
            return cur_url
        elif cur_url.startswith('/'):
            index = from_url.find('/', 8)
            return from_url[0:index] + cur_url
        elif cur_url.startswith('?'):
            index = from_url.find('?')
            return from_url[0:index] + cur_url
        else:
            index = from_url.rfind('/')
            return from_url[0:index + 1] + cur_url
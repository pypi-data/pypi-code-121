# -*- coding: utf-8 -*-
"""
 @Time: 2019/6/10 13:21
"""
import time
import os
import sys
import traceback
import hashlib
import urllib
import pymysql
import json
import time
import base64
from pymysql.converters import escape_string

from datetime import datetime

import re
import urllib3
urllib3.disable_warnings()
import requests
requests.packages.urllib3.disable_warnings()

def util_md5(s):
    m = hashlib.md5()
    m.update(s.encode(encoding='gbk'))
    return m.hexdigest()


class HtmlLocalDownloader(object):
    """
    html下载器
    """

    def __init__(self, set_mode='db', get_mode='db', store_type=5):  # 兼容 保留
        self.user_id = 0
        self.REQUEST_TIMEOUT = 20

    def downloader_set_param(self, request, store_type=5):
        url_type = None
        new_urls = list()
        for url in request.urls:
            if url_type is None:
                url_type = url['type']
            new_url = dict()
            new_url['url'] = url['url']
            if 'unique_key' in url.keys():
                md5 = util_md5(escape_string(url['url']) + str(url['unique_key']))
            else:
                md5 = util_md5(escape_string(url['url']))
            new_url['md5'] = md5
            new_urls.append(new_url)

            url['unique_md5'] = md5
        if len(new_urls) > 0:
            params = {
                'user_id': self.user_id,
                'url_type': url_type,
                'header': request.headers,
                'redirect': 0,
                'priority': 2,
                'single': 0,
                'store_type': store_type,
                'urls': new_urls,
                'concurrent_num': 0,  # 默认
                'conf_district_id': 0
            }
            if 'redirect' in request.config and request.config['redirect'] == 1:
                params['redirect'] = request.config['redirect']
            if 'post_data' in request.config:
                params['post_data'] = request.config['post_data']
            if 'filter' in request.config:
                params['filter'] = request.config['filter']
            return params
        return None

    def set(self, request):
        try:
            results = dict()
            param = self.downloader_set_param(request)
            for url in param['urls']:
                results[url['md5']] = 1
            return results
        except Exception:
            print(traceback.format_exc())
            return 0

    @staticmethod
    def encoding(data):
        types = ['utf-8', 'gb2312', 'gbk', 'gb18030', 'iso-8859-1']
        for t in types:
            try:
                return data.decode(t)
            except Exception:
                pass
        return None

    def get(self, request):
        param = self.downloader_set_param(request)
        if param is None:
            return 0
        urls = param['urls']
        if len(urls) > 0:
            try:
                results = dict()
                url_type = param.get("url_type", 1)

                headers = param.get("header", {})
                data = param.get("post_data", None)
                method = param.get("method", None)
                filter = param.get('filter', 0)

                for url in urls:
                    result = {"url": url["url"], "status": "3", "result": "", "header": "",
                              "redirect_url": "", "code": 0, "type": url_type}

                    # start = time.time()
                    self.download_html_by_requests(url["url"], result, data, headers, req=requests, filter=filter,
                                                   method=method)
                    # print(
                    #     "url: {}; length: {}; time: {}".format(url["url"], len(result["result"]), time.time() - start))

                    results[url['md5']] = result
                return results
            except Exception:
                print(traceback.format_exc())
        return 0

    def download_html_by_requests(self, url, result, data, headers, req=None, filter=0, method=None):
        """
        :param task:
        :param result:
        :param data:
        :param headers:
        :param req:        requests
        :param filter:  0 默认不过滤 1 过滤
        :return:
        """
        try:
            response = self.transfer_requests(req, url, data, headers, None, method)
            try:
                if response.encoding == 'ISO-8859-1':
                    encodings = requests.utils.get_encodings_from_content(response.text)
                    if encodings:
                        encoding = encodings[0]
                    else:
                        encoding = response.apparent_encoding
                else:
                    encoding = response.encoding
            except:
                encoding = "utf-8"

            result["code"] = 0 if response.status_code == 200 else response.status_code
            if url != response.url:
                result["redirect_url"] = response.url

            result["status"] = 2
            encode_content = response.content.decode(encoding, 'replace').encode('utf-8', 'replace')
            if filter == 1:
                encode_content = self.filter_html(encode_content)

            if not isinstance(encode_content, str):
                encode_content = encode_content.decode(encoding="utf-8", errors='ignore')  # bytes to str
            result["result"] = encode_content
            if str(result["type"]) == "2":
                result["header"] = str(self.get_requests_cookie(response))
        except requests.exceptions.ConnectTimeout:
            # 代理问题 连接超时
            print(traceback.format_exc())
        except Exception:
            # url 请求 问题
            print(traceback.format_exc())

    @staticmethod
    def get_requests_cookie(res):
        cookies = requests.utils.dict_from_cookiejar(res.cookies)
        cookies_str = ""
        for k in cookies:
            cookies_str += ";{}={}".format(k, cookies[k])
        return cookies_str[1: -1]

    def transfer_requests(self, req, url, data, headers, proxies, method):
        if proxies:
            if method:
                if method == "get":
                    response = req.get(url=url, timeout=self.REQUEST_TIMEOUT, proxies=proxies,
                                       headers=headers, verify=False)
                else:
                    response = req.post(url=url, timeout=self.REQUEST_TIMEOUT, proxies=proxies,
                                        data=data, headers=headers, verify=False)
            else:
                if data:
                    response = req.post(url=url, timeout=self.REQUEST_TIMEOUT, proxies=proxies,
                                        data=data, headers=headers, verify=False)
                else:
                    response = req.get(url=url, timeout=self.REQUEST_TIMEOUT, proxies=proxies,
                                       headers=headers, verify=False)
        else:
            if method:
                if method == "get":
                    response = req.get(url=url, timeout=self.REQUEST_TIMEOUT, proxies=proxies,
                                       headers=headers, verify=False)
                else:
                    response = req.post(url=url, timeout=self.REQUEST_TIMEOUT, proxies=proxies,
                                        data=data, headers=headers, verify=False)
            else:
                if data:
                    response = req.post(url=url, timeout=self.REQUEST_TIMEOUT, proxies=proxies,
                                        data=data, headers=headers, verify=False)
                else:
                    response = req.get(url=url, timeout=self.REQUEST_TIMEOUT, proxies=proxies,
                                       headers=headers, verify=False)
        return response

    @staticmethod
    def filter_html(content):
        """
        过滤html 无用字符串
        备注
            1、 去除换行
            2、 去除<script
            3、 去<style
            4、 多空格 变成一个
            5、 多tab 键 变成一个
            6、 去<link

            --
            去备注  <!--  -->
            去 style none
        :param content:
        :return:
        """
        if not isinstance(content, str):
            content = content.decode(encoding="utf-8", errors='ignore')  # bytes to str
        content = re.sub('\\n', ' ', content)
        tlist = re.findall(r'<script(.*?)</script>', content)
        for t in tlist:
            content = content.replace("<script" + t + "</script>", "")
        tlist = re.findall(r'<style(.*?)</style>', content)
        for t in tlist:
            content = content.replace("<style" + t + "</style>", "")
        tlist = re.findall(r'<link(.*?)>', content)
        for t in tlist:
            content = content.replace("<link" + t + ">", "")
        content = re.sub(' +', ' ', content)
        content = re.sub('\\t+', ' ', content)
        content = re.sub('\\r+', ' ', content)
        return content


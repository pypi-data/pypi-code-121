"""
baserequest
"""
import json
import traceback

import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from re_common.baselibrary.utils.baseurl import BaseUrl
from re_common.baselibrary.utils.core.mlamada import closeResult
from re_common.baselibrary.utils.core.requests_core import USER_AGENT, set_proxy

ok = requests.codes.ok


class BaseRequest(object):
    def __init__(self, logger=None):
        if logger is None:
            from re_common.baselibrary import MLogger
            logger = MLogger().streamlogger
        self.logger = logger

        self.sn = requests.Session()
        self.proxies = None
        # 是否使用类的代理覆盖传入的代理
        self._is_use_proxy = False

    def set_sn(self):
        sn = requests.Session()
        self.sn = sn
        return sn

    def set_proxy(self, proxy):
        """
        配置代理
        :param proxy:
        :return:
        """
        proxies = set_proxy(proxy)
        self.proxies = proxies
        return proxies

    def is_use_proxy(self, boolvalues):
        """
        设置是否使用全局代理
        :param boolvalues:
        :return:
        """
        self._is_use_proxy = boolvalues

    def set_sn_header(self, useragent=None):
        if USER_AGENT != None:
            self.sn.headers['User-Agent'] = useragent
        else:
            self.sn.headers['User-Agent'] = USER_AGENT

    def base_request(self, url, sn=None, endstring="", marks=None, **kwargs):
        """
        网络请求的基本结构
        :param marks:
        :param url:  请求的url
        :param sn:  会话  sn = requests.Session() 这样保存会话
        :param endstring:  判断html的结束字符串 一般html默认 </html> 结尾
        :param mark:  标志符 默认为""  你的结果中的一些字符串或特殊的标签都可以
        :param kwargs: requests请求的一些参数
        :return: true表示成功 false表示失败或需要进行检查的数据，同时返回r
        BoolResult, errString, r
        """
        if marks is None:
            marks = []
        r = None
        exMsg = None
        try:
            urllib3.disable_warnings(InsecureRequestWarning)
            self.logger.info(url)
            # 对https 自动加上verify参数为False
            if BaseUrl.urlScheme(url) == "https":
                kwargs["verify"] = False
            if self._is_use_proxy:
                kwargs["proxies"] = self.proxies
            if sn:
                r = sn.get(url=url, **kwargs)
            else:
                r = requests.get(url=url, **kwargs)
        except:
            exMsg = '* ' + traceback.format_exc()
            self.logger.error(exMsg)
        finally:
            closeResult(r)
        if exMsg:
            self.logger.info("判断到except，请求出项错误")
            return False, "request", r

        if r.status_code != 200:
            self.logger.warning('r.status_code:' + str(r.status_code))
            return False, "code", r

        r.encoding = r.apparent_encoding
        if endstring:
            """
            请求有可能是html或者json等，如果有需要判断html结束的才启动这个选项
            """

            html = r.text.strip()
            if not html.endswith(endstring):
                self.logger.info("not endswith {}".format(endstring))
                return False, "endString", r

        if marks:
            """
           验证请求是否成功  通过一个特征字符串或者html的标签来查找 保证下载的页面是我需要的页面
           而不是错误页面
           特征值有可能没有是网页出现问题  有可能是请求不完全 这个依照情况而定
            """

            html = r.text.strip()
            for mark in marks:
                if html.find(mark) == -1:
                    self.logger.info('not found {}'.format(mark))
                    return False, "Feature err", r
                else:
                    self.logger.info("found mark is {}".format(mark))

        return True, "", r

    def base_request_post(self, url, sn=None, data=None, endstring="", marks=None, **kwargs):
        """
        网络请求的基本结构
        :param marks:
        :param url:  请求的url
        :param sn:  会话  sn = requests.Session() 这样保存会话
        :param endstring:  判断html的结束字符串 一般html默认 </html> 结尾
        :param mark:  标志符 默认为""  你的结果中的一些字符串或特殊的标签都可以
        :param kwargs: requests请求的一些参数
        :return: true表示成功 false表示失败或需要进行检查的数据，同时返回r
        """
        if marks is None:
            marks = []
        r = None
        exMsg = None
        try:
            urllib3.disable_warnings(InsecureRequestWarning)
            self.logger.info(url)
            # 对https 自动加上verify参数为False
            if BaseUrl.urlScheme(url) == "https":
                kwargs["verify"] = False
            if self._is_use_proxy:
                kwargs["proxies"] = self.proxies
            if sn:
                r = sn.post(url=url, data=data, **kwargs)
            else:
                r = requests.post(url=url, data=data, **kwargs)
        except:
            exMsg = '* ' + traceback.format_exc()
            self.logger.error(exMsg)
        finally:
            closeResult(r)

        if exMsg:
            return False, "request", r

        if r.status_code != 200:
            self.logger.warning('r.status_code:' + str(r.status_code))
            return False, "code", r

        r.encoding = r.apparent_encoding

        if endstring:
            """
            请求有可能是html或者json等，如果有需要判断html结束的才启动这个选项
            """
            html = r.text.strip()
            if not html.endswith(endstring):
                self.logger.info("not endswith {}".format(endstring))
                return False, "endString", r

        if marks:
            """
           验证请求是否成功  通过一个特征字符串或者html的标签来查找 保证下载的页面是我需要的页面
           而不是错误页面
           特征值有可能没有是网页出现问题  有可能是请求不完全 这个依照情况而定
            """
            html = r.text.strip()
            for mark in marks:
                if html.find(mark) == -1:
                    self.logger.info('not found {}'.format(mark))
                    return False, "Feature err", r
                else:
                    self.logger.info("found mark is {}".format(mark))

        return True, "", r

    def post_api(self, url, data, **kwargs):
        dicts = {}
        dicts["result_string"] = None
        dicts["result"] = None
        dicts["exMsg"] = None
        dicts["errtype"] = ""
        r = None
        try:
            try:
                urllib3.disable_warnings(InsecureRequestWarning)
                self.logger.info(url)
                # 对https 自动加上verify参数为False
                if BaseUrl.urlScheme(url) == "https":
                    kwargs["verify"] = False
                if self._is_use_proxy:
                    kwargs["proxies"] = self.proxies
                r = requests.post(url=url, data=data, **kwargs)
            except:
                dicts["exMsg"] = traceback.format_exc()
                dicts["errtype"] = "请求错误，请查看exMsg"
                return False, dicts

            dicts_rs = json.loads(r.text)
            dicts["result"] = dicts_rs
            if dicts_rs["status"] == "SUCCESS":
                return True, dicts
            else:
                self.logger.info(r.text)
                return False, dicts
        except:
            if r is not None:
                dicts["result_string"] = r.text
                self.logger.error("出现结果json错误，不应该，请检查:" + r.text)
                self.logger.error(traceback.format_exc())
                dicts["errtype"] = "json错误，请查看result_string"
                return False, dicts
            else:
                dicts["result_string"] = ""
                self.logger.error("出现结果json错误，不应该，请检查,r为空")
                self.logger.error(traceback.format_exc())
                dicts["errtype"] = "json错误，没有数据"
                return False, dicts

    def get_api(self, url, params=None, **kwargs):
        dicts = {}
        dicts["result_string"] = None
        dicts["result"] = None
        dicts["exMsg"] = None
        dicts["errtype"] = ""
        r = None
        try:
            try:
                urllib3.disable_warnings(InsecureRequestWarning)
                self.logger.info(url)
                # 对https 自动加上verify参数为False
                if BaseUrl.urlScheme(url) == "https":
                    kwargs["verify"] = False
                if self._is_use_proxy:
                    kwargs["proxies"] = self.proxies
                r = requests.get(url=url, params=params, **kwargs)
            except:
                dicts["exMsg"] = traceback.format_exc()
                dicts["errtype"] = "请求错误，请查看exMsg"
                return False, dicts

            dicts_rs = json.loads(r.text)
            dicts["result"] = dicts_rs
            if dicts_rs["status"] == "SUCCESS":
                return True, dicts
            else:
                self.logger.info(r.text)
                return False, dicts
        except:
            if r is not None:
                dicts["result_string"] = r.text
                self.logger.error("出现结果json错误，不应该，请检查:" + r.text)
                self.logger.error(traceback.format_exc())
                dicts["errtype"] = "json错误，请查看result_string"
                return False, dicts
            else:
                dicts["result_string"] = ""
                self.logger.error("出现结果json错误，不应该，请检查,r为空")
                self.logger.error(traceback.format_exc())
                dicts["errtype"] = "json错误，没有数据"
                return False, dicts

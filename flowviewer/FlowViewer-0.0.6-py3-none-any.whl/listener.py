# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   listener.py
"""
from json import JSONDecodeError, loads
from time import sleep
from typing import Union, List, Iterable

from DrissionPage.mix_page import MixPage
from pychrome import CallMethodException
from requests.structures import CaseInsensitiveDict

from .base import BaseListener


class ResponseData(object):
    """返回的数据包管理类"""

    def __init__(self, request_id: str, response: dict, body: str, tab: str, target: str):
        """初始化                               \n
        :param response: response的数据
        :param body: response包含的内容
        :param tab: 产生这个数据包的tab的id
        :param target: 监听目标
        """
        self.request_id = request_id
        self.response = CaseInsensitiveDict(response)
        self.raw_body = body
        self.tab = tab
        self.target = target
        self.post_data = None
        self._json_body = None

    def __getattr__(self, item):
        """可用：url、status、statusText、headers、headersText、mimeType、requestHeaders、requestHeadersText、
        connectionReused、connectionId、remoteIPAddress、remotePort、fromDiskCache、fromServiceWorker、
        fromPrefetchCache、encodedDataLength、timing、serviceWorkerResponseSource、responseTime、
        cacheStorageCacheName、protocol、securityState、securityDetails"""
        return self.response.get(item, None)

    def __getitem__(self, item):
        return self.response.get(item, None)

    @property
    def body(self) -> Union[str, dict]:
        """返回body内容，如果是json格式，自动进行转换，其它格式直接返回文本"""
        if self._json_body is not False and self.response.get('mimeType', None) == 'application/json':
            if self._json_body is None:
                try:
                    self._json_body = loads(self.raw_body)
                except JSONDecodeError:
                    self._json_body = False
                    return self.raw_body
            return self._json_body

        else:
            return self.raw_body


class Listener(BaseListener):
    """浏览器的数据包监听器"""

    def __init__(self, browser: Union[str, int, MixPage, None] = None, tab_handle: str = None):
        """初始化                                                                      \n
        :param browser: 要监听的url、端口或MixPage对象，MixPage对象须设置了local_port参数。
                        为None时自动从系统中寻找可监听的浏览器
        :param tab_handle: 要监听的标签页的handle，不输入读取当前活动标签页
        """
        super().__init__(browser, tab_handle)

    def to_tab(self,
               handle_or_id: str = None,
               browser: Union[str, int, MixPage, None] = None) -> None:
        """设置要监听的标签页                                                   \n
        :param handle_or_id: 要监听的标签页的handle，不输入读取当前活动标签页
        :param browser: 更换别的浏览器
        :return: None
        """
        super().to_tab(handle_or_id, browser)
        self._tab.Network.enable()

    def get_results(self, target: str = None) -> List[ResponseData]:
        """获取结果列表                                        \n
        :param target: 要获取的目标，为None时获取全部
        :return: 结果数据组成的列表
        """
        return super().get_results(target)

    def steps(self, gap: int = 1) -> Iterable[List[ResponseData]]:
        """用于单步操作，可实现没收到若干个数据包执行一步操作（如翻页）                 \n
        于是可以根据数据包是否加载完成来决定是否翻页，无须从页面dom去判断是否加载完成     \n
        大大简化代码，提高可靠性                                                   \n
        eg: for i in listener.steps(2):                                        \n
                btn.click()                                                    \n
        :param gap: 每接收到多少个数据包触发
        :return: 用于在接收到监听目标时触发动作的可迭代对象
        """
        while self.listening or not self._tmp.empty():
            while self._tmp.qsize() >= gap:
                yield [self._tmp.get(False) for _ in range(gap)]

            sleep(.1)

    def _loading_finished(self, **kwargs) -> None:
        """请求完成时处理方法"""
        if not self._is_continue():
            return

        request_id = kwargs['requestId']
        target = self._request_ids.pop(request_id, None)
        if target is None:
            return

        target, response = target.values()
        response = ResponseData(request_id, response, self._get_response_body(request_id), self.tab_id, target)
        r = response.response.get('requestHeaders', None)
        if r and r.get(':method', '').lower() == 'post':
            response.post_data = self._get_post_data(request_id)

        self._caught_count += 1
        self._tmp.put(response)
        self.results.append(response)

        if not self._is_continue():
            self.stop()

    def _response_received(self, **kwargs) -> None:
        """接收到返回信息时处理方法"""
        if self.targets is True:
            self._request_ids[kwargs['requestId']] = {'target': True, 'response': kwargs['response']}

        else:
            for target in self.targets:
                if target in kwargs['response']['url']:
                    self._request_ids[kwargs['requestId']] = {'target': target, 'response': kwargs['response']}

    def _get_response_body(self, request_id: str) -> Union[str, None]:
        """获取返回的内容                  \n
        :param request_id: 请求的id
        :return: 返回内容的文本
        """
        try:
            return self._tab.call_method('Network.getResponseBody', requestId=request_id)['body']
        except CallMethodException:
            return ''

    def _get_post_data(self, response_or_id: Union[str, ResponseData]) -> Union[str, None]:
        """获取请求的post数据                                  \n
        :param response_or_id: ResponseData对象或requestId字符串
        :return: post数据字符串
        """
        if isinstance(response_or_id, ResponseData):
            response_or_id = response_or_id.request_id

        try:
            return self._tab.call_method('Network.getRequestPostData', requestId=response_or_id)['postData']
        except:
            return None

    def _set_callback_func(self) -> None:
        """设置回调函数"""
        self._tab.Network.responseReceived = self._response_received
        self._tab.Network.loadingFinished = self._loading_finished

    def _stop(self) -> None:
        """停止前要做的工作"""
        self._tab.Network.responseReceived = None
        self._tab.Network.loadingFinished = None

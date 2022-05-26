# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   request_man.py
"""
from time import sleep
from typing import Union, Tuple, List, Iterable

from DrissionPage.mix_page import MixPage
from requests.structures import CaseInsensitiveDict

from .base import BaseListener


class RequestData(object):
    """网络请求数据包管理类"""

    def __init__(self, data: dict, tab: str, target: Union[str, bool]):
        """初始化                               \n
        :param data: 请求的数据
        :param tab: 产生这个数据包的tab的id
        :param target: 监听目标
        """
        self._data = data
        self.request_id = data.get('networkId', None)
        self.fetch_id = data.get('requestId', None)
        self.request = CaseInsensitiveDict(data['request'])
        self.tab = tab
        self.target = target

    def __getattr__(self, item):
        return self.request.get(item, None)

    def __getitem__(self, item):
        return self.request.get(item, None)

    @property
    def headers(self):
        h = self.request.get('headers', None)
        return CaseInsensitiveDict(h) if h else None


class RequestMan(BaseListener):
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
        if self.listening:
            self._tab.Fetch.disable()

        super().to_tab(handle_or_id, browser)

        if self.listening:
            self._tab.Fetch.enable()

    def listen(self,
               targets: Union[str, List[str], Tuple, bool, None] = None,
               count: int = None,
               timeout: float = None,
               asyn: bool = True) -> None:
        """拦截目标请求，直到超时或达到拦截个数，每次拦截前清空结果                                     \n
        可监听多个目标，请求url包含这些字符串就会被记录                                               \n
        :param targets: 要监听的目标字符串或其组成的列表，True监听所有，None则保留之前的目标不变
        :param count: 要记录的个数，到达个数停止监听
        :param timeout: 监听最长时间，到时间即使未达到记录个数也停止，None为无限长
        :param asyn: 是否异步监听
        :return: None
        """
        self._tab.Fetch.enable()
        super().listen(targets, count, timeout)

    def get_results(self, target: str = None) -> List[RequestData]:
        """获取结果列表                                \n
        :param target: 要获取的目标，为None时获取全部
        :return: 结果数据组成的列表
        """
        return super().get_results(target)

    def steps(self, gap: int = 1) -> Iterable[List[RequestData]]:
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

    def _request_paused(self, **kwargs) -> None:
        """接收到请求时的回调函数"""
        if not self._is_continue():
            return

        fetch_id = kwargs['requestId']
        if self.targets is True:
            request = RequestData(kwargs, self.tab_id, True)
            self._caught_count += 1
            self._tmp.put(request)
            self.results.append(request)

        else:
            for target in self.targets:
                if target in kwargs['request']['url']:
                    request = RequestData(kwargs, self.tab_id, True)
                    self._caught_count += 1
                    self._tmp.put(request)
                    self.results.append(request)

        self._tab.Fetch.continueRequest(requestId=fetch_id)

    def _set_callback_func(self) -> None:
        """设置监听的回调函数"""
        self._tab.Fetch.requestPaused = self._request_paused

    def _stop(self) -> None:
        """停止监听前要做的工作"""
        self._tab.Fetch.disable()
        self._tab.Fetch.requestPaused = None

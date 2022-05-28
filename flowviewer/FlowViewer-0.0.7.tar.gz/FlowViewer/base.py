# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   base.py
"""
from abc import abstractmethod
from queue import Queue
from threading import Thread
from time import perf_counter, sleep
from typing import Union, Tuple, List
from warnings import filterwarnings

from DrissionPage.mix_page import MixPage
from pychrome import Tab
from requests import get

filterwarnings("ignore")


class BaseListener(object):
    """监听器基类"""

    def __init__(self,
                 browser: Union[str, int, MixPage, None] = None,
                 tab_handle: str = None):
        """初始化                                                                      \n
        :param browser: 要监听的url、端口或MixPage对象，MixPage对象须设置了local_port参数。
                        为None时自动从系统中寻找可监听的浏览器
        :param tab_handle: 要监听的标签页的handle，不输入读取当前活动标签页
        """
        self._browser = None
        self._tab: Union[None, Tab] = None  # Tab对象
        self._tmp: Union[None, Queue] = None  # 临存捕捉到的数据
        self._request_ids: Union[None, dict] = None  # 暂存须要拦截的请求id

        self._caught_total_count = None  # 当次监听的数量上限
        self._caught_count = None  # 当次已监听到的数量
        self._begin_time = None  # 当次监听开始时间
        self._timeout = None  # 当次监听超时时间

        self.listening = False
        self.targets = True  # 默认监听所有
        self.results: list = []
        self.tab_id = None  # 当前tab的id
        self.show_msg = True
        self._set_browser(browser)
        self.to_tab(tab_handle)

    @property
    def active_tab(self) -> str:
        """返回当前活动标签页的id"""
        return _get_active_tab_id(self._browser)

    def to_tab(self,
               handle_or_id: str = None,
               browser: Union[str, int, MixPage, None] = None) -> None:
        """设置要监听的标签页                                                   \n
        :param handle_or_id: 要监听的标签页的handle，不输入读取当前活动标签页
        :param browser: 更换别的浏览器
        :return: None
        """
        if browser:
            self._set_browser(browser)

        self.tab_id = handle_or_id.split('-')[-1] if handle_or_id else self.active_tab
        tab_data = {"id": self.tab_id, "type": "page",
                    "webSocketDebuggerUrl": f"ws://{self._browser}/devtools/page/{self.tab_id}"}
        self._tab = Tab(**tab_data)
        self._tab.start()

        if self.listening:
            self._set_callback_func()

    def set_targets(self, targets: Union[str, List[str], Tuple[str], bool, None]) -> None:
        """设置要拦截的目标，可以设置多个                               \n
        :param targets: 要监听的目标字符串或其组成的列表，True监听所有
        :return: None
        """
        if isinstance(targets, str):
            self.targets = [targets]
        elif isinstance(targets, tuple):
            self.targets = list(targets)
        elif isinstance(targets, list) or targets is True:
            self.targets = targets
        else:
            raise TypeError('targets参数只接收字符串、字符串组成的列表、True、None')

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
        if targets:
            self.set_targets(targets)

        self.listening = True
        self.results = []
        self._request_ids = {}
        self._tmp = Queue(maxsize=0)

        self._caught_count = 0
        self._begin_time = perf_counter()
        self._timeout = timeout
        self._caught_total_count = count

        self._set_callback_func()

        if asyn:
            Thread(target=self._wait_to_stop).start()
        else:
            self._wait_to_stop()

        if self.show_msg:
            print('开始监听')

    def stop(self) -> None:
        """停止监听"""
        self._stop()
        if self.listening:
            self.listening = False
            if self.show_msg:
                print('停止监听')

    def wait(self) -> None:
        """等等监听结束"""
        while self.listening:
            sleep(.5)

    def get_results(self, target: str = None):
        """获取结果列表                                        \n
        :param target: 要获取的目标，为None时获取全部
        :return: 结果数据组成的列表
        """
        return self.results if target is None else [i for i in self.results if i.target == target]

    def _wait_to_stop(self) -> None:
        """当收到停止信号、到达须获取结果数、到时间就停止"""
        while self._is_continue():
            sleep(.5)

        self.stop()

    def _is_continue(self) -> bool:
        """是否继续当前监听"""
        return self.listening \
               and (self._caught_total_count is None or self._caught_count < self._caught_total_count) \
               and (self._timeout is None or perf_counter() - self._begin_time < self._timeout)

    def _set_browser(self, browser: Union[str, int, MixPage, None] = None) -> None:
        """设置浏览器ip:port                                                               \n
        :param browser: 要监听的url、端口或MixPage对象，MixPage对象须设置了local_port参数。
                        为None时自动从系统中寻找可监听的浏览器
        :return: None
        """
        if isinstance(browser, MixPage):
            browser = browser.drission.driver_options.debugger_address

        elif isinstance(browser, int):
            browser = f'127.0.0.1:{browser}'

        self._browser = browser or _find_chrome()
        if self._browser is None:
            raise RuntimeError('未找到可监听的浏览器。')

    @abstractmethod
    def steps(self, gap: int = 1):
        """用于单步操作，可实现没收到若干个数据包执行一步操作（如翻页）                 \n
        :param gap: 每接收到多少个数据包触发
        :return: 用于在接收到监听目标时触发动作的可迭代对象
        """
        pass

    @abstractmethod
    def _set_callback_func(self):
        """设置监听请求的回调函数"""
        pass

    @abstractmethod
    def _stop(self) -> None:
        """停止监听前要做的工作"""
        pass


def _find_chrome() -> Union[str, None]:
    """在系统进程中查找开启调试的Chrome浏览器，只能在Windows系统使用            \n
    :return: ip:port
    """
    from os import popen
    from re import findall, DOTALL, search

    txt = popen('tasklist  /fi "imagename eq chrome.exe" /nh').read()
    pids = findall(r' (\d+) [c,C]', txt, flags=DOTALL)
    for pid in pids:
        txt = popen(f'netstat -ano | findstr "{pid}"').read()
        r = search(r'TCP {4}(\d+.\d+.\d+.\d+:\d+).*?LISTENING.*?\n', txt, flags=DOTALL)
        if r:
            return r.group(1)


def _get_active_tab_id(url: str) -> str:
    """获取浏览器活动标签页id          \n
    :param url: 浏览器ip:port
    :return: 文本形式返回tab id
    """
    try:
        r = get(f'http://{url}/json', json=True, timeout=2).json()
        for i in r:
            if i['type'] == 'page':
                return i['id']

    except Exception:
        raise RuntimeError('未能定位标签页。')

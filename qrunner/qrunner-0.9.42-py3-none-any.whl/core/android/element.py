import inspect
import json
import os
import time
import typing
from multiprocessing.dummy import Pool as ThreadPool
from typing import Union
from uiautomator2 import UiObject
from uiautomator2.xpath import XPathSelector
from qrunner.utils.log import logger
from qrunner.utils.config import conf
from qrunner.core.android.driver import AndroidDriver
from qrunner.utils.exceptions import NoSuchElementException
from qrunner.utils.decorate import step


class AndroidElement(object):
    """
    安卓元素定义
    """
    def __init__(self, driver=None, **kwargs):
        # 从kwargs中删掉并返回index
        self._index = kwargs.pop('index', 0)
        self.desc = kwargs.pop('desc', '')
        # 参数初始化
        self._xpath = kwargs.get('xpath', '')
        self._kwargs = kwargs
        self._element: Union[UiObject, XPathSelector]
        self._driver: AndroidDriver = driver
        self._serial_no = self._driver.serial_no
        self._pkg_name = self._driver.pkg_name
        self._resourceId = kwargs.pop('resourceId', '')
        if self._resourceId:
            kwargs['resourceId'] = f'{self._pkg_name}:{self._resourceId}'
        self._d = self._driver.d

    def handle_alert(self):
        """
        根据不同定位方式进行点击
        @return:
        """
        def click_alert(loc):
            if 'id/' in loc:
                element = self._d(resourceId=f'{self._pkg_name}:{loc}')
            elif '//' in loc:
                element = self._d.xpath(loc)
            else:
                element = self._d(text=loc)
            element.click_exists(timeout=1)

        # 多线程执行点击过程
        alert_list = conf.get_item('app', 'android_alert')
        print(f'异常弹窗列表: {alert_list}')
        pool = ThreadPool(len(alert_list))
        if alert_list:
            pool.map(click_alert, alert_list)
        else:
            logger.debug("弹窗设置列表为空")
        logger.debug('处理异常弹窗完成')

    def _find_element(self, retry=3, timeout=3):
        """
        循环查找元素，查找失败先处理弹窗后重试，后面再考虑xpath要不要用.all()改造一下
        @param retry: 重试次数
        @param timeout: 每次查找超时时间
        @return: 找到的元素列表
        """
        logger.info(f'查找元素: {self._kwargs},{self._index}')
        self._element = self._d.xpath(self._xpath) if \
            self._xpath else self._d(**self._kwargs)[self._index]
        self.handle_alert()  # 处理异常弹窗
        while not self._element.wait(timeout=timeout):
            if retry > 0:
                retry -= 1
                logger.warning(f'重试 查找元素： {self._kwargs},{self._index}')
                self.handle_alert()  # 处理异常弹窗
            else:
                frame = inspect.currentframe().f_back
                caller = inspect.getframeinfo(frame)
                logger.warning(f'【{caller.function}:{caller.lineno}】未找到元素 {self._kwargs}')
                return None
        return self._element

    def get_element(self, retry=3, timeout=3):
        """
        针对元素定位失败的情况，抛出NoSuchElementException异常
        @param retry:
        @param timeout:
        @return:
        """
        element = self._find_element(retry=retry, timeout=timeout)
        if element is None:
            self._driver.screenshot(f'[控件 {self.desc} 定位失败]')
            raise NoSuchElementException(f'[控件 {self.desc} 定位失败]')
        return element

    @property
    def info(self):
        logger.info(f'获取元素: {self._kwargs} 的所有信息')
        return self.get_element().info

    @property
    def text(self):
        logger.info(f'获取元素: {self._kwargs} 的文本')
        return self.get_element().info.get('text')

    @property
    def bounds(self):
        logger.info(f'获取元素: {self._kwargs} 的坐标')
        return self.get_element().info.get('bounds')

    @property
    def rect(self):
        logger.info(f'获取元素: {self._kwargs} 左上角的坐标以及宽高')
        bounds = self.get_element().info.get('bounds')
        x = bounds['left']
        y = bounds['top']
        width = bounds['right'] - x
        height = bounds['bottom'] - y
        return [x, y, width, height]

    @property
    def visibleBounds(self):
        logger.info(f'获取元素: {self._kwargs} 的可见坐标')
        return self.get_element().info.get('visibleBounds')

    @property
    def focusable(self):
        logger.info(f'获取元素: {self._kwargs} 是否聚焦')
        return self.get_element().info.get('focusable')

    @property
    def selected(self):
        logger.info(f'获取元素: {self._kwargs} 是否选中')
        return self.get_element().info.get('selected')

    def child(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs},{self._index} 的子元素{kwargs}')
        return self.get_element().child(*args, **kwargs)

    def brother(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs},{self._index} 的兄弟元素{kwargs}')
        return self.get_element().sibling(*args, **kwargs)

    def left(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs} 左边的元素 {kwargs}')
        return self.get_element().left(*args, **kwargs)

    def right(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs} 右边的元素 {kwargs}')
        return self.get_element().right(*args, **kwargs)

    def up(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs} 上边的元素 {kwargs}')
        return self.get_element().up(*args, **kwargs)

    def down(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs} 下边的元素 {kwargs}')
        return self.get_element().down(*args, **kwargs)

    def exists(self, timeout=1):
        logger.info(f'判断元素是否存在: {self._kwargs},{self._index}')
        element = self._find_element(retry=0, timeout=timeout)
        if element is None:
            # self._driver.screenshot(f'元素定位失败')
            return False
        return True

    def _adapt_center(self, e: typing.Union[UiObject, XPathSelector], offset=(0.5, 0.5)):
        if isinstance(e, UiObject):
            return e.center(offset=offset)
        else:
            return e.offset(offset[0], offset[1])

    def click(self, offset=(0.5, 0.5)):
        logger.info(f'点击元素: {self._kwargs},{self._index}')
        element = self.get_element()
        print('点击元素')
        # 这种方式经常点击不成功，感觉是页面刷新有影响
        # element.click()
        x, y = self._adapt_center(element, offset=offset)
        self._d.click(x, y)
        print('点击成功')

    def click_exists(self):
        logger.info(f'存在才点击元素: {self._kwargs},{self._index}')
        if self.exists():
            self.click()

    def click_gone(self):
        logger.info(f'等元素 {self._kwargs} 消失后再点击')
        flag = self.get_element().click_gone()
        logger.info(flag)
        return flag

    def wait_gone(self, timeout=3):
        logger.info(f'等元素 {self._kwargs} 消失')
        flag = self.get_element().wait_gone(timeout=timeout)
        logger.info(flag)
        return flag

    def long_click(self):
        logger.info(f'长按元素 {self._kwargs}')
        self.get_element().long_click()

    def set_text(self, text):
        logger.info(f'输入文本: {text}')
        self.get_element().set_text(text)

    def clear_text(self):
        logger.info('清除文本')
        self.get_element().clear_text()

    def drag_to(self, *args, **kwargs):
        logger.info(f'从当前元素{self._kwargs},{self._index}, 拖动到元素: {kwargs}')
        self.get_element().drag_to(*args, **kwargs)

    def swipe_left(self):
        logger.info(f'往左滑动元素: {self._kwargs},{self._index}')
        self.get_element().swipe("left")

    def swipe_right(self):
        logger.info(f'往右滑动元素: {self._kwargs},{self._index}')
        self.get_element().swipe("right")

    def swipe_up(self):
        logger.info(f'往上滑动元素: {self._kwargs},{self._index}')
        self.get_element().swipe("up")

    def swipe_down(self):
        logger.info(f'往下滑动元素: {self._kwargs},{self._index}')
        self.get_element().swipe("down")




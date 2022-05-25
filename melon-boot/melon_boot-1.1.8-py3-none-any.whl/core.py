# -*- encoding: utf-8 -*-
"""
@Author  : zh_o
"""
import os.path
import sys
import time
import uuid
from typing import Tuple, List, Text, Callable

import allure
from selenium.common.exceptions import WebDriverException, NoSuchElementException, InvalidSelectorException, \
    StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from melon.settings import get_config
from melon.webdrivers import driver
from melon.loggers import logger


class MelonElement(WebElement):
    """单元素"""

    def __init__(self, label: Text, by: By, loc: Text, timeout=None):
        super(MelonElement, self).__init__(None, None)
        self.label = label
        self.timeout = timeout
        self.by = by
        self.loc = loc
        self.locator = (by, loc)

    def __repr__(self):
        return '{"label": "%s", "locator": ["%s", "%s"]}' % (self.label, self.by, self.loc)


class BasePage:
    """基础 page object"""

    def __init__(self):
        self.driver = driver
        self.element_dict = object.__getattribute__(self, '__dict__')
        self.label_field = '_label'

    def find_element(self, locator: Tuple) -> WebElement:
        """定位单个元素"""
        element = self.driver.find_element(*locator)
        self.__proxy_allure(element)
        return element

    def find_elements(self, locator: Tuple) -> List[WebElement]:
        """定位多个元素"""
        elements = self.driver.find_elements(*locator)
        self.__proxy_allure(*elements)
        return elements

    def find_element_await(self, locator: Tuple, timout: float) -> WebElement:
        """定位单个元素并等待"""
        element = self.webdriver_wait(timout).until(EC.presence_of_element_located(locator))
        self.__proxy_allure(element)
        return element

    def find_elements_await(self, locator: Tuple, timout: float) -> List[WebElement]:
        """定位多个元素并等待"""
        elements = self.webdriver_wait(timout).until(EC.presence_of_all_elements_located(locator))
        self.__proxy_allure(*elements)
        return elements

    def switch_to(self) -> SwitchTo:
        """切换"""
        return self.driver.switch_to

    def action_chains(self) -> ActionChains:
        """构件执行链"""
        return ActionChains(self.driver)

    def webdriver_wait(self, timout=15.0, poll_frequency=0.5) -> WebDriverWait:
        """显示等待"""
        return WebDriverWait(self.driver, timout, poll_frequency)

    def wait_until_presence_of_located(self, by: By, loc: Text, timout=15.0):
        """等待直到定位元素出现"""
        self.webdriver_wait(timout).until(EC.presence_of_element_located((by, loc)))

    def wait_until_visibility(self, element: WebElement, timout=15.0):
        """等待直到元素可见"""
        self.webdriver_wait(timout).until(EC.visibility_of(element))

    def wait_until_visibility_of_located(self, by: By, loc: Text, timout=15.0):
        """等待直到定位元素可见"""
        self.webdriver_wait(timout).until(EC.visibility_of_element_located((by, loc)))

    def wait_until_clickable(self, element: WebElement, timout=15.0):
        """等待直到元素可点击"""
        self.webdriver_wait(timout).until(EC.element_to_be_clickable(element))

    def wait_until_clickable_of_located(self, by: By, loc: Text, timout=15.0):
        """等待直到定位元素可点击"""
        self.webdriver_wait(timout).until(EC.element_to_be_clickable((by, loc)))

    def wait_until_visibility_of_all_located(self, by: By, loc: Text, timout=15.0):
        """等待直到所有定位元素可见"""
        self.webdriver_wait(timout).until(EC.visibility_of_all_elements_located((by, loc)))

    def wait_until_visibility_of_any_located(self, by: By, loc: Text, timout=15.0):
        """等待直到任意定位元素可见"""
        self.webdriver_wait(timout).until(EC.visibility_of_any_elements_located((by, loc)))

    def wait_until_presence_of_all_located(self, by: By, loc: Text, timout=15.0):
        """等待直到所有定位元素出现"""
        self.webdriver_wait(timout).until(EC.presence_of_all_elements_located((by, loc)))

    def wait_until_alert_is_present(self, timout=15.0):
        """等待直到alert出现"""
        self.webdriver_wait(timout).until(EC.alert_is_present())

    def wait_until_attr_include(self, element: WebElement, attr: Text, timout=15.0):
        """等待直到元素包含指定属性"""

        def _predicate():
            try:
                element_attribute = element.get_attribute(attr)
                return element_attribute is not None
            except InvalidSelectorException as e:
                raise e
            except StaleElementReferenceException:
                return False

        self.webdriver_wait(timout).until(_predicate())

    def wait_until_attr_include_of_located(self, by: By, loc: Text, attr: Text, timout=15.0):
        """等待直到定位元素包含指定属性"""
        self.webdriver_wait(timout).until(EC.element_attribute_to_include((by, loc), attr))

    def wait_until_text_in_element(self, element: WebElement, text_: Text, timout=15.0):
        """等待直到指定文本存在元素text中"""

        def _predicate():
            try:
                element_text = element.text
                return text_ in element_text
            except InvalidSelectorException as e:
                raise e
            except StaleElementReferenceException:
                return False

        self.webdriver_wait(timout).until(_predicate())

    def wait_until_text_in_element_of_located(self, by: By, loc: Text, text_: Text, timout=15.0):
        """等待直到指定文本存在定位元素text中"""
        self.webdriver_wait(timout).until(EC.text_to_be_present_in_element((by, loc), text_))

    def wait_until_text_in_element_attr(self, element: WebElement, attr: Text, text_: Text, timout=15.0):
        """等待直到指定文本存在元素属性中"""

        def _predicate():
            try:
                element_text = element.get_attribute(attr)
                return text_ in element_text
            except InvalidSelectorException as e:
                raise e
            except StaleElementReferenceException:
                return False

        self.webdriver_wait(timout).until(_predicate())

    def wait_until_text_in_element_attr_of_located(self, by: By, loc: Text, attr: Text, text_: Text, timout=15.0):
        """等待直到指定文本存在定位元素属性中"""
        self.webdriver_wait(timout).until(EC.text_to_be_present_in_element_attribute((by, loc), attr, text_))

    def wait_until_text_in_element_value(self, element: WebElement, text_: Text, timout=15.0):
        """等待直到指定文本存在定位元素value中"""

        def _predicate():
            try:
                element_text = element.get_attribute("value")
                return text_ in element_text
            except InvalidSelectorException as e:
                raise e
            except StaleElementReferenceException:
                return False

        self.webdriver_wait(timout).until(_predicate())

    def wait_until_text_in_element_value_of_located(self, by: By, loc: Text, text_: Text, timout=15.0):
        """等待直到指定文本存在定位元素value中"""
        self.webdriver_wait(timout).until(EC.text_to_be_present_in_element_value((by, loc), text_))

    def send_keys(self, element_name: Text, value):
        """输入"""
        self.__getattribute__(element_name).send_keys(value)

    def click(self, element_name: Text):
        """点击"""
        self.__getattribute__(element_name).click()

    def open(self, url: Text):
        """跳转至给定的 url"""
        base_url = get_config('melon.selenium.url')

        if url.startswith('http://') or url.startswith('https://'):
            self.__step(f'跳转到 {url}', self.driver.get, url)
            return
        if not url.startswith('/'):
            url = '/' + url
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        url = f'{base_url}{url}'
        self.__step(f'跳转到 {url}', self.driver.get, url)

    def screenshot(self) -> Text:
        """截图保存到文件"""
        screenshot_dir = os.path.abspath(get_config('melon.selenium.screenshot_dir', '.'))
        screenshot_dir = os.path.join(screenshot_dir, time.strftime("%Y-%m-%d"))

        if not os.path.exists(screenshot_dir):
            os.mkdir(screenshot_dir)

        file_name = f'{uuid.uuid4()}.png'
        file_name = os.path.join(screenshot_dir, file_name)
        png = self.driver.get_screenshot_as_png()
        with open(file_name, 'wb') as f:
            f.write(png)
        return png

    def close(self):
        """关闭浏览器"""
        self.__step('关闭浏览器', self.driver.close)

    def __step(self, description: Text, func, *args, **kwargs):
        """allure 报告步骤"""
        with allure.step(f'{self.__class__.__name__} => {description}'):
            return func(*args, **kwargs)

    def __getattribute__(self, attr):
        """属性代理"""
        # e_ 或 _e_ 开头属性需代理
        if attr.startswith('e_') or attr.startswith('_e_'):
            # 获取目标属性(被代理属性)
            _target = self.element_dict.get(attr)
            if not _target:
                return object.__getattribute__(self, attr)

            if isinstance(_target, List) and isinstance(_target[0], MelonElement):
                # 可迭代属性
                _proxy = self.__proxy_iterable(_target)
            elif isinstance(_target, MelonElement):
                # 单属性
                _proxy = self.__proxy_single(_target)
            else:
                logger.error(f'not supported element [{attr}]')
                sys.exit(0)

            return _proxy

        return object.__getattribute__(self, attr)

    def __proxy_single(self, _target: MelonElement) -> WebElement:
        """
        代理单属性
        """
        timeout = _target.timeout
        if timeout:
            _proxy = self.__handle_exceptions(self.find_element_await, _target.label, locator=_target.locator, timeout=timeout)
        else:
            _proxy = self.__handle_exceptions(self.find_element, _target.label, locator=_target.locator)
        _proxy._label = _target.label
        return _proxy

    def __proxy_iterable(self, _targets: List[MelonElement]) -> List[WebElement]:
        """
        代理可迭代属性
        """
        _target = _targets[0]
        timeout = _target.timeout
        if timeout:
            _proxy = self.__handle_exceptions(self.find_elements_await, _target.label, locator=_target.locator, timeout=timeout)
        else:
            _proxy = self.__handle_exceptions(self.find_elements, _target.label, locator=_target.locator)
        [setattr(e, '_label', _target.label) for e in _proxy if e]
        return _proxy

    def __proxy_allure(self, *args: WebElement) -> Tuple[WebElement]:
        """代理元素生产步骤报告"""
        if not args or len(args) < 1:
            return tuple()

        for target in args:
            if not target:
                continue
            # 代理方法
            raw_click = target.click
            raw_send_keys = target.send_keys

            def _click():
                with allure.step(f'点击{getattr(target, self.label_field)}'):
                    raw_click()

            def _send_keys(*values):
                with allure.step(f'输入{getattr(target, self.label_field)}: {" ".join(values)}'):
                    raw_send_keys(*values)

            target.click = _click
            target.send_keys = _send_keys
        return args

    def __handle_exceptions(self, func: Callable, desc: Text, *args, **kwargs):
        """异常处理"""
        result = None
        try:
            result = func(*args, **kwargs)
        except NoSuchElementException as e:
            png = self.screenshot()
            allure.attach(png, f'{desc}未找到', allure.attachment_type.PNG)
            raise e
        except WebDriverException as e:
            png = self.screenshot()
            allure.attach(png, desc, allure.attachment_type.PNG)
            raise e
        except Exception as e:
            png = self.screenshot()
            allure.attach(png, desc, allure.attachment_type.PNG)
            logger.error(e)
        return result

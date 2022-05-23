import re
import sys
import time
import jmespath
from qrunner.utils.decorate import step
from qrunner.core.api.request import HttpRequest, ResponseResult
from qrunner.core.android.driver import AndroidDriver
from qrunner.core.android.element import AndroidElement
from qrunner.core.ios.driver import IosDriver
from qrunner.core.ios.element import IosElement
from qrunner.core.web.driver import WebDriver
from qrunner.core.web.element import WebElement
from qrunner.utils.log import logger
from qrunner.utils.config import conf


class TestCase(HttpRequest):
    """
    测试用例基类，所有测试用例需要继承该类
    """

    # ---------------------初始化-------------------------------
    def start_class(self):
        """
        Hook method for setup_class fixture
        :return:
        """
        pass

    def end_class(self):
        """
        Hook method for teardown_class fixture
        :return:
        """
        pass

    @classmethod
    def setup_class(cls):
        # 从配置文件中获取浏览器相关配置（为了支持并发执行）
        platform = conf.get_item('common', 'platform')
        serial_no = conf.get_item('app', 'serial_no')
        pkg_name = conf.get_item('app', 'pkg_name')
        browser_name = conf.get_item('web', 'browser_name')

        # 初始化driver
        cls.driver = None
        if platform == 'android':
            logger.info('初始化 安卓 driver')
            if serial_no:
                cls.driver = AndroidDriver(serial_no, pkg_name)
            else:
                logger.info('serial_no为空')
                sys.exit()
        elif platform == 'ios':
            logger.info('初始化 IOS driver')
            if serial_no:
                cls.driver = IosDriver(serial_no, pkg_name)
            else:
                logger.info('serial_no为空')
                sys.exit()
        elif platform == 'web':
            logger.info('初始化 Selenium driver')
            cls.driver = WebDriver(browser_name)
        elif platform == 'api':
            pass
        else:
            logger.info(f'不支持的平台: {platform}')
            sys.exit()
        cls().start_class()

    @classmethod
    def teardown_class(cls):
        # 关闭浏览器
        if isinstance(cls().driver, WebDriver):
            cls().driver.quit()
        cls().end_class()

    def start(self):
        """
        Hook method for setup_method fixture
        :return:
        """
        self.start_time = time.time()
        logger.debug(f"[start_time]: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    def end(self):
        """
        Hook method for teardown_method fixture
        :return:
        """
        logger.debug(f"[end_time]: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        take_time = time.time() - self.start_time
        logger.debug("[run_time]: {:.2f} s".format(take_time))
        if isinstance(self.driver, AndroidDriver) or isinstance(self.driver, IosDriver) or isinstance(self.driver, WebDriver):
            logger.debug("[截图]: 用例执行结束")
            self.driver.screenshot('[用例执行结束]')

    def setup_method(self):
        # 启动应用
        if isinstance(self.driver, AndroidDriver) or isinstance(self.driver, IosDriver):
            self.driver.force_start_app()
        self.start()

    def teardown_method(self):
        self.end()
        # 退出应用
        if isinstance(self.driver, AndroidDriver) or isinstance(self.driver, IosDriver):
            self.driver.stop_app()

    @staticmethod
    def sleep(n: int):
        logger.debug(f'等待: {n}s')
        time.sleep(n)

    # --------------------------------ui自动化相关封装------------------------------------

    def element(self, **kwargs):
        """
        定位元素
        :param kwargs: 元素定位方式
        :return: 根据平台返回对应的元素
        """
        if isinstance(self.driver, AndroidDriver):
            element = AndroidElement(self.driver, **kwargs)
        elif isinstance(self.driver, IosDriver):
            element = IosElement(self.driver, **kwargs)
        elif isinstance(self.driver, WebDriver):
            element = WebElement(self.driver, **kwargs)
        else:
            platform = conf.get('common', 'platform')
            logger.info(f'不支持的平台: {platform}，暂时只支持android、ios、web')
            sys.exit()
        return element

    def screenshot(self, desc, element):
        """截图并标记元素位置"""
        platform = conf.get_item('common', 'platform')
        if platform == 'web':
            self.driver.execute_js("arguments[0].style.border='3px solid red'", element.get_element())
            self.driver.screenshot(desc)
        else:
            self.driver.screenshot(desc, rect=element.rect)

    def click(self, **kwargs):
        """点击"""
        desc = kwargs.get('desc', '')
        step_desc = f'[点击 {desc}]'
        with step(step_desc):
            try:
                element = self.element(**kwargs)
                element.click()
            except Exception as e:
                raise AssertionError(str(e))
            else:
                self.screenshot(step_desc, element)

    def click_exists(self, **kwargs):
        """存在才点击"""
        desc = kwargs.get('desc', '')
        step_desc = f'[存在才点击 {desc}]'
        with step(step_desc):
            try:
                element = self.element(**kwargs)
                element.click_exists()
            except Exception as e:
                raise AssertionError(str(e))
            else:
                self.screenshot(step_desc, element)

    def set_text(self, text, **kwargs):
        """输入"""
        desc = kwargs.get('desc', '')
        step_desc = f'[点击 {desc} 后输入 {text}]'
        with step(step_desc):
            try:
                element = self.element(**kwargs)
                element.set_text(text)
            except Exception as e:
                raise AssertionError(str(e))
            else:
                self.screenshot(step_desc, element)

    def set_password(self, text, **kwargs):
        """输入密码，仅安卓使用"""
        desc = kwargs.get('desc', '')
        step_desc = f'[点击 {desc} 后输入 {text}]'
        with step(step_desc):
            try:
                if isinstance(self.driver, AndroidDriver):
                    element = self.element(**kwargs)
                    element.click()
                    self.driver.set_password(text)
                else:
                    platform = conf.get('common', 'platform')
                    logger.debug(f'仅支持安卓平台，当前平台为: {platform}')
            except Exception as e:
                raise AssertionError(str(e))
            else:
                self.screenshot(step_desc, element)

    def clear_text(self, **kwargs):
        """清除输入框"""
        desc = kwargs.get('desc', '')
        step_desc = f'[点击 {desc} 后清除文本]'
        with step(step_desc):
            try:
                element = self.element(**kwargs)
                element.clear_text()
            except Exception as e:
                raise AssertionError(str(e))
            else:
                self.screenshot(step_desc, element)

    def get_text(self, **kwargs):
        """获取文本属性"""
        desc = kwargs.get('desc', '')
        step_desc = f'[获取 {desc} 的文本]'
        with step(step_desc):
            try:
                element = self.element(**kwargs)
                return element.text
            except Exception as e:
                raise AssertionError(str(e))

    def assertText(self, expect_value=None, timeout=5, desc=''):
        """断言页面包含文本"""
        step_desc = f'断言页面 {desc} 包含文本 {expect_value}'
        with step(step_desc):
            try:
                if expect_value is None:
                    raise AssertionError('预期结果不能为空')
                for _ in range(timeout + 1):
                    try:
                        page_source = self.driver.page_content
                        assert expect_value in page_source, f'页面内容不包含 {expect_value}'
                        break
                    except AssertionError:
                        time.sleep(1)
                else:
                    page_source = self.driver.page_content
                    assert expect_value in page_source, f'页面内容不包含 {expect_value}'
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def assertNotText(self, expect_value=None, timeout=5, desc=''):
        """断言页面不包含文本"""
        step_desc = f'断言页面 {desc} 不包含文本 {expect_value}'
        with step(step_desc):
            try:
                if expect_value is None:
                    raise AssertionError('预期结果不能为空')
                for _ in range(timeout + 1):
                    try:
                        page_source = self.driver.page_content
                        assert expect_value not in page_source, f'页面内容不包含 {expect_value}'
                        break
                    except AssertionError:
                        time.sleep(1)
                else:
                    page_source = self.driver.page_content
                    assert expect_value not in page_source, f'页面内容不包含 {expect_value}'
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def assertElement(self, timeout=5, **kwargs):
        """断言元素存在"""
        desc = kwargs.get('desc', '')
        step_desc = f'[断言控件 {desc} 存在]'
        with step(step_desc):
            try:
                for _ in range(timeout + 1):
                    try:
                        element = self.element(**kwargs)
                        assert element.exists(), f'元素 {kwargs} 不存在'
                        break
                    except AssertionError:
                        time.sleep(1)
                else:
                    assert self.element(**kwargs).exists(), f'元素 {kwargs} 不存在'
            except Exception as e:
                raise AssertionError(str(e))
            else:
                self.screenshot(step_desc, element)

    def assertNotElement(self, timeout=5, **kwargs):
        """断言元素不存在"""
        desc = kwargs.get('desc', '')
        step_desc = f'[断言控件 {desc} 不存在]'
        with step(step_desc):
            try:
                for _ in range(timeout + 1):
                    try:
                        assert not self.element(**kwargs).exists(), f'元素 {kwargs} 仍然存在'
                        break
                    except AssertionError:
                        time.sleep(1)
                else:
                    assert not self.element(**kwargs).exists(), f'元素 {kwargs} 仍然存在'
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    # -------------------仅web使用-----------------------
    def open_url(self, url='', login=True, desc='页面描述'):
        """打开页面"""
        step_desc = f'[打开 {desc}]'
        with step(step_desc):
            try:
                self.driver.open_url(url, login=login)
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def click_by_js(self, **kwargs):
        """通过js的方式点击"""
        desc = kwargs.get('desc', '')
        step_desc = f'[点击 {desc}]'
        with step(step_desc):
            try:
                element = self.element(**kwargs)
                self.driver.click(element)
            except Exception as e:
                raise AssertionError(str(e))
            else:
                self.screenshot(step_desc, element)

    def accept_alert(self, desc=''):
        """同意弹窗"""
        step_desc = f'[同意 {desc}]'
        with step(step_desc):
            try:
                self.driver.accept_alert()
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def dismiss_alert(self, desc=''):
        """拒绝弹窗"""
        step_desc = f'[拒绝 {desc}]'
        with step(step_desc):
            try:
                self.driver.dismiss_alert()
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def assertTitle(self, expect_value=None, timeout=5, desc=''):
        """断言页面标题等于"""
        step_desc = f'[断言 {desc} 标题 等于 {expect_value}]'
        with step(step_desc):
            try:
                if expect_value is None:
                    raise AssertionError('预期结果不能为空')
                for _ in range(timeout + 1):
                    try:
                        title = self.driver.get_title()
                        assert expect_value == title, f'页面标题 {title} 不等于 {expect_value}'
                        break
                    except AssertionError:
                        time.sleep(1)
                else:
                    title = self.driver.get_title()
                    assert expect_value == title, f'页面标题 {title} 不等于 {expect_value}'
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def assertInTitle(self, expect_value=None, timeout=5, desc=''):
        """断言页面标题包含"""
        step_desc = f'[断言 {desc} 标题 包含 {expect_value}]'
        with step(step_desc):
            try:
                if expect_value is None:
                    raise AssertionError('预期结果不能为空')
                for _ in range(timeout + 1):
                    try:
                        title = self.driver.get_title()
                        assert expect_value in title, f'页面标题 {title} 不包含 {expect_value}'
                        break
                    except AssertionError:
                        time.sleep(1)
                else:
                    title = self.driver.get_title()
                    assert expect_value in title, f'页面标题 {title} 不包含 {expect_value}'
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def assertUrl(self, expect_value=None, timeout=5, desc=''):
        """断言页面url等于"""
        step_desc = f'[断言 {desc} 的url等于 {expect_value}]'
        with step(step_desc):
            try:
                if expect_value is None:
                    raise AssertionError('预期结果不能为空')
                for _ in range(timeout + 1):
                    try:
                        url = self.driver.get_url()
                        assert expect_value == url, f'页面url {url} 不等于 {expect_value}'
                        break
                    except AssertionError:
                        time.sleep(1)
                else:
                    url = self.driver.get_url()
                    assert expect_value == url, f'页面url {url} 不等于 {expect_value}'
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def assertInUrl(self, expect_value=None, timeout=5, desc=''):
        """断言页面url包含"""
        step_desc = f'[断言 {desc} 的url包含 {expect_value}]'
        with step(step_desc):
            try:
                if expect_value is None:
                    raise AssertionError('预期结果不能为空')
                for _ in range(timeout + 1):
                    try:
                        url = self.driver.get_url()
                        assert expect_value in url, f'页面url {url} 不包含 {expect_value}'
                        break
                    except AssertionError:
                        time.sleep(1)
                else:
                    url = self.driver.get_url()
                    assert expect_value in url, f'页面url {url} 不包含 {expect_value}'
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def assertAlertText(self, expect_value, desc=''):
        """断言弹窗文本"""
        step_desc = f'[断言 {desc} 的文本等于 {expect_value}]'
        with step(step_desc):
            try:
                alert_text = self.driver.get_alert_text()
                assert expect_value == alert_text, f'弹窗文本 {alert_text} 等于 {expect_value}'
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    # ---------------------------------接口自动化相关封装------------------------------------

    @staticmethod
    def assertStatusCode(status_code):
        """
        断言状态码
        """
        assert ResponseResult.status_code == status_code, \
            f'status_code {ResponseResult} != {status_code}'

    @staticmethod
    def assertPath(path, value):
        """
        断言响应json中对应path的值等于value
        doc: https://jmespath.org/
        """
        search_value = jmespath.search(path, ResponseResult.response)
        assert search_value == value, f'{search_value} != {value}'

    @staticmethod
    def assertEq(path, value):
        """
        assertPath换个名字
        doc: https://jmespath.org/
        """
        search_value = jmespath.search(path, ResponseResult.response)
        assert search_value == value, f'{search_value} != {value}'

    @staticmethod
    def assertLenEq(path, value):
        """
        断言列表长度等于多少
        doc: https://jmespath.org/
        """
        search_value = jmespath.search(path, ResponseResult.response)
        assert len(search_value) == value, f"{search_value} 的长度不等于 {value}"

    @staticmethod
    def assertLenGt(path, value):
        """
        断言列表长度大于多少
        doc: https://jmespath.org/
        """
        search_value = jmespath.search(path, ResponseResult.response)
        assert len(search_value) > value, f"{search_value} 的长度不大于 {value}"

    @staticmethod
    def assertLenGtOrEq(path, value):
        """
        断言列表长度大于等于多少
        doc: https://jmespath.org/
        """
        search_value = jmespath.search(path, ResponseResult.response)
        assert len(search_value) >= value, f"{search_value} 的长度不大于 {value}"

    @staticmethod
    def assertLenLt(path, value):
        """
        断言列表长度小于多少
        doc: https://jmespath.org/
        """
        search_value = jmespath.search(path, ResponseResult.response)
        assert len(search_value) < value, f"{search_value} 的长度不大于 {value}"

    @staticmethod
    def assertLenLtOrEq(path, value):
        """
        断言列表长度小于等于多少
        doc: https://jmespath.org/
        """
        search_value = jmespath.search(path, ResponseResult.response)
        assert len(search_value) <= value, f"{search_value} 的长度不大于 {value}"

    @staticmethod
    def assertGt(path, value):
        """
        值大于多少
        doc: https://jmespath.org/
        """
        search_value = jmespath.search(path, ResponseResult.response)
        assert int(search_value) > int(value), f"{search_value} 不大于 {value}"

    @staticmethod
    def assertGtOrEq(path, value):
        """
        值大于等于
        doc: https://jmespath.org/
        """
        search_value = jmespath.search(path, ResponseResult.response)
        if isinstance(search_value, str):
            search_value = int(search_value)
        assert search_value >= value, f"{search_value} 小于 {value}"

    @staticmethod
    def assertLt(path, value):
        """
        值小于多少
        doc: https://jmespath.org/
        """
        search_value = jmespath.search(path, ResponseResult.response)
        assert int(search_value) < int(value), f"{search_value} 不大于 {value}"

    @staticmethod
    def assertLtOrEq(path, value):
        """
        值小于等于多少
        doc: https://jmespath.org/
        """
        search_value = jmespath.search(path, ResponseResult.response)
        assert int(search_value) <= int(value), f"{search_value} 不大于 {value}"

    @staticmethod
    def assertNotEq(path, value):
        """
        值不等于
        doc: https://jmespath.org/
        """
        search_value = jmespath.search(path, ResponseResult.response)
        assert search_value != value, f"{search_value} 等于 {value}"

    @staticmethod
    def assertIn(path, value_list: list):
        """
        断言匹配结果被value_list包含
        doc: https://jmespath.org/
        """
        search_value = jmespath.search(path, ResponseResult.response)
        assert search_value in value_list, f"{value_list} 不包含 {search_value}"

    @staticmethod
    def assertNotExists(path):
        """断言字段不存在"""
        search_value = jmespath.search(path, ResponseResult.response)
        assert search_value is None, f'仍然包含 {path} 为 {search_value}'

    @staticmethod
    def assertContains(path, value):
        """
        断言匹配结果包含value
        doc: https://jmespath.org/
        """
        search_value = jmespath.search(path, ResponseResult.response)
        assert value in search_value, f"{search_value} 不包含 {value}"

    @staticmethod
    def assertTypeMatch(path, value_type):
        """
        类型匹配
        doc: https://jmespath.org/
        """
        if not isinstance(value_type, type):
            if value_type == 'int':
                value_type = int
            elif value_type == 'str':
                value_type = str
            elif value_type == 'list':
                value_type = list
            elif value_type == 'dict':
                value_type = dict
            else:
                value_type = str

        search_value = jmespath.search(path, ResponseResult.response)
        assert isinstance(search_value, value_type), f'{search_value} 不是 {value_type} 类型'

    @staticmethod
    def assertStartsWith(path, value):
        """
        以什么开头
        doc: https://jmespath.org/
        """
        search_value: str = jmespath.search(path, ResponseResult.response)
        assert search_value.startswith(value), f'{search_value} 不以 {value} 开头'

    @staticmethod
    def assertEndsWith(path, value):
        """
        以什么结尾
        doc: https://jmespath.org/
        """
        search_value: str = jmespath.search(path, ResponseResult.response)
        assert search_value.endswith(value), f'{search_value} 不以 {value} 结尾'

    @staticmethod
    def assertRegexMatch(path, value):
        """
        正则匹配
        doc: https://jmespath.org/
        """
        search_value = jmespath.search(path, ResponseResult.response)
        match_obj = re.match(r'' + value, search_value, flags=re.I)
        assert match_obj is not None, f'结果 {search_value} 匹配失败'


class Page:
    """
    测试页面基类，所有页面需要继承该类
    """
    def __init__(self, driver):
        """
        :param driver: 驱动句柄
        """
        self.driver = driver

    def element(self, **kwargs):
        """
        定位元素
        :param kwargs: 元素定位方式
        :return: 根据平台返回对应的元素
        """
        if isinstance(self.driver, AndroidDriver):
            element = AndroidElement(self.driver, **kwargs)
        elif isinstance(self.driver, IosDriver):
            element = IosElement(self.driver, **kwargs)
        elif isinstance(self.driver, WebDriver):
            element = WebElement(self.driver, **kwargs)
        else:
            platform = conf.get('common', 'platform')
            logger.info(f'不支持的平台: {platform}，暂时只支持android、ios、web')
            sys.exit()
        return element

    def screenshot(self, desc, element):
        """截图并标记元素位置"""
        platform = conf.get_item('common', 'platform')
        if platform == 'web':
            self.driver.execute_js("arguments[0].style.border='3px solid red'", element.get_element())
            self.driver.screenshot(desc)
        else:
            self.driver.screenshot(desc, rect=element.rect)

    def click(self, element):
        """点击"""
        step_desc = f'[点击 {element.desc}]'
        with step(step_desc):
            try:
                element.click()
            except Exception as e:
                raise AssertionError(str(e))
            else:
                self.screenshot(step_desc, element)

    def click_exists(self, element):
        """存在才点击"""
        step_desc = f'[存在才点击 {element.desc}]'
        with step(step_desc):
            try:
                element.click_exists()
            except Exception as e:
                raise AssertionError(str(e))
            else:
                self.screenshot(step_desc, element)

    def set_text(self, element, text):
        """输入"""
        step_desc = f'[点击 {element.desc} 后输入 {text}]'
        with step(step_desc):
            try:
                element.set_text(text)
            except Exception as e:
                raise AssertionError(str(e))
            else:
                self.screenshot(step_desc, element)

    def set_password(self, element, text):
        """输入密码，仅安卓使用"""
        step_desc = f'[点击 {element.desc} 后输入 {text}]'
        with step(step_desc):
            try:
                if isinstance(self.driver, AndroidDriver):
                    element.click()
                    self.driver.set_password(text)
                else:
                    platform = conf.get('common', 'platform')
                    logger.debug(f'仅支持安卓平台，当前平台为: {platform}')
            except Exception as e:
                raise AssertionError(str(e))
            else:
                self.screenshot(step_desc, element)

    def clear_text(self, element):
        """清除输入框"""
        step_desc = f'[点击 {element.desc} 后清除文本]'
        with step(step_desc):
            try:
                element.clear_text()
            except Exception as e:
                raise AssertionError(str(e))
            else:
                self.screenshot(step_desc, element)

    @staticmethod
    def get_text(element):
        """获取文本属性"""
        step_desc = f'[获取 {element.desc} 的文本]'
        with step(step_desc):
            try:
                return element.text
            except Exception as e:
                raise AssertionError(str(e))

    def assertText(self, expect_value=None, timeout=5, desc=''):
        """断言页面包含文本"""
        step_desc = f'断言页面 {desc} 包含文本 {expect_value}'
        with step(step_desc):
            try:
                if expect_value is None:
                    raise AssertionError('预期结果不能为空')
                for _ in range(timeout + 1):
                    try:
                        page_source = self.driver.page_content
                        assert expect_value in page_source, f'页面内容不包含 {expect_value}'
                        break
                    except AssertionError:
                        time.sleep(1)
                else:
                    page_source = self.driver.page_content
                    assert expect_value in page_source, f'页面内容不包含 {expect_value}'
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def assertNotText(self, expect_value=None, timeout=5, desc=''):
        """断言页面不包含文本"""
        step_desc = f'断言页面 {desc} 不包含文本 {expect_value}'
        with step(step_desc):
            try:
                if expect_value is None:
                    raise AssertionError('预期结果不能为空')
                for _ in range(timeout + 1):
                    try:
                        page_source = self.driver.page_content
                        assert expect_value not in page_source, f'页面内容不包含 {expect_value}'
                        break
                    except AssertionError:
                        time.sleep(1)
                else:
                    page_source = self.driver.page_content
                    assert expect_value not in page_source, f'页面内容不包含 {expect_value}'
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def assertElement(self, element, timeout=5):
        """断言元素存在"""
        step_desc = f'[断言控件 {element.desc} 存在]'
        with step(step_desc):
            try:
                for _ in range(timeout + 1):
                    try:
                        assert element.exists(), f'元素 {element.desc} 不存在'
                        break
                    except AssertionError:
                        time.sleep(1)
                else:
                    assert element.exists(), f'元素 {element.desc} 不存在'
            except Exception as e:
                raise AssertionError(str(e))
            else:
                self.screenshot(step_desc, element)

    def assertNotElement(self, element, timeout=5):
        """断言元素不存在"""
        step_desc = f'[断言控件 {element.desc} 不存在]'
        with step(step_desc):
            try:
                for _ in range(timeout + 1):
                    try:
                        assert not element.exists(), f'元素 {element.desc} 仍然存在'
                        break
                    except AssertionError:
                        time.sleep(1)
                else:
                    assert not element.exists(), f'元素 {element.desc} 仍然存在'
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    # -------------------仅web使用-----------------------
    def open_url(self, url='', login=True, desc='页面描述'):
        """打开页面"""
        step_desc = f'[打开 {desc}]'
        with step(step_desc):
            try:
                self.driver.open_url(url, login=login)
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def click_by_js(self, element):
        """通过js的方式点击"""
        step_desc = f'[点击 {element.desc}]'
        with step(step_desc):
            try:
                self.driver.click(element)
            except Exception as e:
                raise AssertionError(str(e))
            else:
                self.screenshot(step_desc, element)

    def accept_alert(self, desc=''):
        """同意弹窗"""
        step_desc = f'[同意 {desc}]'
        with step(step_desc):
            try:
                self.driver.accept_alert()
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def dismiss_alert(self, desc=''):
        """拒绝弹窗"""
        step_desc = f'[拒绝 {desc}]'
        with step(step_desc):
            try:
                self.driver.dismiss_alert()
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def assertTitle(self, expect_value=None, timeout=5, desc=''):
        """断言页面标题等于"""
        step_desc = f'[断言 {desc} 标题 等于 {expect_value}]'
        with step(step_desc):
            try:
                if expect_value is None:
                    raise AssertionError('预期结果不能为空')
                for _ in range(timeout + 1):
                    try:
                        title = self.driver.get_title()
                        assert expect_value == title, f'页面标题 {title} 不等于 {expect_value}'
                        break
                    except AssertionError:
                        time.sleep(1)
                else:
                    title = self.driver.get_title()
                    assert expect_value == title, f'页面标题 {title} 不等于 {expect_value}'
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def assertInTitle(self, expect_value=None, timeout=5, desc=''):
        """断言页面标题包含"""
        step_desc = f'[断言 {desc} 标题 包含 {expect_value}]'
        with step(step_desc):
            try:
                if expect_value is None:
                    raise AssertionError('预期结果不能为空')
                for _ in range(timeout + 1):
                    try:
                        title = self.driver.get_title()
                        assert expect_value in title, f'页面标题 {title} 不包含 {expect_value}'
                        break
                    except AssertionError:
                        time.sleep(1)
                else:
                    title = self.driver.get_title()
                    assert expect_value in title, f'页面标题 {title} 不包含 {expect_value}'
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def assertUrl(self, expect_value=None, timeout=5, desc=''):
        """断言页面url等于"""
        step_desc = f'[断言 {desc} 的url等于 {expect_value}]'
        with step(step_desc):
            try:
                if expect_value is None:
                    raise AssertionError('预期结果不能为空')
                for _ in range(timeout + 1):
                    try:
                        url = self.driver.get_url()
                        assert expect_value == url, f'页面url {url} 不等于 {expect_value}'
                        break
                    except AssertionError:
                        time.sleep(1)
                else:
                    url = self.driver.get_url()
                    assert expect_value == url, f'页面url {url} 不等于 {expect_value}'
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def assertInUrl(self, expect_value=None, timeout=5, desc=''):
        """断言页面url包含"""
        step_desc = f'[断言 {desc} 的url包含 {expect_value}]'
        with step(step_desc):
            try:
                if expect_value is None:
                    raise AssertionError('预期结果不能为空')
                for _ in range(timeout + 1):
                    try:
                        url = self.driver.get_url()
                        assert expect_value in url, f'页面url {url} 不包含 {expect_value}'
                        break
                    except AssertionError:
                        time.sleep(1)
                else:
                    url = self.driver.get_url()
                    assert expect_value in url, f'页面url {url} 不包含 {expect_value}'
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)

    def assertAlertText(self, expect_value, desc=''):
        """断言弹窗文本"""
        step_desc = f'[断言 {desc} 的文本等于 {expect_value}]'
        with step(step_desc):
            try:
                alert_text = self.driver.get_alert_text()
                assert expect_value == alert_text, f'弹窗文本 {alert_text} 等于 {expect_value}'
            except Exception as e:
                raise AssertionError(str(e))
            finally:
                self.driver.screenshot(step_desc)






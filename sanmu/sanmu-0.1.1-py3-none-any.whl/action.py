import logging
import unittest
from typing import Optional

from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.remote.webdriver import WebElement as RemoteWebElement
from selenium.webdriver.support.wait import WebDriverWait

from sanmu.models import BaseTestCase

logger = logging.getLogger("KeyWord")


class KeyWord:
    _all_keyword = None
    _activate_ele: RemoteWebElement = None
    webdriver: RemoteWebDriver = None

    def __init__(self, webdriver: RemoteWebDriver):
        self.webdriver = webdriver

    def find_element(self, value: str) -> RemoteWebElement:
        return WebDriverWait(self.webdriver, 5).until(
            lambda x: self.webdriver.find_element(By.XPATH, value)
        )

    def key_goto(self, url, *args):
        self.webdriver.get(url)

    def key_touch(self, locator, *args):
        ele = self.find_element(locator)

    def key_click(self, locator, *args):
        ele = self.find_element(locator)

        ele.click()

    def key_input(self, locator, content, *args):
        ele = self.find_element(locator)

        ele.clear()
        ele.send_keys(content)

    def key_verify(self, locator, verify_name, expression, value, *args):
        validator = Validator(self,
                              locator,
                              verify_name,
                              expression,
                              value,
                              args,
                              )
        validator.is_valid()


class Validator:

    def __init__(
            self,
            keyword: KeyWord,
            locator: Optional[str],
            verify_name: str,
            expression: str,
            value: str,
            args: tuple,
    ):
        self.keyword = keyword
        self.locator = locator
        self.verify_name = verify_name
        self.expression = expression
        self.value = value
        self.args = args

    def is_valid(self):

        a = self.get_actual_value()
        b = self.value

        if self.expression in [">", ">=", "<", "<=", "==", "!="]:
            # 常用表达式
            _ = f"a  {self.expression}  b "
            assert eval(_), f"断言失败： {_}"
        else:
            # 特殊表达式
            match self.expression:
                case "contains":
                    assert b in a, f"断言失败:  {a} contains {b}"
                case _:
                    raise ValueError(f"未知的验证表达式：{self.expression}")

    def get_actual_value(self):

        ele = None
        f = getattr(self, f"get_{self.verify_name}", None)
        if not f:
            ele = self.keyword.find_element(self.locator)
            f = getattr(self, f"get_ele_{self.verify_name}")

        return f(ele)

    def get_title(self, _: None):
        return self.keyword.webdriver.title

    def get_url(self, _: None):
        return self.keyword.webdriver.current_url

    def get_alert(self, _: None):
        return Alert(self.keyword.webdriver).text

    @staticmethod
    def get_ele_text(ele: RemoteWebElement):
        return ele.text


class Runner:

    def __init__(self, case: BaseTestCase):
        self.case = case
        self.__name__ = self.case.info.name
        self.__doc__ = ""

    def run(self, test: unittest.TestCase):
        webdriver: RemoteWebDriver = test.driver
        action = KeyWord(webdriver)

        for index, step in enumerate(self.case.steps, start=1):
            step_func = getattr(action, f"key_{step.关键字}")
            print(f"{index}. {step.步骤名} ... ... ", end="")
            try:
                step_func(*step.参数)
                print("OK <br />")
            except Exception as e:
                print("Error <br />")
                raise e

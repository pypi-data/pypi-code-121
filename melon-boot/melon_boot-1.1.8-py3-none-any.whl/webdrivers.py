# -*- encoding: utf-8 -*-
"""
@Author  : zh_o
"""
from selenium import webdriver
from melon.settings import get_config


_DRIVER_ROUTER = dict(
    CHROME=webdriver.Chrome,
    FIREFOX=webdriver.Firefox,
    IE=webdriver.Ie,
    EDGE=webdriver.Edge
)


def create_driver():
    """构建单例 webdriver"""
    url = get_config('melon.selenium.url')
    assert url and url != '', 'URL must not be blank'

    browser_type = get_config('melon.selenium.browser', 'CHROME')
    func = _DRIVER_ROUTER.get(browser_type.upper())
    assert func, f'not supported browser [{browser_type}]'

    _driver = func()

    _driver.get(url)
    _driver.implicitly_wait(get_config('melon.selenium.implicitly_wait', 0))
    if get_config('melon.selenium.maximize_window', False):
        _driver.maximize_window()
    return _driver


driver = create_driver()


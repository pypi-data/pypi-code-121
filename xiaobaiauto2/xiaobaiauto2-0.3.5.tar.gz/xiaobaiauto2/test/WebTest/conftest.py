#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'conftest.py'
__create_time__ = '2020/7/6 14:11'
'''  UI自动化可以使用该文件，其他测试可以移除防止对测试有干扰   '''
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from xiaobaiauto2.data.GLO_VARS import PUBLIC_VARS
from xiaobaiauto2.utils.xiaobaiauto2Installer import chromedriver_download
import pytest

b = None

@pytest.mark.hookwrapper
def pytest_runtest_makereport(item):
    """
    当测试失败的时候，自动截图，展示到html报告中
    :param item:
    """
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])
    if report.when == 'call' or report.when == "setup":
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            file_name = report.nodeid.replace("::", "_")+".png"
            screen_img = _capture_screenshot()
            if file_name:
                html = '<div><img src="data:image/png;base64,%s" alt="screenshot" style="width:600px;height:300px;" ' \
                       'onclick="window.open(this.src)" align="right"/></div>' % screen_img
                extra.append(pytest_html.extras.html(html))
        report.extra = extra

def _capture_screenshot():
    '''
    截图保存为base64，展示到html中
    :return:
    '''
    if b:
        return b.get_screenshot_as_base64()
    else:
        return '未截图'

@pytest.fixture(scope="session", autouse=True)
def browser():
    global b
    if b is None:
        '''
            chrome的一些设置，有助测试，注释的部分自行选择
        '''
        chrome_options = Options()
        # 去除"Chrome正在受到自动化测试软件的控制"弹出框信息
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option('excludeSwitches', ['--enable-automation'])
        # 启动最大化
        chrome_options.add_argument('--start-maximized')
        # 规避不必要的BUG出现
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('-ignore-certificate-errors')
        chrome_options.add_argument('-ignore -ssl-errors')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        prefs = {}
        prefs["credentials_enable_service"] = False
        prefs["profile.password_manager_enabled"] = False
        chrome_options.add_experimental_option("prefs", prefs)
        # 无头（无界面）模式
        # chrome_options.add_argument('--headless')
        # 设置手机浏览器头（模拟手机端web）
        # chrome_options.add_argument('User-Agent=Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BLA-AL00 Build/HUAWEIBLA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/8.9 Mobile Safari/537.36')
        # 禁止图片
        # chrome_options.add_argument('blink-settings=imagesEnabled=false')
        # 指定chrome.exe路径
        # chrome_options.binary_location = '*\\chrome.exe'
        try:
            b = webdriver.Chrome(chrome_options=chrome_options)
        except Exception as e:
            chromedriver_download()
            b = webdriver.Chrome(chrome_options=chrome_options)
        except TimeoutError as e:
            print('自己手动下载吧，https://npm.taobao.org/mirrors/chromedriver/')
    b.implicitly_wait(PUBLIC_VARS['WebDriverWait'])
    yield b
    b.quit()

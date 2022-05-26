# -*- coding:utf-8 -*-
# author:jackwu 
# time:2022/5/18
# des: selenium 工具类

import os
import sys
import datetime
import zipfile
import requests
import time
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_PATH)

from utils.config import PROXY_IP_URL
try:
    from utils.util_normal import get_proxy_ip  # 需替换自己的代理池
except:
    pass
from hgj_download_center.downloader.new_basespider import NewBaseSpider


class SeleniumSpiderBase(NewBaseSpider):
    def __init__(self, task_name, use_redis=True):
        super(SeleniumSpiderBase, self).__init__(task_name=task_name, use_redis=use_redis)
        self.task_name = task_name
        self.use_redis = use_redis
        # 是否使用 无头模式 无痕模式，默认为True
        self.is_headless, self.is_incognito = False, False
        # 是否加载图片
        self.load_picture = True
        self.use_userdata = False
        # 代理
        self.use_proxy = False
        self.ip_prefix = "ippool_"

    def create_browser(self):
        """
        初始化一个chrome
        """
        # desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
        # desired_capabilities["pageLoadStrategy"] = "none"  # 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出

        chrome_options = webdriver.ChromeOptions()

        # 设置中文
        chrome_options.add_argument('lang=zh_CN.UTF-8')

        # root
        chrome_options.add_argument('--no-sandbox')
        # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument('--disable-gpu')
        # 隐藏滚动条, 应对一些特殊页面
        chrome_options.add_argument('--hide-scrollbars')
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument('--disable-dev-shm-usage')
        # 忽略验证：您的连接不是私密连接
        chrome_options.add_argument('--ignore-certificate-errors')

        # 取消chrome受自动控制提示
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        # 扩展程序
        # chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_experimental_option('useAutomationExtension', False)

        if self.load_picture is False:
            # 不加载图片, 提升速度
            chrome_options.add_argument('blink-settings=imagesEnabled=false')

        # 关掉密码弹窗
        prefs = {"": ""}
        prefs["credentials_enable_service"] = False
        prefs["profile.password_manager_enabled"] = False
        chrome_options.add_experimental_option("prefs", prefs)

        if self.use_proxy is True:
            # 无头模式，无痕模式 不支持使用扩展
            self.is_headless = False
            self.is_incognito = False
            self.use_userdata = False
            while True:
                try:
                    proxy_dict = get_proxy_ip()
                    if proxy_dict.get('info', '') == '暂时没有代理ip':
                        self.logger.info('暂时没有代理ip')
                        time.sleep(10)
                        continue
                    else:
                        break
                except:
                    time.sleep(30)

            PLUGIN_PATH = self.__create_proxyauth_extension(proxy_host=proxy_dict['ip'], proxy_port=proxy_dict['port'], proxy_username=proxy_dict['username'], proxy_password=proxy_dict['password'])
            chrome_options.add_extension(PLUGIN_PATH)
            try:
                requests.delete(PROXY_IP_URL + "?ipkey={}".format(self.ip_prefix + proxy_dict['ip']), timeout=10)
            except:
                pass

        if self.use_userdata:
            # chrome_options.add_argument(f"--user-data-dir={os.path.join(PROJECT_PATH, 'userdata')}")
            pass

        if self.is_incognito:
            # 无痕
            chrome_options.add_argument('--incognito')

        if self.is_headless:
            chrome_options.add_argument('--headless')

        # 开启服务，通过服务，控制浏览器关闭
        if sys.platform == 'win32':
            executable_path = os.path.join(PROJECT_PATH, 'util', 'chromedriver')
        else:
            executable_path = '/usr/local/bin/chromedriver'
        try:
            selenium_service = Service(executable_path=executable_path)
            selenium_service.command_line_args()
            selenium_service.start()
            browser = webdriver.Chrome(executable_path=executable_path, options=chrome_options)
            browser.set_page_load_timeout(60)
        except:
            display = Display(visible=False, size=(1792, 1120))
            display.start()
            selenium_service = Service(executable_path=executable_path)
            selenium_service.command_line_args()
            selenium_service.start()
            browser = webdriver.Chrome(executable_path=executable_path, options=chrome_options)
            browser.set_page_load_timeout(60)
        try:
            stealth_path = os.path.join(PROJECT_PATH, 'util', 'stealth.min.js')
            with open(stealth_path) as f:
                js = f.read()
            browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": js
            })
        except:
            pass
        # try:
        #     tk = tkinter.Tk()
        #     width = tk.winfo_screenwidth()
        #     height = tk.winfo_screenheight()
        #     tk.quit()
        # except:
        width = 1792
        height = 1120
        browser.set_window_size(width, height)
        browser.maximize_window()

        browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
        })
        return selenium_service, browser

    def click_and_send_keys(self, browser, by, rule, msg):
        """
        点击并发送
        每次都获取是因为有时旧的元素定位不到会报错，所以每次都重新获取元素并完成相应操作
        :param browser: 浏览器对象
        :param by: 通过什么方式定位，如： id，xpath，css_selector
        :param rule: 定位的规则
        :param msg: 需要输入的值
        :return:
        """
        by = by.lower()
        self.__get_element(browser, by, rule).click()
        time.sleep(1)
        self.__get_element(browser, by, rule).clear()
        self.__get_element(browser, by, rule).click()
        time.sleep(1)
        self.__get_element(browser, by, rule).send_keys(msg)

    def clear_and_send(self, browser, by, rule, msg):
        """
        清空并发送
        每次都获取是因为有时旧的元素定位不到会报错，所以每次都重新获取元素并完成相应操作
        :param browser: 浏览器对象
        :param by: 通过什么方式定位，如： id，xpath，css_selector
        :param rule: 定位的规则
        :param msg: 需要输入的值
        :return:
        """
        by = by.lower()
        self.__get_element(browser, by, rule).clear()
        time.sleep(0.3)
        self.__get_element(browser, by, rule).send_keys(msg)
        time.sleep(0.3)

    @staticmethod
    def close_browser(selenium_service, browser):
        """
        关闭浏览器
        """
        try:
            browser.quit()
            time.sleep(1)
            selenium_service.stop()
            time.sleep(2)
        except:
            pass

    def init_new_browser(self, selenium_service, browser, next_init_time):
        """
        :param selenium_service: 服务
        :param browser: 浏览器
        :param next_init_time: 下次初始化时间
        :return:
        """
        if datetime.datetime.now() >= next_init_time:
            browser.quit()
            time.sleep(1)
            selenium_service.stop()
            time.sleep(2)

            selenium_service, browser = self.create_browser()
            next_init_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        return selenium_service, browser, next_init_time

    def scroll_to_ele(self, browser, by, rule):
        """滚动到某个元素的位置"""
        ele = self.__get_element(browser, by, rule)
        js4 = "arguments[0].scrollIntoView();"
        browser.execute_script(js4, ele)
        return True

    def click_by_js(self, browser, by, rule):
        """通过js点击"""
        by = by.lower()
        ele = self.__get_element(browser, by, rule)
        browser.execute_script("arguments[0].click();", ele)
        time.sleep(0.5)

    def __create_proxyauth_extension(self, proxy_host, proxy_port, proxy_username, proxy_password, scheme='http'):
        """带密码验证的扩展"""
        plugin_path = os.path.join(PROJECT_PATH, "util", "proxy_auth_plugin.zip")

        manifest_json = """
                {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
                """
        background_js = """
            var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "proxy_host",
                port: parseInt(proxy_port)
              },
              bypassList: ["foobar.com"]
            }
          };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "proxy_username",
                    password: "proxy_password"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
        );
            """.replace('proxy_host', proxy_host).replace('proxy_port', str(proxy_port)) \
            .replace('proxy_username', proxy_username).replace('proxy_password', proxy_password)

        with zipfile.ZipFile(plugin_path, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

        return plugin_path

    def __get_element(self, browser, by, value):
        """通过不同的方式查找界面元素"""
        element = None
        by = by.lower()
        if (by == "id"):
            element = browser.find_element_by_id(value)
        elif (by == "name"):
            element = browser.find_element_by_name(value)
        elif (by == "xpath"):
            element = browser.find_element_by_xpath(value)
        elif (by == "classname"):
            element = browser.find_element_by_class_name(value)
        elif (by == "css"):
            element = browser.find_element_by_css_selector(value)
        elif (by == "link_text"):
            element = browser.find_element_by_link_text(value)
        else:
            print("无对应方法，请检查")
        return element

    def send_msg_to_wechat(self, msg: str):
        """目的港预警机器人"""
        bot_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=18688e74-3491-4ed6-8a7f-cc60721376c9'
        json_dict = {
            "msgtype": "text",
            "text": {
                "content": msg
            }
        }
        for i in range(3):
            res = requests.post(bot_url, json=json_dict)
            if res.status_code == 200:
                return True
        return False


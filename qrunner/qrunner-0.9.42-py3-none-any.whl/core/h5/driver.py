import os
import subprocess
import sys
import time
import allure
import requests
from baseImage import Image, Rect
from selenium import webdriver
from qrunner.utils.config import conf
from qrunner.utils.log import logger
from qrunner.utils.webdriver_manager_extend import ChromeDriverManager
from qrunner.core.android.driver import AndroidDriver


# class H5Config:
#     webview_version = '77.0.3865.40'


# # 重启chromedriver的装饰器
# def relaunch(func):
#     def wrapper(self, *args, **kwargs):
#         try:
#             return func(self, *args, **kwargs)
#         except requests.exceptions.ConnectionError as _:
#             logger.warning("h5 driver error, relaunch now.")
#             self.d = H5Driver(conf.get_name('app', 'serial_no'))
#     return wrapper

def get_server_chrome_versions():
    """获取淘宝镜像网站上所有的版本列表"""
    version_list = []
    url = "https://registry.npmmirror.com/-/binary/chromedriver/"
    rep = requests.get(url).json()
    for item in rep:
        version_list.append(item["name"])
    return version_list


def get_webview_version(serial_no, pkg_name):
    """通过shell命令获取webview对应chrome的版本号"""
    # 获取应用的pid
    pid = subprocess.getoutput(f'adb -s {serial_no} shell ps | grep {pkg_name}').split(' ')[6]
    print(pid)

    # 获取webview的socket名称
    socket_name = subprocess.getoutput(f'adb -s {serial_no} shell cat /proc/net/unix | grep --binary-file=text webview').split(' ')[-1][1:]
    print(socket_name)

    # 将webview端口转发到本地
    cmd = f'adb -s {serial_no} forward tcp:5000 localabstract:{socket_name}'
    print(cmd)
    subprocess.getoutput(cmd)

    # 请求本地服务，获取版本号
    version_data = requests.get('http://127.0.0.1:5000/json/version').json()
    print(version_data)
    version = version_data['Browser'].split('/')[1]
    print(version)

    return version


def get_driver_version(serial_no, pkg_name):
    """获取应用对应的淘宝镜像的chromedriver的版本号"""
    webview_version = get_webview_version(serial_no, pkg_name)

    version_list = get_server_chrome_versions()
    if webview_version in version_list:
        return webview_version
    else:
        for version in version_list:
            if version[0:10] == webview_version[0:10]:
                return version.split('/')[0]
        else:
            print('淘宝镜像未找到匹配本机的chromedriver版本')
            sys.exit()


class H5Driver(object):
    # _instance = {}
    #
    # def __new__(cls, serial_no=None):
    #     if not serial_no:
    #         serial_no = conf.get_name('app', 'serial_no')
    #     if serial_no not in cls._instance:
    #         cls._instance[serial_no] = super().__new__(cls)
    #     return cls._instance[serial_no]

    def __init__(self, android_driver: AndroidDriver):
        serial_no = android_driver.serial_no
        pkg_name = android_driver.pkg_name

        # # 判断应用是否已启动
        # pid = android_driver.wait_app_running()
        # if pid:
        #     logger.debug('应用已启动')
        # else:
        #     logger.debug('应用未启动，h5Driver初始化失败')
        #     sys.exit()

        logger.info(f'启动H5Driver for {serial_no}')
        options = webdriver.ChromeOptions()
        options.add_experimental_option('androidDeviceSerial', serial_no)
        options.add_experimental_option('androidPackage', pkg_name)
        options.add_experimental_option('androidUseRunningApp', True)
        options.add_experimental_option('androidProcess', pkg_name)
        for i in range(3):
            try:
                version = get_driver_version(serial_no, pkg_name)
                path_ = ChromeDriverManager(version=version).install()
                self.d = webdriver.Chrome(
                    executable_path=path_,
                    options=options
                )
                logger.debug('h5Driver初始化成功')
                break
            except Exception as e:
                logger.debug(f'发生异常: {str(e)}')
                logger.debug(f'第 {i+1} 次重试')
                time.sleep(3)
        else:
            logger.debug('重试3次失败，h5Driver初始化失败')
            sys.exit()

        # 设置页面加载超时时间
        try:
            timeout = int(conf.get_item('common', 'timeout'))
        except:
            pass
        else:
            self.d.set_page_load_timeout(timeout)

    # @staticmethod
    # def get_instance(cls, serial_no=None):
    #     if serial_no not in cls._instance:
    #         logger.info(f'{serial_no} Create h5 driver singleton')
    #         return H5Driver(serial_no)
    #     return H5Driver._instance[serial_no]

    def open_url(self, url):
        logger.info(f'访问: {url}')
        self.d.get(url)

    def back(self):
        logger.info('返回上一页')
        self.d.back()

    def screenshot(self, file_name, rect=None):
        """
        截图并保存到预定路径并上传到allure报告
        @param file_name: foo.png or fool
        @param rect: 列表
        @return:
        """
        # 把文件名处理成test.png的样式
        if '.' in file_name:
            file_name = file_name.split(r'.')[0]
        # 截图并保存到当前目录的images文件夹中
        img_dir = os.path.join(os.getcwd(), 'images')
        if os.path.exists(img_dir) is False:
            os.mkdir(img_dir)
        time_str = time.strftime('%Y年%m月%d日 %H时%M分%S秒')
        file_path = os.path.join(img_dir,
                                 f'{time_str}-{file_name}.png')
        logger.info(f'截图保存至: {file_path}')
        self.d.save_screenshot(file_path)

        # 标记
        if rect is not None:
            img = Image(file_path)
            img.rectangle(Rect(*rect), color=(0, 0, 255), thickness=3)
            img.imwrite(file_path)

        # 截图并上传到allure报告
        logger.info(f'截图上传至allure报告')
        allure.attach.file(file_path,
                           attachment_type=allure.attachment_type.PNG,
                           name=f'{time_str}-{file_name}.png')

    # @relaunch
    # def upload_pic(self, filename):
    #     # allure.attach.file(self.d.get_screenshot_as_png(),
    #     #                    attachment_type=allure.attachment_type.PNG,
    #     #                    name=f'{filename}')
    #     self.d.save_screenshot('tmp.png')
    #     allure.attach.file('tmp.png', attachment_type=allure.attachment_type.PNG,
    #                        name=f'{filename}-{get_time()}')
    #     os.remove('tmp.png')

    @property
    def page_content(self):
        page_source = self.d.page_source
        logger.info(f'获取页面内容: \n{page_source}')
        return page_source

    def max_window(self):
        logger.info('窗口设置全屏')
        self.d.maximize_window()

    def set_window_size(self, width, height):
        logger.info('设置窗口长宽')
        self.d.set_window_size(width, height)

    def get_windows(self):
        logger.info(f'获取当前打开的窗口列表')
        return self.d.window_handles

    def switch_window(self, old_windows):
        logger.info('切换到最新的window')
        current_windows = self.d.window_handles
        newest_window = [window for window in current_windows if window not in old_windows][0]
        self.d.switch_to.window(newest_window)

    def window_scroll(self, width, height):
        logger.info(f'设置scroll bar的宽高')
        js = "window.scrollTo({w},{h});".format(w=str(width), h=str(height))
        self.d.execute_script(js)

    def switch_to_frame(self, frame_id):
        logger.info(f'切换到frame {frame_id}')
        self.d.switch_to.frame(frame_id)

    def switch_to_frame_out(self):
        logger.info('从frame中切出来')
        self.d.switch_to.default_content()

    def execute_js(self, script, *args):
        logger.info(f'执行js脚本: \n{script}')
        self.d.execute_script(script, *args)

    def click(self, element):
        logger.info(f'点击元素: {element}')
        self.d.execute_script('arguments[0].click();', element)

    def quit(self):
        logger.info('退出浏览器')
        self.d.quit()

    def close(self):
        logger.info('关闭当前页签')
        self.d.close()

    def add_cookies(self, cookies: list):
        for cookie in cookies:
            self.d.add_cookie(cookie)

    def get_cookies(self):
        logger.info('获取cookies')
        cookies = self.d.get_cookies()
        logger.info(cookies)
        return cookies

    def get_cookie(self, name):
        logger.info(f'获取cookie: {name}')
        cookie = self.d.get_cookie(name)
        logger.info(cookie)
        return cookie

    def delete_all_cookies(self):
        logger.info('删除所有cookie')
        self.d.delete_all_cookies()

    def delete_cookie(self, name):
        logger.info(f'删除cookie: {name}')
        self.d.delete_cookie(name)

    def refresh(self):
        logger.info(f'刷新当前页')
        self.d.refresh()

    def get_title(self):
        logger.info('获取页面标题')
        title = self.d.title
        logger.info(title)
        return title

    def get_url(self):
        logger.info('获取页面url')
        url = self.d.current_url
        logger.info(url)
        return url

    def get_alert_text(self):
        logger.info('获取alert的文本')
        alert_text = self.d.switch_to.alert.text
        logger.info(alert_text)
        return alert_text

    def accept_alert(self):
        logger.info('同意确认框')
        self.d.switch_to.alert.accept()

    def dismiss_alert(self):
        logger.info('取消确认框')
        self.d.switch_to.alert.dismiss()






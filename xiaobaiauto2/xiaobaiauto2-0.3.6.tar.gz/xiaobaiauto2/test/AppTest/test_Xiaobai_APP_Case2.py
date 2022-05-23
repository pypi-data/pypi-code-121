#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'test_Manzhai_APP_Case2.py'
__create_time__ = '2020/7/17 2:29'

from appium import webdriver
from xiaobaiauto2.xiaobaiauto2 import app_aciton
from xiaobaiauto2.utils.xiaobaiauto2Email import send_email
from xiaobaiauto2.data.GLO_VARS import PUBLIC_VARS
from xiaobaiauto2.config.config import EMAILCONFIG
from os import path
from time import sleep
import pytest

browser = None

def setup_module():
    global b
    '''
        'platformName': 'Android',
        'platformVersion': '5.1',  
        'deviceName': '',  
        'noReset': True,  
        'allowClearUserData' = 'true',      #用户可自行选择清除数据
        'fullReset' = "false",              #卸载程序，默认为false
        'exported'="true",                  #是否支持其他应用调用当前组件
        'appPackage': '',  
        'appActivity': '',  
        'unicodeKeyboard': True,            #使用unicode编码方式发送字符串  
        'resetKeyboard': True               #将键盘隐藏起来，输入中文就要增加这两个参数
        'udid':'设备UDID'
        'bundleId':'应用包名'
    '''
    android_caps = {
        'platformName': 'Android',
        'platformVersion': '5.1',
        'deviceName': '设备名',
        'noReset': True,
        'allowClearUserData': 'true',
        'fullReset': "false",
        'exported': "true",
        'appPackage': '应用包名',
        'appActivity': '应用Activity名',
        'unicodeKeyboard': True,
        'resetKeyboard': True
    }
    ios_caps = {
        'platformName': 'iOS',
        'platformVersion': '11.4',
        'deviceName': '设备名',
        'udid': '设备UDID',
        'bundleId': '应用包名',
        'noReset': True,
    }
    emil = {
        'sender': 'tser@jicaiyunshang.com',
        'receiver': ['807447312@qq.com', 'qiankuny@163.com', '912194099@qq.com'],
        'smtpserver': 'smtp.ym.163.com',
        'smtp_port': 25,
        'username': 'tser@jicaiyunshang.com',
        'password': '',
        'subject': '吉彩云尚自动化测试报告',
        'report': 'report.html'
    }
    PUBLIC_VARS.update(emil)
    if b is None:
        b = webdriver.Remote('http://127.0.0.1:4723/wd/hub', android_caps)

def teardown_module():
    b.quit()
    sleep(2)
    _emil = EMAILCONFIG()
    _cur_path = path.abspath(path.curdir)
    if 'report' in PUBLIC_VARS.keys() and '' != PUBLIC_VARS['report']:
        if path.isfile(_cur_path + '/' + PUBLIC_VARS['report']):
            send_email(_cur_path + '/' + PUBLIC_VARS['report'])
    elif '' != _emil.report:
        if path.isfile(_cur_path + '/' + _emil.report):
            send_email(_cur_path + '/' + _emil.report)

def test_yewu_a():
    app_aciton(b, cmd='点击', loc='xxx', data='')
    app_aciton(b, cmd='输入', loc='xxx', data='xxx')

def test_yewu_b():
    app_aciton(b, cmd='点击', loc='xxx', data='')
    app_aciton(b, cmd='输入', loc='xxx', data='xxx')
    app_aciton(b, cmd='属性', contains_assert='吉彩')
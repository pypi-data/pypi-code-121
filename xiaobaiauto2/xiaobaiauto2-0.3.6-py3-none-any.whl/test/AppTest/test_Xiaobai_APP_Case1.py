#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'test_Manzhai_APP_Case1.py'
__create_time__ = '2020/7/17 2:29'

from xiaobaiauto2.xiaobaiauto2 import app_aciton
from xiaobaiauto2.utils.xiaobaiauto2Email import send_email
from xiaobaiauto2.data.GLO_VARS import PUBLIC_VARS
from xiaobaiauto2.config.config import EMAILCONFIG
from os import path
from time import sleep
import pytest

@pytest.mark.run(order=2)
def test_yewu_a(mobile):
    app_aciton(mobile, cmd='点击', loc='xxx', data='')
    app_aciton(mobile, cmd='输入', loc='xxx', data='xxx')

@pytest.mark.run(order=3)
def test_yewu_b(mobile):
    app_aciton(mobile, cmd='点击', loc='xxx', data='')
    app_aciton(mobile, cmd='输入', loc='xxx', data='xxx')
    app_aciton(mobile, cmd='属性', contains_assert='吉彩')

@pytest.mark.last
def test_last():
    ''' 本次结束测试结束，发送邮件 '''
    print('测试结束了，发个邮件吧')
    sleep(2)
    _emil = EMAILCONFIG()
    _cur_path = path.abspath(path.curdir)
    if 'report' in PUBLIC_VARS.keys() and '' != PUBLIC_VARS['report']:
        if path.isfile(_cur_path + '/' + PUBLIC_VARS['report']):
            send_email(_cur_path + '/' + PUBLIC_VARS['report'])
    elif '' != _emil.report:
        if path.isfile(_cur_path + '/' + _emil.report):
            send_email(_cur_path + '/' + _emil.report)

@pytest.mark.run(order=1)
def test_first():
    print('测试开始了，准备邮件信息')
    emil = {
        'sender': 'tser@xiaobaiit.com',
        'receiver': ['807447312@qq.com', 'qiankuny@163.com', '912194099@qq.com'],
        'smtpserver': 'smtp.ym.163.com',
        'smtp_port': 25,
        'username': 'tser@xiaobaiit.com',
        'password': '',
        'subject': '小白自动化测试报告',
        'report': 'report.html'
    }
    PUBLIC_VARS.update(emil)
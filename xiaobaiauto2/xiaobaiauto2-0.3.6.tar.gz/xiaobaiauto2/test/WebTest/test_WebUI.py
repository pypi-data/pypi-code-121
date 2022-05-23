#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'test_WebUI.py'
__create_time__ = '2020/7/15 23:34'

from xiaobaiauto2.xiaobaiauto2 import web_action, cmd
from xiaobaiauto2.utils.xiaobaiauto2Email import send_email
from xiaobaiauto2.data.GLO_VARS import PUBLIC_VARS
from xiaobaiauto2.config.config import EMAILCONFIG
from os import path
from time import sleep
import pytest

@pytest.mark.xiaobai_web
def test_Case1(browser):
    web_action(browser, cmd=cmd.打开网页, loc='', data='http://www.baidu.com')
    web_action(browser, cmd=cmd.输入, loc='//*[@id="kw"]', data='小白科技')
    web_action(browser, cmd=cmd.点击, loc='//*[@id="su"]')
    web_action(browser, cmd=cmd.wait, data=3)
    web_action(browser, cmd=cmd.标题, contains_assert='小白')

@pytest.mark.xiaobai_web
def test_Case2(browser):
    web_action(browser, '打开', loc='', data='https://www.baidu.com')
    web_action(browser, '输入', '//*[@id="kw"]', '漫宅')
    web_action(browser, '点击', '//*[@id="su"]')
    web_action(browser, '停止时间', data=3)
    web_action(browser, '标题', contains_assert='漫')
    web_action(browser, '关闭')

@pytest.mark.last
def test_last():
    ''' 本次结束测试结束，发送邮件 '''
    print('测试结束了，发个邮件吧')
    sleep(2)
    _emil = EMAILCONFIG()
    _cur_path = path.abspath(path.curdir)
    PUBLIC_VARS['report'] = 'report.html'  # 命令行您期望的报告文件名
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
        'sender': 'tser@163.com',
        'receiver': ['807447312@qq.com', 'qiankuny@163.com', '912194099@qq.com'],
        'smtpserver': 'smtp.163.com',
        'smtp_port': 25,
        'username': 'tser@xiaobaiit.com',
        'password': '',
        'subject': '小白自动化测试报告',
        'report': 'report.html'
    }
    PUBLIC_VARS.update(emil)

# if __name__ == '__main__':
#     pytest.main(['test_WebUI.py', '--html=report.html', ' -s'])
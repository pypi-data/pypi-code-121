#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'test02.py'
__create_time__ = '2020/7/15 23:34'

import pytest

'''通过order=序号，first与last关键词将脚本进行顺序运行'''

@pytest.mark.run(order=2)
def test_Case1():
    '''操作步骤'''

@pytest.mark.run(order=3)
def test_Case2():
    '''操作步骤'''

@pytest.mark.last
def test_last():
    '''测试结束了，发个邮件吧'''

@pytest.mark.run(order=1)
def test_first():
    '''测试开始了，准备邮件信息'''
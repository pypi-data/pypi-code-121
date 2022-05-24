#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'test_allure_report_demo.py'
__create_time__ = '2020/12/23 21:32'

import pytest
import allure
import os

@pytest.fixture()
def login():
    print("登录")
    yield
    print("登录完成")

@allure.feature('搜索')
def test_search(login):
    ''' 搜索商品 '''
    print("search")

@allure.feature('支付')
def test_pay():
    ''' 余额支付 '''
    print("pay")

if __name__ =="__main__":
    # 执行测试并生成数据为allure生成报告做准备
    pytest.main(['--alluredir', '.'])
    # 生成测试报告
    os.system('allure serve .')
#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'cases.py'
__create_time__ = '2020/11/25 16:01'

from xiaobaiauto2.xiaobaiauto2 import *

'''
    ······业务层接口······
    方法名定义规则：
        接口方式_接口路径(路径中/替换为_)
    例如：
        POST  /api/user/login --> post_api_user_login
        或
        POST  /api/user/login --> post_api_user_login__其它描述信息
    注意：方法参数与方法体不需要写任何内容，可以写描述信息（如下）
'''

@apiTestCase
def post_api_user_login():
    ''' 用户登录接口 '''

@apiTestCase
def post_api_getList():
    ''' 获取列表接口 '''

@apiTestCase
def post_api_getInfo():
    ''' 获取详情接口 '''

@apiTestCase
def post_api_saveOrder():
    ''' 下单接口 '''
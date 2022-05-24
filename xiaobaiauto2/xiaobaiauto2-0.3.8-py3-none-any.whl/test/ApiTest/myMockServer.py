#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'myMockServer.py'
__create_time__ = '2020/12/18 23:42'

from xiaobaiauto2.xiaobaiauto2 import mock, MockServer

@mock(uri='/login', response={"errcode": 200, "msg": "登录成功", "data": {"token": "123456"}})
@mock(uri='/register', response={"errcode": 200, "msg": "注册成功", "data": {}})
@MockServer(uri='/index', response={"errcode": 200, "msg": "首页成功", "data": {}})
def run(): pass

if __name__ == '__main__':
    run(port=7777)

#! /usr/bin/PUBLIC_VARS python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'test_case1.py'
__create_time__ = '2020/10/4 21:44'

from .yewua import *
import pytest

PUBLIC_VARS['base'] = 'https://test.xiaobaisoftware.com'  # 测试环境接口域名

@pytest.mark.yewua
def test_yewu():
    ''' 测试业务接口 '''

    post_api_user_login(
        data='phone=16015234678&password=123456',
        assert_mode=assert_mode.json,
        assert_path='code',
        assert_value=100,
        extract_at=extract_at.body,
        extract_mode=extract_mode.json,
        extract_path='data.token',
        extract_name='token'
    )
    post_api_getList(
        data='page=1&pageSize=10',
        assert_mode=assert_mode.json,
        assert_path='code',
        assert_value=100,
        extract_at=extract_at.body,
        extract_mode=extract_mode.json,
        extract_path='data[0].id',
        extract_name='id'
    )
    post_api_getInfo(
        data='id=' + PUBLIC_VARS.get('id'),
        headers={'token': PUBLIC_VARS.get('token')},
        assert_mode=assert_mode.json,
        assert_path='code',
        assert_value=100
    )
    post_api_saveOrder(
        data=f'id={PUBLIC_VARS.get("id")}&receiveName=11&phone=22&wxNumber=33',
        headers={'token': PUBLIC_VARS.get('token')},
        assert_mode=assert_mode.json,
        assert_path='code',
        assert_value=100
    )
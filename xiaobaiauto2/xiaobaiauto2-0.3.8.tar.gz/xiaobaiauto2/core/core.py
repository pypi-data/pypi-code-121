#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'client.py'
__create_time__ = '2020/9/18 13:50'

from xiaobaiauto2.xiaobaiauto2 import *
from typing import Optional
from requests import request, Response
from jmespath import search
from re import findall
import pysnooper

env: Optional[dict] = {}   # 环境变量

def apiCase(func):
    def inner(**kwargs):
        data = func.__name__.replace('test_', '').replace('_test', '')
        data_list = data.split('_')
        doc = func.__doc__
        global env
        if env.get('base') in ['', None]:
            env['base'] = 'https://www.jicaiyunshang.com/'
        kw = kwargs.copy()
        keyword = ['assert_mode','assert_path','assert_value','extract_at','extract_mode','extract_path','extract_name']
        for k in keyword:
            if k in kw.keys():
                kw.pop(k)
        res = request(method=data_list[0], url=env.get('base') + '/'.join(data_list[1:]), **kw)

        if 'json' == kwargs.get('assert_mode') and\
                'assert_mode' in kwargs.keys() and\
                'application/json' in res.headers.get('content-type'):
            assert kwargs.get('assert_value') == search(kwargs.get('assert_path'), res.json())
        elif 'contains' == kwargs.get('assert_mode') and 'assert_mode' in kwargs.keys():
            assert kwargs.get('assert_value') in res.text
        if 'status' == kwargs.get('extract_at') and 'extract_at' in kwargs.keys():
            env[kwargs.get('extract_name')] = res.status_code
        elif 'headers' == kwargs.get('extract_at') and 'extract_at' in kwargs.keys():
            if 'json' == kwargs.get('extract_mode') and 'extract_mode' in kwargs.keys():
                env[kwargs.get('extract_name')] = search(kwargs.get('extract_path'), res.headers)
            elif 're' == kwargs.get('extract_mode') and 'extract_mode' in kwargs.keys():
                env[kwargs.get('extract_name')] = findall(kwargs.get('extract_path'), res.headers.__str__())
        elif 'body' == kwargs.get('extract_at') and 'extract_at' in kwargs.keys():
            if 'json' == kwargs.get('extract_mode') and\
                    'extract_mode' in kwargs.keys() and \
                    'application/json' in res.headers.get('content-type'):
                env[kwargs.get('extract_name')] = search(kwargs.get('extract_path'), res.json())
            elif 're' == kwargs.get('extract_mode') and 'extract_mode' in kwargs.keys():
                env[kwargs.get('extract_name')] = findall(kwargs.get('extract_path'), res.text)
        elif 'all' == kwargs.get('extract_at') and 'extract_at' in kwargs.keys():
            ''' search in headers and body '''
            env[kwargs.get('extract_name')] = []
            env[kwargs.get('extract_name')].append(search(kwargs.get('extract_path'), res.headers))
            if 'application/json' in res.headers.get('content-type'):
                env[kwargs.get('extract_name')].append(search(kwargs.get('extract_path'), res.json()))
            else:
                env[kwargs.get('extract_name')].append(findall(kwargs.get('extract_path'), res.text))
    return inner

class mode(object):
    ''' 断言格式 '''
    json = 'json'
    re = 're'
    contains = 'contains'

class at(object):
    ''' 提取位置 '''
    status = 'status'
    headers = 'headers'
    body = 'body'
    all = 'all'

class apiTestCase(object):
    res = Response()
    @property
    def res_text(self):
        ''' Text '''
        self.res.encoding = 'utf-8'
        return self.res.text

    @property
    def res_content(self):
        ''' content '''
        return self.res.content

    @property
    def res_json(self):
        ''' json '''
        return self.res.json()

    def assertion(self, at: Optional[str] = 'body',
                  mode: Optional[str] = 'json',
                  path: Optional[str] = '',
                  value=None):
        ''' assert '''

    def paramsHandles(self, params):
        '''
            username={name0}&password={pwd0}
            name0 and pwd0 find by PUBLIC_VARS

        '''

    def __call__(self, func):
        def run(**kwargs):
            '''
            1、参数化
            2、请求
            3、断言、提取
            公共参数 params, data, headers, at, mode, path, value等
            '''
            if kwargs.get('at') == 'body':
                if 'json' in self.res.headers.get('content-type'):
                    content = self.res_json
                else:
                    content = self.res_text
            if 'assert' in func.__name__.lower():
                ''' 执行断言的处理 '''
                data = self.res
            elif 'extract' in func.__name__.lower():
                ''' 执行提取的处理 '''
        return run
#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'xiaobaiauto2.py'
__create_time__ = '2020/7/2 18:20'

from xiaobaiauto2.utils.xiaobaiauto2db import DB
from xiaobaiauto2.data.GLO_VARS import PUBLIC_VARS
from requests import request
from jmespath import search
from re import findall
from typing import Optional
from ddddocr import DdddOcr
from os import path, remove
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from wsgiref.simple_server import make_server

allapi = dict()

def get(key: str = ''):
    if key is not '':
        return PUBLIC_VARS.get(key)

def set(key: str = '', value=None):
    if key is not '':
        PUBLIC_VARS[key] = value

def app(environ, start_response):
    if environ.get('PATH_INFO') in allapi:
        status = '200 OK'
        headers = [('Content-type', 'text/plain; charset=utf-8'),
                   ('project', 'xiaobaiauto2'),
                   ('Server', 'xiaobaikeji')]
        start_response(status, headers)
        return [allapi.get(environ.get('PATH_INFO'))]
    else:
        status = '404 Not Found'
        headers = [('Content-type', 'text/plain; charset=utf-8'),
                   ('project', 'xiaobaiauto2'),
                   ('Server', 'xiaobaikeji')]
        start_response(status, headers)
        return [b'Not Found']

def MockServer(**kwargs):
    '''
    其他参数待扩展
    :param kwargs:
    :return:
    '''
    if 'uri' in kwargs.keys():
        uri = kwargs.get('uri')
    else:
        uri = '/'
    if 'response' in kwargs.keys():
        response = str(kwargs.get('response')).encode('utf-8')
    else:
        response = '{"errcode": 200, "msg": "请求成功", "data": {}}'.encode('utf-8')
    global allapi
    if uri not in allapi.keys():
        allapi[uri] = response
    def xiaobai(func):
        def core(**kwargs):
            if 'host' in kwargs.keys():
                host = kwargs.get('host')
            else:
                host = '0.0.0.0'
            if 'port' in kwargs.keys():
                port = kwargs.get('port')
            else:
                port = 6666
            with make_server(host=host, port=port, app=app) as httpd:
                print(f"xiaobaiMock Serving on port {port}...")
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    print("[Ctrl+C] Shutting down.")
                    httpd.server_close()
        return core
    return xiaobai

mock = MockServer

def verify_check(image_element: WebElement=None, input_element:WebElement =None):
    '''
    验证码识别过程:
    1、通过验证码图片元素进行截图并保存为图片
    2、通过OCR识别并获取结果
    3、将结果填写到验证码输入框
    :param image_element: 验证码图片元素
    :param input_element: 验证码输入框元素
    :return:
    '''
    IMAGE_FILE_NAME = 'verify.png'
    image_element.screenshot(IMAGE_FILE_NAME)
    if path.isfile(IMAGE_FILE_NAME):
        ocr = DdddOcr(old=True)
        with open(IMAGE_FILE_NAME, 'rb') as f:
            image = f.read()
        res = ocr.classification(image)
        if '' != res:
            input_element.send_keys(res)
        else:
            ''' 识别失败 '''
        remove(IMAGE_FILE_NAME)

def cmd2action(b=None, r=None, loc=None, data=None, contains_assert=None, equal_assert=None):
    wait = WebDriverWait(b, PUBLIC_VARS['WebDriverWait'], PUBLIC_VARS['poll_frequency'])
    if r[0][0] == 1:
        if loc not in ('', None):
            if isinstance(b, WebDriver):
                try:
                    e = wait.until(EC.presence_of_element_located((By.XPATH, loc)))
                except TimeoutError as e:
                    try:
                        e = wait.until(lambda b: b.find_element(by=By.XPATH, value=loc))
                    except TimeoutError as e:
                        e = b.find_element(by=By.XPATH, value=loc)
                if '%s' in r[0][2] or '%d' in r[0][2]:
                    eval(r[0][2] % data)
                    if contains_assert:
                        assert contains_assert in eval(r[0][2] % data)
                    elif equal_assert:
                        assert equal_assert == eval(r[0][2] % data)
                else:
                    eval(r[0][2])
                    if contains_assert:
                        assert contains_assert in eval(r[0][2])
                    elif equal_assert:
                        assert equal_assert == eval(r[0][2])
    elif r[0][1] == 1:
        if isinstance(b, WebDriver):
            if '%s' in r[0][2] or '%d' in r[0][2]:
                eval(r[0][2] % data)
                if contains_assert:
                    assert contains_assert in eval(r[0][2] % data)
                elif equal_assert:
                    assert equal_assert == eval(r[0][2] % data)
            else:
                eval(r[0][2])
                if contains_assert:
                    assert contains_assert in eval(r[0][2])
                elif equal_assert:
                    assert equal_assert == eval(r[0][2])
    else:
        if '%s' in r[0][2] or '%d' in r[0][2]:
            eval(r[0][2] % data)
            if contains_assert:
                assert contains_assert in eval(r[0][2] % data)
            elif equal_assert:
                assert equal_assert == eval(r[0][2] % data)
        else:
            eval(r[0][2])
            if contains_assert:
                assert contains_assert in eval(r[0][2])
            elif equal_assert:
                assert equal_assert == eval(r[0][2])

def action(app_type=1, b=None, cmd=None, loc=None, data=None, contains_assert=None, equal_assert=None):
    '''
    操作方法
    :param app_type: 操作对象类型1为web，2为app
    :param b: 操作对象
    :param cmd: 操作命令
    :param loc: 操作路径
    :param data: 操作数据
    :param contains_assert: 包含校验
    :param equal_assert: 相等校验
    :return:
    '''
    if b is not None:
        db = DB()
        r = db.select(f"select is_element,is_driver,code\
                      from keyword\
                      where testtype like '%{app_type}%' and command like '%{cmd}%' or key like '%{cmd}%' limit 1;")
        cmd2action(b, r, loc, data, contains_assert, equal_assert)

def web_action(b=None, cmd=None, loc=None, data=None, contains_assert=None, equal_assert=None):
    action(app_type=1, b=b, cmd=cmd, loc=loc, data=data, contains_assert=contains_assert, equal_assert=equal_assert)

def app_aciton(b=None, cmd=None, loc=None, data=None, contains_assert=None, equal_assert=None):
    action(app_type=2, b=b, cmd=cmd, loc=loc, data=data, contains_assert=contains_assert, equal_assert=equal_assert)

class cmd(object):
    ''' UI动作 '''
    openurl = '打开网页'
    click = '点击'
    sendkey = '输入'
    refresh = '刷新'
    back = '后退'
    close = '关闭'
    quit = '退出'
    tag = '标签'
    attr = '属性'
    curl = 'URL'
    title = '标题'
    frame = '内嵌页'
    window = '标签页[序号(1开始)]'
    alter0 = 'JS_确定'
    alter1 = 'JS_取消'
    alter2 = 'JS_输入框'
    alter3 = 'JS_文本'
    wait = '停止'
    script = '脚本'
    addcookie = '添加cookie'
    swipe = '滑屏'
    dscreenshot = '截屏'
    escreenshot = '元素截图'
    findtext = '识别验证码'
    location = '坐标'
    page_source = '网页源码'
    打开网页 = 'OPENURL'
    点击 = 'CLICK'
    输入 = 'SENDKEY'
    刷新 = 'REFRESH'
    后退 = 'BACK'
    关闭 = 'CLOSE'
    退出 = 'QUIT'
    标签 = 'TAG'
    属性 = 'ATTR'
    URL = 'CURL'
    标题 = 'TITLE'
    内嵌页 = 'FRAME'
    标签页 = 'WINDOW'
    JS_确定 = 'ALERT0'
    JS_取消 = 'ALERT1'
    JS_输入框 = 'ALERT2'
    JS_文本 = 'ALERT3'
    停止 = 'WAIT'
    脚本 = 'SCRIPT'
    添加cookie = 'ADDCOOKIE'
    滑屏 = 'SWIPE'
    截屏 = 'DSCREENSHOT'
    元素截图 = 'ESCREENSHOT'
    识别验证码 = 'FINDTEXT'
    坐标 = 'LOCATION'
    网页源码 = 'page_source'

class assert_mode(object):
    ''' 断言格式 '''
    json = 'json'
    contains = 'contains'

class extract_at(object):
    ''' 提取位置 '''
    status = 'status'
    headers = 'headers'
    body = 'body'
    all = 'all'

class extract_mode(object):
    ''' 提取方式 '''
    json = 'json'
    re = 're'

def _str_format(params):
    '''
    字符串格式化，将参数化数据替换为预设值
    :param params:  待处理对象
    :return:        处理后对象
    '''
    if isinstance(params, dict):
        ''' dict格式 '''
        for k, v in params.items():
            params[k] = _str_format(v)
        return params

    elif isinstance(params, list):
        ''' list格式 '''
        for i, v in enumerate(params):
            params[i] = _str_format(v)
        return params

    elif isinstance(params, tuple):
        ''' tuple格式 '''
        params = list(params)
        for i, v in enumerate(params):
            params[i] = _str_format(v)
        return tuple(params)

    elif isinstance(params, set):
        ''' set格式 '''
        params = list(params)
        for i, v in enumerate(params):
            params[i] = _str_format(v)
        return set(params)

    elif isinstance(params, bytes):
        ''' byte格式 '''
        return bytes(_str_format(str(params, 'utf-8')), 'utf-8')

    elif isinstance(params, str):
        ''' 字符串格式 '''
        keys = findall('{(.+?)}', params)
        if len(keys) != 0:
            for key in keys:
                source = '{' + key + '}'
                target = PUBLIC_VARS.get(key)
                if target:
                    params = params.replace(source, target.__str__())
        return params
    else:
        ''' 其他格式 '''
        return params

def apiTestCase(func):
    '''
    接口描述的装饰器
    :param func:
    :return:
    '''
    def xiaobai(**kwargs):
        kwargs = _str_format(kwargs)
        d = func.__name__.split('_')
        try:
            data_list = d[:d.index('')]
        except ValueError as e:
            data_list = d
        data_list = _str_format(data_list)
        doc = func.__doc__
        if PUBLIC_VARS.get('base') in ['', None]:
            PUBLIC_VARS['base'] = 'https://bbs.jicaiyunshang.com/'
        kw = kwargs.copy()
        keyword = ['assert_mode', 'assert_path', 'assert_value', 'extract_at', 'extract_mode', 'extract_path',
                   'extract_name']
        for k in keyword:
            if k in kw.keys():
                kw.pop(k)
        PUBLIC_VARS['base'] = _str_format(PUBLIC_VARS.get('base'))
        res = request(method=data_list[0], url=PUBLIC_VARS.get('base') + '/'.join(data_list[1:]), **kw)
        res.encoding = 'utf-8'
        if 'json' == kwargs.get('assert_mode') and \
                'assert_mode' in kwargs.keys() and 'application/json' in res.headers.get('Content-Type'):
            assert kwargs.get('assert_value') == search(kwargs.get('assert_path'), res.json())
        elif 'contains' == kwargs.get('assert_mode') and 'assert_mode' in kwargs.keys():
            assert kwargs.get('assert_value') in res.text
        if 'status' == kwargs.get('extract_at') and 'extract_at' in kwargs.keys():
            PUBLIC_VARS[kwargs.get('extract_name')] = res.status_code
        elif 'headers' == kwargs.get('extract_at') and 'extract_at' in kwargs.keys():
            if 'json' == kwargs.get('extract_mode') and 'extract_mode' in kwargs.keys():
                value = search(kwargs.get('extract_path'), res.headers)
                PUBLIC_VARS[kwargs.get('extract_name')] = value if value is not None else ''
            elif 're' == kwargs.get('extract_mode') and 'extract_mode' in kwargs.keys():
                value = findall(kwargs.get('extract_path'), res.headers.__str__())
                PUBLIC_VARS[kwargs.get('extract_name')] = value if value != [] else ['']
        elif 'body' == kwargs.get('extract_at') and 'extract_at' in kwargs.keys():
            if 'json' == kwargs.get('extract_mode') and\
                    'extract_mode' in kwargs.keys() and 'application/json' in res.headers.get('Content-Type'):
                value = search(kwargs.get('extract_path'), res.json())
                PUBLIC_VARS[kwargs.get('extract_name')] = value if value is not None else ''
            elif 're' == kwargs.get('extract_mode') and 'extract_mode' in kwargs.keys():
                value = findall(kwargs.get('extract_path'), res.text)
                PUBLIC_VARS[kwargs.get('extract_name')] = value if value != [] else ['']
        elif 'all' == kwargs.get('extract_at') and 'extract_at' in kwargs.keys():
            ''' search in headers and body '''
            PUBLIC_VARS[kwargs.get('extract_name')] = []
            value = search(kwargs.get('extract_path'), res.headers)
            v = value if value is not None else ''
            PUBLIC_VARS[kwargs.get('extract_name')].append(v)
            if 'application/json' in res.headers.get('Content-Type'):
                value = search(kwargs.get('extract_path'), res.json())
                v = value if value is not None else ''
                PUBLIC_VARS[kwargs.get('extract_name')].append(v)
            else:
                value = search(kwargs.get('extract_path'), res.json())
                v = value if value != [] else ['']
                PUBLIC_VARS[kwargs.get('extract_name')].append(v)
    return xiaobai

def api_action(method: Optional[str] = 'POST', url: Optional[str] = '', **kwargs):
    '''
    接口操作方法
    :param method: 接口请求方式
    :param url: 接口地址
    :param assert_mode: 校验模式[json, contains]
    :param assert_path:  校验预期结果路径
    :param assert_value: 校验预期结果
    :param extract_at:  提取数据所在位置 [status, headers, body, all]
    :param extract_mode: 提取方式 [json, re]
    :param extract_path: 提取路径表达式
    :param extract_name: 提取数据变量名
    :param kwargs: 其他参数参考requests的api
    :return:
    例如：api_action(
            method='POST',
            url='https://bbs.jicaiyunshang.com/login',
            params='',
            data='{"username": "xiaobai", "password": "abcdef"}',
            headers={},
            assert_mode=assert_mode.json,
            assert_path='code',
            assert_value=200,
            extract_at=extract_at.body,
            extract_mode=extract_at.json,
            extract_path='data.accessToken',
            extract_name='accessToken'
        )
    '''
    kwargs = _str_format(kwargs)
    method = _str_format(method)
    url = _str_format(url)
    kw = kwargs.copy()
    keyword = ['assert_mode', 'assert_path', 'assert_value', 'extract_at', 'extract_mode', 'extract_path',
               'extract_name']
    for k in keyword:
        if k in kw.keys():
            kw.pop(k)
    res = request(method=method.upper(), url=url, **kw)
    res.encoding = 'utf-8'
    if 'json' == kwargs.get('assert_mode') and \
            'assert_mode' in kwargs.keys() and 'application/json' in res.headers.get('Content-Type'):
        assert kwargs.get('assert_value') == search(kwargs.get('assert_path'), res.json())
    elif 'contains' == kwargs.get('assert_mode') and 'assert_mode' in kwargs.keys():
        assert kwargs.get('assert_value') in res.text
    if 'status' == kwargs.get('extract_at') and 'extract_at' in kwargs.keys():
        PUBLIC_VARS[kwargs.get('extract_name')] = res.status_code
    elif 'headers' == kwargs.get('extract_at') and 'extract_at' in kwargs.keys():
        if 'json' == kwargs.get('extract_mode') and 'extract_mode' in kwargs.keys():
            value = search(kwargs.get('extract_path'), res.headers)
            PUBLIC_VARS[kwargs.get('extract_name')] = value if value is not None else ''
        elif 're' == kwargs.get('extract_mode') and 'extract_mode' in kwargs.keys():
            value = findall(kwargs.get('extract_path'), res.headers.__str__())
            PUBLIC_VARS[kwargs.get('extract_name')] = value if value != [] else ['']
    elif 'body' == kwargs.get('extract_at') and 'extract_at' in kwargs.keys():
        if 'json' == kwargs.get('extract_mode') and \
                'extract_mode' in kwargs.keys() and 'application/json' in res.headers.get('Content-Type'):
            value = search(kwargs.get('extract_path'), res.json())
            PUBLIC_VARS[kwargs.get('extract_name')] = value if value is not None else ''
        elif 're' == kwargs.get('extract_mode') and 'extract_mode' in kwargs.keys():
            value = findall(kwargs.get('extract_path'), res.text)
            PUBLIC_VARS[kwargs.get('extract_name')] = value if value != [] else ['']
    elif 'all' == kwargs.get('extract_at') and 'extract_at' in kwargs.keys():
        ''' search in headers and body '''
        PUBLIC_VARS[kwargs.get('extract_name')] = []
        value = search(kwargs.get('extract_path'), res.headers)
        v = value if value is not None else ''
        PUBLIC_VARS[kwargs.get('extract_name')].append(v)
        if 'application/json' in res.headers.get('Content-Type'):
            value = search(kwargs.get('extract_path'), res.json())
            v = value if value is not None else ''
            PUBLIC_VARS[kwargs.get('extract_name')].append(v)
        else:
            value = search(kwargs.get('extract_path'), res.json())
            v = value if value != [] else ['']
            PUBLIC_VARS[kwargs.get('extract_name')].append(v)
    return res
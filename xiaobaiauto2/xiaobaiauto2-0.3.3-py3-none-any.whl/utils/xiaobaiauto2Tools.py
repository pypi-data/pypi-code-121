#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'xiaobaiauto2Tools.py'
__create_time__ = '2020/9/23 23:14'

from typing import Optional
import argparse
import os
import zipfile
import sys
import shutil
from xiaobaiauto2.__version__ import __version__
from xiaobaiauto2.utils.jmeter_script_template import create_jmeter
from xiaobaiauto2.utils.xiaobaiauto2Installer import \
    jdk_install, jmeter_install, chromedriver_download, jenkins_war_install, git_windows_install, node_install,\
    allure_install, svn_install, adb_install, fiddler_install, postman_install
from jmespath import search
from urllib.parse import urlparse
from json import loads, JSONDecodeError
import json

step = '\\' if os.name == 'nt' else '/'

def raw_handle(s: Optional[str] = ''):
    '''
    数据分割处理（单个请求放在一起）
    :param s:
    :return:
    '''
    s = s.strip()
    sLines = s.split('\n')
    _start_index = [i for i, _ in enumerate(sLines) if 'HTTP/' in _ or ':authority:' in _]
    _span_data = []
    for i, v in enumerate(_start_index):
        if v != _start_index[-1]:
            _span_data.append(sLines[v:_start_index[i+1]])
        else:
            _span_data.append(sLines[v:])
    # 数据分离(method、url、headers、data)
    result = []
    for request in _span_data:
        if 'HTTP/' in request[0]:
            _method = request[0].split(' ')[0]
            _headers = {}
            _headers_end = 0
            raw_header_data_list = request[1:]
            for _, j in enumerate(raw_header_data_list):
                _headers_end = _
                if '' == j:
                    break
                else:
                    _headers[j.split(': ')[0]] = j.split(': ')[1].strip()
            if raw_header_data_list.__len__() > _headers_end + 1:
                _data = ''.join([i for i in request[_headers_end + 1:] if i != ''])
            else:
                _data = ''
            _url = request[0].split(' ')[1]
            if '://' not in _url and '443' in _headers.get('Host'):
                _url = 'https://' + _headers.get('Host') + _url
            elif '://' not in _url and '443' not in _headers.get('Host'):
                _url = 'http://' + _headers.get('Host') + _url
            result.append(
                {
                    'method': _method,
                    'url': _url,
                    'headers': _headers,
                    'data': _data
                }
            )
        elif ':authority:' in request[0]:
            '''
            :authority: 域名
            :method:    方式
            :path:      地址
            :scheme:    协议
            '''
            _authority = request[0].split(':')[2].strip()
            _method = request[1].split(':')[2].strip()
            _path = request[2].split(':')[2].strip()
            _scheme = request[3].split(':')[2].strip()
            _url = _scheme + '://' + _authority + _path
            _headers = {}
            _headers_end = 0
            raw_header_data_list = request[4:]
            for _, j in enumerate(raw_header_data_list):
                _headers_end = _
                if '' == j:
                    break
                else:
                    _headers[j.split(': ')[0]] = j.split(': ')[1].strip()
            if raw_header_data_list.__len__() > _headers_end + 1:
                _data = ''.join([i for i in request[_headers_end + 1:] if i != ''])
            else:
                _data = ''
            result.append(
                {
                    'method': _method,
                    'url': _url,
                    'headers': _headers,
                    'data': _data
                }
            )
    return result

def har_handle(s: Optional[str] = ''):
    '''
    将har文件字符串，提取接口数据
    :param s:
    :return:
    '''
    result = []
    try:
        d = loads(s)
    except json.decoder.JSONDecodeError as e:
        if s.startswith('\ufeff'):
            s = s.encode('utf8')[3:].decode('utf8')
            d = loads(s)
        else:
            result.append({
                'method': '',
                'url': '',
                'headers': {},
                'data': '',
                'response': None
            })
            return result
    except JSONDecodeError as e:
        d = loads(s.replace("'", '"'))
    except ValueError as e:
        result.append({
            'method': '',
            'url': '',
            'headers': {},
            'data': '',
            'response': None
        })
        return result
    search_request = search('log.entries[].request', d)
    search_response = search('log.entries[].response', d)
    for i, request in enumerate(search_request):
        _method = request.get('method')
        _url = request.get('url')
        _headers = {}
        _data = ''
        if 'content' in search_response[i].keys() and 'mimeType' in search_response[i]['content'].keys() and \
            'text' in search_response[i]['content']:
                _response = search_response[i]['content']['text']
        else:
            _response = None
        for item in request.get('headers'):
            if item.get('name') not in [':method', ':path', ':authority', ':scheme']:
                _headers[item.get('name')] = item.get('value')
        if _method.upper() != 'GET':
            if 'json' in request.get('postData').get('mimeType'):
                if 'text' in request['postData'].keys():  # browser(chrome)
                    _data = request['postData']['text']
                elif 'params' in request['postData'].keys():  # fiddler/charles
                    _data = {}
                    for item in request.get('postData').get('params'):
                        _data[item.get('name')] = item.get('value')
                    _data = _data.__str__().replace("'", '"')
            else:
                if 'text' in request['postData'].keys():  # browser(chrome)
                    _data = request['postData']['text']
                elif 'params' in request['postData'].keys():  # fiddler/charles
                    try:
                        for item in request.get('postData').get('params'):
                            _data += item.get('name') + '=' + item.get('value') + '&'
                        _data = _data[:-1]
                    except TypeError as e:
                        try:
                            _data = request.get('postData').get('params')[0].get('value')
                        except TypeError as e:
                            pass
        result.append(
            {
                'method': _method,
                'url': _url,
                'headers': _headers,
                'data': _data,
                'response': _response
            }
        )
    return result

def convert(data: Optional[list], is_xiaobaiauto2: Optional[int] = 0) -> str:
    '''
    代码转换器
    :param data: {'method':'', 'url': '', 'headers': '', 'data': ''}
    :param is_xiaobaiauto2: 是否转为xiaobaiauto2库
    :param is_har: 是否是har文件
    :return:
    '''
    _code_top = '#! /usr/bin/env python\n'
    _code_pytest_import = \
        'from re import findall\n' \
        'try:\n\timport pytest\n' \
        '\timport requests\n' \
        'except ModuleNotFoundError as e:\n' \
        '\timport os\n' \
        '\tos.system("pip install xiaobaiauto2")\n' \
        '\timport pytest\n' \
        '\timport requests\n\n' \
        'def setup_function():\n' \
        '\t""" 每个接口执行前都会执行的方法，存放公共变量、加密等操作 """\n' \
        '\tpass\n\n' \
        'def teardown_function():\n' \
        '\t""" 每个接口执行后都会执行的方法，存放断言、提取值等操作 """\n' \
        '\tpass\n\n'
    _code_xiaobaiauto2_import = \
        'from os import path\n' \
        'try:\n\timport pytest\n' \
        '\tfrom xiaobaiauto2.xiaobaiauto2 import ' \
        'api_action, assert_mode, extract_at, extract_mode, PUBLIC_VARS, sleep\n' \
        '\tfrom xiaobaiauto2.utils.xiaobaiauto2Email import send_email\n' \
        '\tfrom xiaobaiauto2.data.GLO_VARS import PUBLIC_VARS\n' \
        '\tfrom xiaobaiauto2.config.config import EMAILCONFIG\n' \
        'except ModuleNotFoundError as e:\n' \
        '\timport os\n' \
        '\tos.system("pip install xiaobaiauto2")\n' \
        '\timport pytest\n' \
        '\tfrom xiaobaiauto2.xiaobaiauto2 import ' \
        'api_action, assert_mode, extract_at, extract_mode, PUBLIC_VARS, sleep\n' \
        '\tfrom xiaobaiauto2.utils.xiaobaiauto2Email import send_email\n' \
        '\tfrom xiaobaiauto2.data.GLO_VARS import PUBLIC_VARS\n' \
        '\tfrom xiaobaiauto2.config.config import EMAILCONFIG\n\n'
    _code_requests_import = \
        'from re import findall\n' \
        'try:\n\timport requests\n' \
        'except ModuleNotFoundError as e:\n' \
        '\timport os\n' \
        '\tos.system("pip install xiaobaiauto2")\n' \
        '\timport requests\n\n'
    _code_pytest_end = \
        '# 脚本命令行运行须知： ' \
        '\r# pytest -s -v   运行当前目录所有test_*开头的脚本文件' \
        '\r# pytest -s -v xxx.py 运行指定脚本文件' \
        '\r# pytest -s -v --html=report.html  运行并将结果记录到HTML报告中' \
        '\r# pytest -s -v --html=report.html --self-contained-html 运行并将结果记录到HTML报告中' \
        '\r# pytest其他运行方式参考https://pypi.org/project/xiaobaiauto2或官网说明'
    _code_xiaobaiauto2_end = \
        '@pytest.mark.last\n' \
        'def test_last():\n' \
        '\t#print("测试结束了，发个邮件吧")\n' \
        '\tsleep(2)\n' \
        '\t_emil = EMAILCONFIG()\n' \
        '\t_cur_path = path.abspath(path.curdir)\n' \
        '\tPUBLIC_VARS["report"] = "report.html"  # 命令行您期望的报告文件名\n' \
        '\tif "report" in PUBLIC_VARS.keys() and "" != PUBLIC_VARS["report"]:\n' \
        '\t\tif path.isfile(_cur_path + "/" + PUBLIC_VARS["report"]):\n' \
        '\t\t\tsend_email(_cur_path + "/" + PUBLIC_VARS["report"])\n' \
        '\telif "" != _emil.report:\n' \
        '\t\tif path.isfile(_cur_path + "/" + _emil.report):\n' \
        '\t\t\tsend_email(_cur_path + "/" + _emil.report)\n\n' \
        '@pytest.mark.first\n' \
        'def test_first():\n' \
        '\t# print("测试开始了，准备邮件信息")\n' \
        '\temil = {\n' \
        '\t\t"sender": "807447312@qq.com",\n' \
        '\t\t"receiver": ["807447312@qq.com", "qiankuny@163.com", "912194099@qq.com"],\n' \
        '\t\t"smtpserver": "smtp.163.com",\n' \
        '\t\t"smtp_port": 25,\n' \
        '\t\t"username": "807447312@qq.com",\n' \
        '\t\t"password": "",\n' \
        '\t\t"subject": "小白自动化测试报告",\n' \
        '\t\t"report": "report.html"\n' \
        '\t}\n' \
        '\tPUBLIC_VARS.update(emil)\n\n'
    _code = ''
    for i, v in enumerate(data):
        if is_xiaobaiauto2 == 1:
            _code += f'''@pytest.mark.run(order={i + 2})\
                \rdef test_xiaobai_api_{i + 1}():\
                \r\t# 测试前数据准备 其中下方代码中{{变量名}}是需要在前面的接口返回值提取 \
                \r\theaders = {v.get('headers')}\
                \r\turl = '{v.get('url')}' \
                \r\tdata = '{v.get('data')}'.encode('utf-8')\
                \r\tresponse = requests.request(method='{v.get('method')}', url=url, data=data, headers=headers)\
                \r\t# 测试后时间判断/提取\
                \r\t# assert response.status_code == 200  # 判断HTTP响应状态\
                \r\t# var_name = response.headers()[路径]  # 提取响应头数据\
                \r\t# global var_name # 设置全局变量\
                \r\tif 'json' in response.headers.get('Content-Type'):\
                \r\t\t# assert '预期结果' == response.json()[路径]  # 判断json响应体结果\
                \r\t\t# var_name = response.json()[路径]  # 提取json响应体数据\
                \r\t\t# var_name = response.headers()[路径]  # 提取响应头数据\
                \r\t\tprint(response.json())\
                \r\telse:\
                \r\t\t# assert '预期结果' in response.text # 判断字符串返回值结果 \
                \r\t\t# var_name = findall('正则表达式', response.text)[0] # 正则提取数据\
                \r\t\tprint(response.text)\n\n'''
        elif is_xiaobaiauto2 == 2:
            _code += f'''@pytest.mark.run(order={i + 2})\
                \rdef test_xiaobai_api_{i + 1}():\
                \r\t# 测试前数据准备\
                \r\theaders = {v.get('headers')}\
                \r\turl = '{v.get('url')}' \
                \r\tdata = '{v.get('data')}'.encode('utf-8')\
                \r\tapi_action(\
                \r\t\tmethod='{v.get('method')}',\
                \r\t\turl=url,\
                \r\t\tdata=data,\
                \r\t\theaders=headers,\
                \r\t\tassert_mode=assert_mode.json,\
                \r\t\tassert_path='',\
                \r\t\tassert_value='',\
                \r\t\textract_at=extract_at.body,\
                \r\t\textract_mode=extract_mode.json,\
                \r\t\textract_path='',\
                \r\t\textract_name=''\
                \r\t)\
                \r\t#:param method: 接口请求方式\
                \r\t#:param url: 接口请求地址\
                \r\t#:param data: 接口请求数据\
                \r\t#:param headers: 接口请求头\
                \r\t# 其他可用参数如下：\
                \r\t#:param assert_mode: 校验模式[json, contains]\
                \r\t#:param assert_path:  校验预期结果路径\
                \r\t#:param assert_value: 校验预期结果\
                \r\t#:param extract_at:  提取数据所在位置 [status, headers, body, all]\
                \r\t#:param extract_mode: 提取方式 [json, re]\
                \r\t#:param extract_path: 提取路径表达式\
                \r\t#:param extract_name: 提取数据变量名\
                \r\t#:param kwargs: 其他参数参考requests的api\n\n'''
        else:
            _code += f'''\r# 测试前数据准备 其中下方代码中{{变量名}}是需要在前面的接口返回值提取 \
                \rheaders = {v.get('headers')}\
                \rurl = '{v.get('url')}' \
                \rdata = '{v.get('data')}'.encode('utf-8')\
                \rresponse = requests.request(method='{v.get('method')}', url=url, data=data, headers=headers)\
                \r# 测试后数据判断/提取\
                \r# assert response.status_code == 200  # 判断HTTP响应状态\
                \r# var_name = response.headers()[路径]  # 提取响应头数据\
                \rif 'json' in response.headers.get('Content-Type'):\
                \r\t# assert '预期结果' == response.json()[路径]  # 判断json响应体结果\
                \r\t# var_name = response.json()[路径]  # 提取json响应体数据\
                \r\tprint(response.json())\
                \relse:\
                \r\t# assert '预期结果' in response.text # 判断字符串返回值结果 \
                \r\t# var_name = findall('正则表达式', response.text)[0] # 正则提取数据\
                \r\tprint(response.text)\n\n'''
    if is_xiaobaiauto2 == 1:
        return _code_top + _code_pytest_import + _code + _code_pytest_end
    elif is_xiaobaiauto2 == 2:
        return _code_top + _code_xiaobaiauto2_import + _code + _code_xiaobaiauto2_end + \
               '\n# 使用公共变量的格式：\n# PUBLIC_VARS["变量名"]\n' + _code_pytest_end
    elif is_xiaobaiauto2 == 3:
        return create_jmeter(request=data)
    else:
        return _code_top + _code_requests_import + _code

def har_convert(data: Optional[str], is_xiaobaiauto2: Optional[int] = 0):
    '''
    har单文件转换
    :param data:
    :param is_xiaobaiauto2:
    :return:
    '''
    if data != '':
        return convert(data=har_handle(data), is_xiaobaiauto2=is_xiaobaiauto2)
    else:
        return ''

def raw_convert(raw: Optional[str], is_xiaobaiauto2: Optional[int] = 0) -> str:
    '''
    原文转换器
    :param raw:
    :param is_xiaobaiauto2: 是否转xiaobaiauto2库代码样例
    :return:
    '''
    if raw != '':
        return convert(data=raw_handle(raw), is_xiaobaiauto2=is_xiaobaiauto2)
    else:
        return ''

def file_convert(data: Optional[str], is_xiaobaiauto2: Optional[int], is_har: Optional[bool]):
    if is_har:
        return har_convert(data=data, is_xiaobaiauto2=is_xiaobaiauto2)
    else:
        return raw_convert(raw=data, is_xiaobaiauto2=is_xiaobaiauto2)

def compare_str(k: Optional[str] = None, s0: Optional[str] = '', s1: Optional[str] = '',
                t: Optional[str] = 'text', is_xiaobaiauto2: Optional[int] = 0):
    '''
    比较两个字符串区别，暂时只考虑请求数据的不同，其他情况暂时忽略
    data = 'a=1&b=2&c=3'  字符串型
    data = '{'a':1, 'b': '0'}'  字典型
    data = '！@#￥%……&*'         文件内容型==字符串型
    :param s0: 字符串1
    :param s1: 字符串2
    :param t:  字符串是否含请求头
    :return:
    '''
    if 3 == is_xiaobaiauto2:
        start_step = '${'
        stop_step = '}'
    elif 4 == is_xiaobaiauto2:
        start_step = '{{'
        stop_step = '}}'
    else:
        start_step = '{'
        stop_step = '}'
    if 'json' in t and '{' in s0 and '}' in s0 and ':' in s0:
        try:
            d0 = loads(s0)
            d1 = loads(s1)
        except json.decoder.JSONDecodeError as e:
            try:
                if s0.startswith('\ufeff'):
                    s0 = s0.encode('utf8')[3:].decode('utf8')
                    d0 = loads(s0)
                if s1.startswith('\ufeff'):
                    s1 = s1.encode('utf8')[3:].decode('utf8')
                    d1 = loads(s1)
            except Exception as e:
                pass
        except JSONDecodeError as e:
            d0 = loads(s0.replace("'", '"'))
            d1 = loads(s1.replace("'", '"'))
        finally:
            return compare_dict(d0, d1, is_xiaobaiauto2=is_xiaobaiauto2)
    elif isinstance(s0, dict) and isinstance(s1, dict):
        compare_dict(s0, s1, is_xiaobaiauto2=is_xiaobaiauto2)
    else:
        IS_CUT = False
        result_str = ''
        s0s = s0
        s1s = s1
        if '?' in s0 and '?' in s1:
            s0 = s0[s0.find('?') + 1:]
            s1 = s1[s1.find('?') + 1:]
            IS_CUT = True
        # 分割参数
        sl0 = s0.split('&')
        sl0.sort()
        sl1 = s1.split('&')
        sl1.sort()
        for s_0, s_1 in zip(sl0, sl1):
            if '=' in s_0 and '=' in s_1:
                s_0l = s_0.split('=')
                s_1l = s_1.split('=')
                if s_0l[0] == s_1l[0] and s_0l[1] != s_1l[1]:
                    result_str += s_0l[0] + '=' + start_step + s_0l[0] + stop_step + '&'
                else:
                    result_str += s_0 + '&'
            elif s0s != s1s:
                result_str += start_step + k + stop_step
        if '&' == result_str[-1]:
            if IS_CUT:
                return s0s[:s0s.find('?') + 1] + result_str[:-1]
            else:
                return result_str[:-1]
        else:
            if IS_CUT:
                return s0s[:s0s.find('?') + 1] + result_str
            else:
                return result_str

def compare_dict(d0: Optional[dict], d1: Optional[dict], is_xiaobaiauto2: Optional[int] = 0) -> dict:
    '''
    比较两个字典数据
    :param d0:  字典对象1
    :param d1:  字典对象2
    :return:
    '''
    if not isinstance(d0, dict) and not isinstance(d1, dict) or d0 == {} or d1 == {}:
        return {}
    diff = d0.keys() & d1
    diffr = [(k, d0[k], d1[k]) for k in diff if d0[k] != d1[k]]
    diff_api = False
    if diffr.__len__() > 0:
        for v in diffr:
            if v[0] == 'method' and d0['method'] != d1['method']:
                diff_api = True
                break
            elif v[0] == 'url' and urlparse(d0['url']).path != urlparse(d1['url']).path:
                diff_api = True
                break
            elif v[0] == 'headers':
                d0[v[0]] = compare_dict(v[1], v[2], is_xiaobaiauto2)
            else:
                if 'headers' in d0.keys() and 'content-type' in d0['headers'].keys():
                    d0[v[0]] = compare_str(k=v[0], s0=v[1], s1=v[2], t=d0['headers']['content-type'], is_xiaobaiauto2=is_xiaobaiauto2)
                elif 'headers' in d0.keys() and 'Content-Type' in d0['headers'].keys():
                    d0[v[0]] = compare_str(k=v[0], s0=v[1], s1=v[2], t=d0['headers']['Content-Type'], is_xiaobaiauto2=is_xiaobaiauto2)
                else:
                    d0[v[0]] = compare_str(k=v[0], s0=v[1], s1=v[2], t='text', is_xiaobaiauto2=is_xiaobaiauto2)
    if diff_api:
        return {}
    else:
        d1.update(d0)
        return d1

def compare_har_convert(s0: Optional[str], s1: Optional[str], is_xiaobaiauto2: Optional[int] = 0):
    '''
    比较两个har文件字符串
    :param s0:
    :param s1:
    :return:
    '''
    result0 = har_handle(s0)
    result1 = har_handle(s1)
    result = []
    # 两个脚本数据雷同，记录条数一致
    for r0, r1 in zip(result0, result1):
        r = compare_dict(d0=r0, d1=r1, is_xiaobaiauto2=is_xiaobaiauto2)
        if r != {}:
            result.append(r)
        else:
            result.append(r0)
            result.append(r1)
    if result0.__len__() < result1.__len__():
        result.extend(result1[result0.__len__():])
    elif result1.__len__() < result0.__len__():
        result.extend(result0[result1.__len__():])
    if result.__len__() != 0:
        return convert(data=result, is_xiaobaiauto2=is_xiaobaiauto2)
    else:
        return ''

def yaml_convert(data: Optional[dict], is_xiaobaiauto2: Optional[int] = 0) -> list:
    '''
    YAML文档转python代码
    :param data:
    :param is_xiaobaiauto2:
    :return:
    YAML样例：
        -----------------------------------------------------------------------
        |# 本数据仅限于Python语言的PyYaml库正常解析，不保证其它库可正常解析
        |public:
        |  version: 1.0
        |  site: &site http://test.xiaobai.com/api/
        |  env:
        |    token: 0
        |list:
        |  - title: 登录
        |    method: POST
        |    headers:
        |      Content-Type: application/x-www-form-data
        |    url: !!python/object/apply:os.path.join [*site, login]
        |    paramers:
        |    data: username=username&password=password
        |    assert_mode: json
        |    assert_path: code
        |    assert_value: 200
        |    extract_mode: json
        |    extract_at: body
        |    extract_path: data.token
        |    extract_name: token
        |  - title: 注册
        |    method: POST
        |    url: !!python/object/apply:os.path.join [*site, register]
        |    paramers:
        |    data: username=username&password=password&repassword=password
        |    assert_mode: json
        |    assert_path: code
        |    assert_value: 200
        |  - title: 列表
        |    method: GET
        |    headers:
        |      token: ${token}
        |    url: !!python/object/apply:os.path.join [*site, list]
        |    assert_mode: json
        |    assert_path: code
        |    assert_value: 200
        |    extract_mode: json
        |    extract_at: body
        |    extract_path: data[1].id
        |    extract_name: id
        ------------------------------------------------------------------------
        |样例解释：
        |    &site 设置的变量，供yaml下文调用
        |    *site 表示调用yaml中的变量
        |    env 表示环境，下面定义的都是代码运行中的临时变量
        |    list 表示接口列表
        |    !!python/object/apply:os.path.join [*site, login]
        |    上面的内容表示：将yaml变量与字符串连接，如果表示域名，变量末尾最好带“/”符合
        |    ${token} 表示动态获取环境中的变量
        -------------------------------------------------------------------------
    '''

def copy_template(source: str = '', target: str = '.'):
    CMD = f'xcopy /E/S "{source}" "{target}"' if os.name == 'nt' else f'cp -r {source} {target}'
    if os.path.isdir(target):
        os.popen(CMD)

def api_raw(c: Optional[int], f: Optional[str], d: Optional[str], s: Optional[str], x: Optional[int]):
    is_har = False
    if x == 3:
        extname = '.jmx'
    else:
        extname = '.py'
    if ',' not in f or c == 0:
        if f != '' and os.path.isfile(f):
            raw_data = ''
            if os.path.splitext(f)[1] == '.saz':
                is_har = False
                raw_file_path = os.path.splitext(f)[0]
                zipfile.ZipFile(f).extractall(raw_file_path)
                raw_file_list = [i for i in os.listdir(raw_file_path + step + 'raw') if '_c.txt' == i[-6:]]
                for i in raw_file_list:
                    with open(raw_file_path + step + 'raw' + step + i, 'r', encoding='utf-8') as fr:
                        raw_data += fr.read() + '\n\n\n'
                        fr.close()
                if os.path.isdir(raw_file_path):
                    try:
                        os.remove(raw_file_path)
                    except PermissionError as e:
                        pass
            elif os.path.splitext(f)[1] == '.har':
                is_har = True
                with open(f, 'r', encoding='utf-8') as fr:
                    raw_data += fr.read()
                    fr.close()
            elif os.path.splitext(f)[1] == '.txt':
                with open(f, 'r', encoding='utf-8') as fr:
                    is_har = False
                    raw_data += fr.read()
                    fr.close()
            code = file_convert(data=raw_data, is_xiaobaiauto2=x, is_har=is_har)
            if s != '':
                with open(s + extname, 'w', encoding='utf-8') as fw:
                    fw.write(code)
                    fw.flush()
                    fw.close()
            else:
                with open(os.path.splitext(f)[0] + extname, 'w', encoding='utf-8') as fw:
                    fw.write(code)
                    fw.flush()
                    fw.close()
        else:
            if f != '':
                if os.path.isfile(d + step + f):
                    raw_data = ''
                    if os.path.splitext(d + step + f)[1] == '.saz':
                        is_har = False
                        raw_file_path = os.path.splitext(d + step + f)[0]
                        zipfile.ZipFile(d + step + f).extractall(raw_file_path)
                        raw_file_list = [i for i in os.listdir(d + step + raw_file_path + step + 'raw') if '_c.txt' == i[-6:]]
                        for i in raw_file_list:
                            with open(d + step + raw_file_path + step + 'raw' + step + i, 'r') as fr:
                                raw_data += fr.read() + '\n\n\n'
                                fr.close()
                        if os.path.isdir(d + step + raw_file_path):
                            try:
                                os.remove(d + step + raw_file_path)
                            except PermissionError as e:
                                raise (e)
                    elif os.path.splitext(d + step + f)[1] == '.har':
                        is_har = True
                        with open(d + '/' + f, 'r', encoding='utf-8') as fr:
                            raw_data += fr.read()
                            fr.close()
                    elif os.path.splitext(d + step + f)[1] == '.txt':
                        with open(d + step + f, 'r', encoding='utf-8') as fr:
                            is_har = False
                            raw_data += fr.read()
                            fr.close()
                    code = file_convert(data=raw_data, is_xiaobaiauto2=x, is_har=is_har)
                    if s != '':
                        with open(d + step + s + extname, 'w', encoding='utf-8') as fw:
                            fw.write(code)
                            fw.flush()
                            fw.close()
                    else:
                        with open(os.path.splitext(d + step + f)[0] + extname, 'w', encoding='utf-8') as fw:
                            fw.write(code)
                            fw.flush()
                            fw.close()
            else:
                for f in [i for i in os.listdir(d) if os.path.splitext(i)[1] in ['.saz', '.har', '.txt']]:
                    raw_data = ''
                    if os.path.splitext(d + step + f)[1] == '.saz':
                        is_har = False
                        raw_file_path = os.path.splitext(d + step + f)[0]
                        zipfile.ZipFile(d + step + f).extractall(raw_file_path)
                        raw_file_list = [i for i in os.listdir(raw_file_path + step + 'raw') if
                                         '_c.txt' == i[-6:]]
                        for i in raw_file_list:
                            with open(raw_file_path + step + 'raw' + step + i, 'r') as fr:
                                raw_data += fr.read() + '\n\n\n'
                                fr.close()
                        if os.path.isdir(raw_file_path):
                            try:
                                os.remove(raw_file_path)
                            except PermissionError as e:
                                pass
                    elif os.path.splitext(d + step + f)[1] == '.har':
                        is_har = True
                        with open(d + step + f, 'r', encoding='utf-8') as fr:
                            raw_data += fr.read()
                            fr.close()
                    elif os.path.splitext(d + step + f)[1] == '.txt':
                        with open(d + step + f, 'r', encoding='utf-8') as fr:
                            is_har = False
                            raw_data += fr.read()
                            fr.close()
                    code = file_convert(data=raw_data, is_xiaobaiauto2=x, is_har=is_har)
                    if s != '':
                        with open(d + step + s + extname, 'w', encoding='utf-8') as fw:
                            fw.write(code)
                            fw.flush()
                            fw.close()
                    else:
                        with open(os.path.splitext(d + step + f)[0] + extname, 'w', encoding='utf-8') as fw:
                            fw.write(code)
                            fw.flush()
                            fw.close()
    elif ',' in f and c == 1:
        f_l = f.split(',')
        if f_l.__len__() == 2 and \
                os.path.isfile(f_l[0]) and \
                os.path.isfile(f_l[1]) and \
                os.path.splitext(f_l[0])[1] == '.har':
            ''' 暂时支持比较 *.har格式文件 '''
            data0 = ''
            data1 = ''
            with open(f_l[0], 'r', encoding='utf-8') as fr:
                data0 += fr.read()
                fr.close()
            with open(f_l[1], 'r', encoding='utf-8') as fr:
                data1 += fr.read()
                fr.close()
            code = compare_har_convert(s0=data0, s1=data1, is_xiaobaiauto2=x)
            if s != '':
                with open(s + extname, 'w', encoding='utf-8') as fw:
                    fw.write(code)
                    fw.flush()
                    fw.close()
            else:
                with open(os.path.splitext(f_l[0])[0] + '_' + os.path.splitext(f_l[1])[0] + '_compare' + extname,
                          'w', encoding='utf-8') as fw:
                    fw.write(code)
                    fw.flush()
                    fw.close()
        elif f_l.__len__() == 2 and \
                os.path.isfile(d + step + f_l[0]) and \
                os.path.isfile(d + step + f_l[1]) and \
                os.path.splitext(f_l[0])[1] == '.har':
            ''' 暂时支持比较 *.har格式文件 '''
            data0 = ''
            data1 = ''
            with open(d + step + f_l[0], 'r', encoding='utf-8') as fr:
                data0 += fr.read()
                fr.close()
            with open(d + step + f_l[1], 'r', encoding='utf-8') as fr:
                data1 += fr.read()
                fr.close()
            code = compare_har_convert(s0=data0, s1=data1, is_xiaobaiauto2=x)
            if s != '':
                with open(d + step + s + extname, 'w', encoding='utf-8') as fw:
                    fw.write(code)
                    fw.flush()
                    fw.close()
            else:
                with open(d + step + os.path.splitext(f_l[0])[0] + '_' + os.path.splitext(f_l[1])[0] + '_compare' + extname,
                          'w', encoding='utf-8') as fw:
                    fw.write(code)
                    fw.flush()
                    fw.close()
        else:
            ''' 大于两个文件比较 '''
            print('目前支持两个文件比较，两次的请求包已经可以比较出其差异:>')

def cmd():
    arg = argparse.ArgumentParser(
        '小白科技·Python接口转换器·工具下载器 v' + __version__
    )
    arg.add_argument('-c', '--compare',
                     type=int,
                     choices=(0, 1),
                     default=0,
                     help='比较两个har文件的区别,并转为python代码,0:不比较(默认),1:比较')
    arg.add_argument('-f', '--file', type=str, default='', help='支持har|saz|txt扩展名的raw数据文件')
    arg.add_argument('-d', '--dir', type=str, default='.',
                     help='批量转换指定目录下所有har|saz|txt扩展名的raw数据文件, 默认当前目录')
    arg.add_argument('-s', '--save', type=str, default='', help='默认生成同名的脚本文件,省略扩展名')
    arg.add_argument('-x', '--xiaobai', type=int, choices=(0, 1, 2, 3), default=0,
                     help='0:requests格式(默认),1:pytest格式,2:xiaobaiauto2格式,3:jmeter格式')
    arg.add_argument('-t', '--template', default='',
                     help='获取模板到本地,无模板(默认),api模板,web模板,app模板')
    arg.add_argument('-i', '--install', default=-1, help='(默认)不安装,支持jdk|jmeter|chromdriver|jenkins|git|node')
    arg.add_argument('-v', '--version', type=str, default='latest', help='指定软件的版本，默认最新版')
    params = arg.parse_args()
    package_path_list = [p for p in sys.path if '\\lib\\site-packages' in p]
    if sys.platform == 'win32':
        package_path = package_path_list[0] \
            if len(package_path_list) > 0 else os.popen('pip show xiaobaiauto2').readlines()[7].split(' ')[-1][:-1]
    else:
        package_path = package_path_list[0] \
            if len(package_path_list) > 0 else os.popen('pip3 show xiaobaiauto2').readlines()[7].split(' ')[-1][:-1]
    if params.install in [0, 'jdk']:
        v = params.version
        if v != '':
            jdk_install(v, params.dir)
        else:
            jdk_install(dest_dir=params.dir)
    elif params.install in [1, 'jmeter', 'JMeter']:
        v = params.version
        if v != '':
            jmeter_install(v, params.dir)
        else:
            jmeter_install(dest_dir=params.dir)
    elif params.install in [2, 'chromedriver', 'ChromeDriver']:
        v = params.version
        if v != '':
            chromedriver_download(v, params.dir)
        else:
            chromedriver_download(dest_dir=params.dir)
    elif params.install == 'jenkins':
        v = params.version
        if v != '':
            jenkins_war_install(v, params.dir)
        else:
            jenkins_war_install(dest_dir=params.dir)
    elif params.install == 'git':
        v = params.version
        if v != '':
            git_windows_install(v, params.dir)
        else:
            git_windows_install(dest_dir=params.dir)
    elif params.install in ['node', 'nodejs']:
        v = params.version
        if v != '':
            node_install(v, params.dir)
        else:
            node_install(dest_dir=params.dir)
    elif params.install in ['allure', 'Allure']:
        v = params.version
        if v != '':
            allure_install(v, params.dir)
        else:
            allure_install(dest_dir=params.dir)
    elif params.install in ['svn', 'subversion']:
        v = params.version
        if v != '':
            svn_install(v, params.dir)
        else:
            svn_install(dest_dir=params.dir)
    elif params.install in ['adb']:
        v = params.version
        if v != '':
            adb_install(v, params.dir)
        else:
            adb_install(dest_dir=params.dir)
    elif params.install in ['fiddler', 'Fiddler']:
        v = params.version
        if v != '':
            fiddler_install(v, params.dir)
        else:
            fiddler_install(dest_dir=params.dir)
    elif params.install in ['postman', 'PostMan']:
        v = params.version
        if v != '':
            postman_install(v, params.dir)
        else:
            postman_install(dest_dir=params.dir)
    elif params.template in [0, 'api']:
        shutil.copytree(f'{package_path}{step}xiaobaiauto2{step}test{step}ApiTest', f'{params.dir}{step}ApiTest')
    elif params.template in [1, 'web']:
        shutil.copytree(f'{package_path}{step}xiaobaiauto2{step}test{step}WebTest', f'{params.dir}{step}WebTest')
    elif params.template in [2, 'app']:
        shutil.copytree(f'{package_path}{step}xiaobaiauto2{step}test{step}AppTest', f'{params.dir}{step}AppTest')
    else:
        api_raw(c=params.compare, f=params.file, d=params.dir, s=params.save, x=params.xiaobai)
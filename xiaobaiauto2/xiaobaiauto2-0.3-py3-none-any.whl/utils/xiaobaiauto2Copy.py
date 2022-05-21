#! /usr/bin/env python
# coding=utf-8

__auther__ = 'Tser'
__mail__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'xiaobaiauto2Copy.py'
__created__ = '2022/5/20 1:03'

import pyperclip
from re import findall
from time import sleep, ctime, time
from tkinter.messagebox import askyesno, showinfo

def curl2requests(curl_str: str = None):
    '''
    解析参数文档：https://curl.se/docs/manpage.html
    解析curl中的地址、请求方法：-X、请求头：-H、请求体：--data-raw、证书不验证：--insecure，其他参数后续再追加
    '''
    if 'curl' == curl_str[:4] and '-H' in curl_str:
        code = '''# 本代码为解析代码，可能存在不确定性问题，如有问题请及时与作者微信联系：xiaobaiTser，感谢您的使用☺
                    \rfrom requests import request\
                    \rfrom re import findall\
                    \r
        '''
        curl_str = curl_str.replace('\n', '').replace('\\\r', '').replace('   ', ' ')
        url = ''
        method = 'GET'
        data = ''
        verify = True
        if '--compressed' in curl_str and 'curl -H' != curl_str[:7]:
            ''' browser '''
            URLReResult = findall('curl [\'|\"](\S+)[\'|\"]', curl_str)
            url = URLReResult[0] if URLReResult.__len__() > 0 else ''
            DataReResult = findall('--data-raw [\'|\"](\S+)[\'|\"]', curl_str)
            data = DataReResult[0] if DataReResult.__len__() > 0 else ''
            if data:
                method = 'POST'
            else:
                method = 'GET'
            if '--insecure' in curl_str:
                verify = False
        elif '--compressed' in curl_str and 'curl -H' == curl_str[:7]:
            ''' charles '''
            URLReResult = findall('--compressed [\'|\"](\S+)[\'|\"]', curl_str)
            url = URLReResult[0] if URLReResult.__len__() > 0 else ''
            DataReResult = findall('--data-binary [\'|\"](\S+)[\'|\"]', curl_str)
            data = DataReResult[0] if DataReResult.__len__() > 0 else ''
            if data:
                method = 'POST'
            else:
                method = 'GET'
            if ' -k ' in curl_str:
                verify = False
        elif '--compressed' not in curl_str and '-o' in curl_str:
            ''' fiddler '''
            if '-X' in curl_str:
                URLReResult = findall('-X [A-Z]+ [\'|\"](\S+)[\'|\"]', curl_str)
                url = URLReResult[0] if URLReResult.__len__() > 0 else ''
            else:
                URLReResult = findall('[\'|\"](.+?)[\'|\"]', curl_str)
                URLFilter = [i for i in URLReResult if ' ' not in i]
                url = URLFilter[0] if URLFilter.__len__() > 0 else ''
            methodReResult = findall('-X ([A-Z]+)', curl_str)
            method = methodReResult[0] if methodReResult.__len__() > 0 else 'GET'
        headers = {}
        header_list = findall('-H [\'|\"](.+?)[\'|\"]', curl_str)
        for value in header_list:
            header = value.split(': ')
            headers[header[0]] = header[1]
        code += f'''\
            \rurl = '{url}'\
            \rmethod = '{method}'\
            \rheaders = {headers}\
            '''
        if data:
            code += f'''\
                \rdata = '{data}'\
                '''
        if False == verify:
            code += f'''\
                \rverify = {verify}\
                '''
        if data and False == verify:
            code += '''
                \rresponse = request(method=method, url=url, headers=headers, data=data, verify=verify)\
                '''
        elif data and True == verify:
            code += '''
                \rresponse = request(method=method, url=url, headers=headers, data=data)\
                '''
        elif not data and False == verify:
            code += '''
                \rresponse = request(method=method, url=url, headers=headers, verify=verify)\
                '''
        else:
            code += '''
                \rresponse = request(method=method, url=url, headers=headers)\
                '''
        code += '''
            \r# 测试后数据判断/提取\
            \r# assert response.status_code == 200  # 判断HTTP响应状态\
            \r# var_name = response.headers()[路径]  # 提取响应头数据\
            \rif 'json' in response.headers.get('Content-Type'):\
            \r    # assert '预期结果' == response.json()[路径]  # 判断json响应体结果\
            \r    # var_name = response.json()[路径]  # 提取json响应体数据\
            \r    print(response.json())\
            \relse:\
            \r    # assert '预期结果' in response.text # 判断字符串返回值结果\
            \r    # var_name = findall('正则表达式', response.text)[0] # 正则提取数据\
            \r    print(response.text)\
            '''
        pyperclip.copy(code)
        return '已转为requests代码，请使用[Ctrl + V]粘贴使用☺'
    else:
        return '无效内容，转换失败，请微信联系作者：xiaobaiTser'

def main():
    while True:
        CPtext = pyperclip.paste()
        if 'curl ' in CPtext[:5]:
            result = askyesno(title='小白提示：', message='发现粘贴板有curl脚本是否转requests代码？')
            if 1 == result:
                ''' 代码替换 '''
                msg = curl2requests(CPtext)
                showinfo(title='小白提示：', message=msg)
        sleep(1)
        print('', end='\r')
        print(f'[{ctime()}]正在监听粘贴板中{"."*(int(time())%6)}', end='')
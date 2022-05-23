#! /usr/bin/env python
# -*- coding=utf-8 -*-
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'xiaobaiauto2Subprocess.py'
__create_time__ = '2021/1/4 17:13'

import subprocess
import shlex
import re
import os
from datetime import datetime
from xiaobaiauto2.utils import _get_xpath, del_temp
from xiaobaiauto2.utils.code_template import *

devices = []
version = '0.0'
info = '''
# 本脚本为录制自动生成，本脚本会有部分的脚本与实际场景存在出入，例如：如何获取哪个操作是输入框的动作，哪个操作是按钮的操作，所以
# 导致无法准备生成输入的输入操作（send_keys方法），会在后续的版本中更新:）
# 脚本的自动生成属于人为操作与机器识别，故准确度不能保证为100%，解释权为小白科技拥有:)
# 未经许可不能用于商业用途！！！
# 可自由用于学习或者研究使用！！！
'''

def dataProcess(data=None, filename=''):
    if '' != filename and data:
        name, extname = os.path.splitext(filename)
        with open(name + '.py', 'a', encoding='utf-8') as f:
            if data.count('\t') == 2:
                ''' head '''
                data_list = data.split('\t')
                package_activity = data_list[2].split('/')
                code = appium_head_template_code % (info, version, data_list[1].replace('[', '').replace(']', ''),
                                                    package_activity[0], package_activity[1])
            elif data.count('\t') == 3:
                data_list = data.split('\t')
                if data_list[3] in ['//', None, 'None']:
                    code = appium_location_by_position_template_code % (data_list[2].replace('[', '').replace(']', ''),
                                                                        data_list[2].replace('[', '').replace(']', ''))
                else:
                    path_list = data_list[3].split('/')
                    if 'EditText' not in path_list[-1]:
                        code = appium_location_by_xpath_of_click_template_code % data_list[3]
                    else:
                        code = appium_location_by_xpath_of_sendkeys_template_code % data_list[3]
            else:
                code = ''
            f.write(code)
            f.flush()
            f.close()
    elif data:
        print(data)
    else:
        pass

def syncSub(cmd=None, match=None, other=None, deviceName=None, filename=''):
    if cmd:
        global devices, version
        all_r = []
        p = subprocess.Popen(shlex.split(cmd), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while p.poll() is None:
            l = p.stdout.readline()
            l = l.strip()
            if l and match and other == 'getevent':
                r = [int(v, 16) for v in re.findall(match, str(l, encoding='utf-8'))]
                if r != [] and r != b'' and r != [0]:
                    all_r.extend(r)
            elif l and match and other:
                r = re.findall(match, str(l, encoding='utf-8'))
                if r != [] and r != b'' and r != [0]:
                    all_r.extend(r)
            if other == 'device':
                devices.extend(all_r)
                all_r.clear()
            elif other == 'version':
                if l != b'': version = l.decode('utf-8')
            elif other == 'activity':
                if all_r != []:
                    dataProcess(f'[{datetime.now()}]\t[{str(deviceName).split(" ")[-1]}]\t{all_r[0]}', filename)
                    all_r.clear()
            elif len(all_r) > 1:
                if other == 'getevent':
                    try:
                        print('[debug]-all_r:', all_r)
                        xpath = _get_xpath(x=all_r[0], y=all_r[1], deviceName=deviceName)
                        del_temp()
                        dataProcess(f'[{datetime.now()}]\t[{str(deviceName).split(" ")[-1]}]\t{all_r}\t{xpath}', filename)
                    except Exception as e:
                        dataProcess(f'[{datetime.now()}]\t[{str(deviceName).split(" ")[-1]}]\t{all_r}\t{e}')
                elif other == 'size':
                    dataProcess(f'[{datetime.now()}]\t[{str(deviceName).split(" ")[-1]}]\t{all_r}')
                all_r.clear()
        if p.returncode == 0:
            return True
        else:
            return False
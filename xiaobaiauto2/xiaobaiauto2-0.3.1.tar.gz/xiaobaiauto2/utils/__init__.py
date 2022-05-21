#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = '__init__.py'
__create_time__ = '2020/7/15 23:12'

import re
import os
try:
    import winreg
except ModuleNotFoundError as e:
    ''' 非windows系统 '''
import shutil
import xml.dom.minidom
from typing import Union, Optional

step = '\\' if os.name == 'nt' else '/'
grep = 'findstr' if os.name == 'nt' else 'grep'
home = os.environ['HOMEPATH'] if 'HOMEPATH' in os.environ.keys() else os.environ['HOME']
home = 'C:\\' + home if os.name == 'nt' else home

def _get_path(cmd='adb'):
    _path = shutil.which(cmd=cmd)
    if not _path and os.name == 'nt':
        return os.path.dirname(os.path.abspath(__file__)) + step + 'adb' + step + 'adb.exe'
    else:
        return _path

def _get_xpath(x: Union[int, str], y: Union[int, str], deviceName=None):
    x, y = int(x), int(y)
    device = deviceName if deviceName else ''
    ADB_COMMAND = f'"{_get_path("adb")}" '
    os.popen(f'{ADB_COMMAND} {device} shell uiautomator dump /sdcard/ui.xml')
    os.popen(f'{ADB_COMMAND} {device} pull /sdcard/ui.xml "{home}"')
    if os.name == 'nt':
        r = re.findall('003[56]\s+.+max\s+(\d+)', os.popen(cmd=f'{ADB_COMMAND} {device} shell getevent -p').read())
    else:
        r = re.findall('003[56]\s+.+max\s+(\d+)',
                       os.popen(cmd=f'{ADB_COMMAND} {device} shell getevent -p | grep -e "0035" -e "0036" | grep -e "max"').read())
    filePath = f'{home}{step}ui.xml'
    if os.path.isfile(filePath):
        DOM = xml.dom.minidom.parse(filePath)
        coll = DOM.documentElement
        nodes = coll.getElementsByTagName('node')
        path = xpath = ''
        pare_size = int(r[0]) * int(r[1])
        for node in nodes:
            pos = re.findall('(\d+)', node.getAttribute('bounds'))
            if x > int(pos[0]) and y > int(pos[1]) and x < int(pos[2]) and y < int(pos[3]):
                if (int(pos[2]) - int(pos[0])) * (int(pos[3]) - int(pos[1])) > pare_size:
                    continue
                pare_size = (int(pos[2]) - int(pos[0])) * (int(pos[3]) - int(pos[1]))
                className = node.getAttribute('class')
                node_class = className if className not in ["", None] else "*"
                node_text = node.getAttribute('text')
                node_id = node.getAttribute('resource-id')
                node_content = node.getAttribute('content-desc')
                node_index = node.getAttribute('index')
                if node_id != "" and node_text != "":
                    path += f'{node_class}[@resource-id="{node_id}" and @text="{node_text}"]/'
                elif node_id != "" and node_text == "":
                    path += f'{node_class}[@resource-id="{node_id}"]/'
                elif node_id == "" and node_text != "":
                    path += f'{node_class}[@text="{node_text}"]/'
                elif node_content != "":
                    path += f'{node_class}[@content-desc="{node_content}"]/'
                else:
                    path += f'{node_class}[{node_index}]/'
        path_list = path[:-1].split('/')
        for i in range(len(path_list) - 1, 0, -1):
            xpath = f'{path_list[i]}/{xpath}'
            if '[@resource-id="' in path_list[i] or '[@text="' in path_list[i] or '[@content-desc="' in path_list[i]:
                break
        return '//' + xpath[:-1]
    else:
        print('截图文件不存在！！！')
        return None

def getPointImg(x: int, y: int):
    ''' 依据指定的左边进行小范围截图
        x,y
        截图坐标（x-5,y-5,x+5,y+5）
    '''

def findpointImg(target, source):
    ''' 将source在target中进行定位 '''

def del_temp(file=f'{home}{step}ui.xml'):
    if os.path.isfile(file):
        try:
            os.remove(file)
        except PermissionError as e:
            print(e)

def win_reg_WRITE_HKEY_CURRENT_USER(path: Optional[str] = None):
    return winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_WRITE)

def win_reg_READ_HKEY_CURRENT_USER(path: Optional[str] = None):
    return winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_READ)

def win_reg_READ_HKEY_LOCAL_MACHINE(path: Optional[str] = None):
    return winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)

def win_reg_WRITE_HKEY_LOCAL_MACHINE(path: Optional[str] = None):
    return winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_WRITE)

def win_reg_write(path: Optional[str] = None, name: Optional[str] = None,  value: Union[int, str] = None):
    K = win_reg_WRITE_HKEY_CURRENT_USER(path=path)
    try:
        winreg.SetValueEx(K, name, 0, winreg.REG_DWORD, value)
    except Exception as e:
        winreg.SetValueEx(K, name, 0, winreg.REG_SZ, value)
    winreg.CloseKey(K)

def win_reg_read(path: Optional[str] = None, name: Optional[str] = None):
    K = win_reg_READ_HKEY_CURRENT_USER(path=path)
    V = winreg.QueryValueEx(K, name)
    winreg.CloseKey(K)
    return V

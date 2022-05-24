#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'xiaobaiauto2App.py'
__create_time__ = '2020/12/29 21:41'

import os
from argparse import ArgumentParser
from xiaobaiauto2.utils.xiaobaiauto2Subprocess import syncSub, devices, dataProcess
from xiaobaiauto2.__version__ import __version__
from xiaobaiauto2.utils import grep, _get_path

def adb_cmd():
    ADB_COMMAND = f'"{_get_path("adb")}" '
    arg = ArgumentParser(prog='xiaobaiauto2App [optional] [command]',
                         description=f'小白科技·移动设备调试桥·{__version__}')
    arg.add_argument('-d', '--deviceName', default='', help='多设备场景使用')
    arg.add_argument('-i', '--index', default=0, type=int, help='设备索引，多设备场景使用')
    arg.add_argument('-s', '--save', default='', type=str, help='需要保存的*.py脚本')
    par = arg.parse_args()
    syncSub(ADB_COMMAND + 'devices -l', match='(\S+)\s+device\s+', other='device', filename=par.save)
    if par.deviceName == '' and isinstance(devices, list) and devices.__len__() > 0 or\
        par.deviceName != '' and par.deviceName not in devices:
        deviceName = '-s ' + devices[par.index]
    elif par.deviceName != '' and isinstance(devices, list) and devices.__len__() > 0 and par.deviceName in devices:
        deviceName = '-s ' + par.deviceName
    else:
        deviceName = ''
    version = os.popen(cmd=f'{ADB_COMMAND}{deviceName} shell getprop ro.build.version.release').read()
    syncSub(f'{ADB_COMMAND}{deviceName} shell getprop ro.build.version.release',
            other='version', deviceName=deviceName, filename=par.save)
    if os.name == 'nt':
        syncSub(f'{ADB_COMMAND}{deviceName} shell getevent -p',
                match='003[56]\s+.+max\s+(\d+)', other='size', deviceName=deviceName, filename=par.save)
    else:
        syncSub(f'{ADB_COMMAND}{deviceName} shell getevent -p' + f'| {grep} -e "0035" -e "0036" | {grep} -e "max"',
                match='003[56]\s+.+max\s+(\d+)', other='size', deviceName=deviceName, filename=par.save)
    if [int(v) for v in version.split('.')] >= [int(v) for v in '8.1'.split('.')]:
        syncSub(f'{ADB_COMMAND}{deviceName} shell dumpsys activity | grep ' + '"mResume"',
                match='([\.0-9a-zA-Z]+?/[\.0-9a-zA-Z]+)', other='activity', deviceName=deviceName, filename=par.save)
    else:
        syncSub(f'{ADB_COMMAND}{deviceName} shell dumpsys activity | grep ' + '"mFocus"',
                match='([\.0-9a-zA-Z]+?/[\.0-9a-zA-Z]+)', other='activity', deviceName=deviceName, filename=par.save)
    try:
        syncSub(f'{ADB_COMMAND}{deviceName} shell getevent',
                match='003[56]\s+[0]+([0-9a-f]+)', other='getevent', deviceName=deviceName, filename=par.save)
    except KeyboardInterrupt as e:
        print('您已经手动终止进程.')
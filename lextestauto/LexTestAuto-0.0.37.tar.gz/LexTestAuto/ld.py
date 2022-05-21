# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : ld.py
# Time       ：22/3/12 2:06
# Author     ：Lex
# email      : 2983997560@qq.com
# Description：
"""

import os
from xml.dom.minidom import parseString


class DnPlayer(object):
    def __init__(self, info: list):
        super(DnPlayer, self).__init__()
        # 索引，标题，顶层窗口句柄，绑定窗口句柄，是否进入android，进程PID，VBox进程PID
        self.index = int(info[0])
        self.name = info[1]
        self.top_win_handler = int(info[2])
        self.bind_win_handler = int(info[3])
        self.is_in_android = True if int(info[4]) == 1 else False
        self.pid = int(info[5])
        self.vbox_pid = int(info[6])

    def is_running(self) -> bool:
        return self.is_in_android

    def __str__(self):
        index = self.index
        name = self.name
        r = str(self.is_in_android)
        twh = self.top_win_handler
        bwh = self.bind_win_handler
        pid = self.pid
        vpid = self.vbox_pid
        return "\nindex:%d name:%s top:%08X bind:%08X running:%s pid:%d vbox_pid:%d\n" % (
            index, name, twh, bwh, r, pid, vpid)

    def __repr__(self):
        index = self.index
        name = self.name
        r = str(self.is_in_android)
        twh = self.top_win_handler
        bwh = self.bind_win_handler
        pid = self.pid
        vpid = self.vbox_pid
        return "\nindex:%d name:%s top:%08X bind:%08X running:%s pid:%d vbox_pid:%d\n" % (
            index, name, twh, bwh, r, pid, vpid)


class UserInfo(object):
    def __init__(self, text: str = ""):
        super(UserInfo, self).__init__()
        self.info = dict()
        if len(text) == 0:
            return
        self.__xml = parseString(text)
        nodes = self.__xml.getElementsByTagName('node')
        res_set = [
            # 用户信息节点
        ]
        name_set = [
            'id', 'id', 'following', 'fans', 'all_like', 'rank', 'flex',
            'signature', 'location', 'video', 'name'
        ]
        number_item = ['following', 'fans', 'all_like', 'video', 'videolike']
        for n in nodes:
            name = n.getAttribute('resource-id')
            if len(name) == 0:
                continue
            if name in res_set:
                idx = res_set.index(name)
                text = n.getAttribute('text')
                if name_set[idx] not in self.info:
                    self.info[name_set[idx]] = text
                    print(name_set[idx], text)
                elif idx == 9:
                    self.info['videolike'] = text
                elif idx < 2:
                    if len(text) == 0:
                        continue
                    if self.info['id'] != text:
                        self.info['id'] = text
        for item in number_item:
            if item in self.info:
                self.info[item] = int(self.info[item].replace('w', '0000').replace('.', ''))

    def __str__(self):
        return str(self.info)

    def __repr__(self):
        return str(self.info)


class LdConsole:
    # 请根据自己电脑配置
    console = None
    ld = None

    # 获取模拟器列表
    @staticmethod
    def get_list():
        cmd = os.popen(LdConsole.console + 'list2')
        text = cmd.read()
        cmd.close()
        info = text.split('\n')
        result = list()
        for line in info:
            if len(line) > 1:
                dnplayer = line.split(',')
                result.append(DnPlayer(dnplayer))
        return result

    # 获取正在运行的模拟器列表
    @staticmethod
    def list_running() -> list:
        result = list()
        all = LdConsole.get_list()
        for dn in all:
            if dn.is_running() is True:
                result.append(dn)
        return result

    # 检测指定序号的模拟器是否正在运行
    @staticmethod
    def is_running(index: int) -> bool:
        all = LdConsole.get_list()
        if index >= len(all):
            raise IndexError('%d is not exist' % index)
        return all[index].is_running()

    # 启动App  指定模拟器必须已经启动
    @staticmethod
    def invokeapp(index: int, package: str):
        cmd = LdConsole.console + 'runapp --index %d --packagename %s' % (index, package)
        process = os.popen(cmd)
        result = process.read()
        process.close()
        print(result)
        return result

    # 停止App  指定模拟器必须已经启动
    @staticmethod
    def stopapp(index: int, package: str):
        cmd = LdConsole.console + 'killapp --index %d --packagename %s' % (index, package)
        process = os.popen(cmd)
        result = process.read()
        process.close()
        return result

    # 启动模拟器
    @staticmethod
    def launch(index: int):
        cmd = LdConsole.console + 'launch --index ' + str(index)
        process = os.popen(cmd)
        result = process.read()
        process.close()
        return result

    # 关闭模拟器
    @staticmethod
    def quit(index: int):
        cmd = LdConsole.console + 'quit --index ' + str(index)
        process = os.popen(cmd)
        result = process.read()
        process.close()
        return result

    # 设置屏幕分辨率为1080×1920 下次启动时生效
    @staticmethod
    def set_screen_size(index: int):
        cmd = LdConsole.console + 'modify --index %d --resolution 1080,1920,480' % index
        process = os.popen(cmd)
        result = process.read()
        process.close()
        return result

    # 点击或者长按某点
    @staticmethod
    def touch(index: int, x: int, y: int, delay: int = 0):
        if delay == 0:
            LdConsole.dnld(index, 'input tap %d %d' % (x, y))
        else:
            LdConsole.dnld(index, 'input touch %d %d %d' % (x, y, delay))

    # 滑动
    @staticmethod
    def swipe(index, coordinate_leftup: tuple, coordinate_rightdown: tuple, delay: int = 0):
        x0 = coordinate_leftup[0]
        y0 = coordinate_leftup[1]
        x1 = coordinate_rightdown[0]
        y1 = coordinate_rightdown[1]
        if delay == 0:
            LdConsole.dnld(index, 'input swipe %d %d %d %d' % (x0, y0, x1, y1))
        else:
            LdConsole.dnld(index, 'input swipe %d %d %d %d %d' % (x0, y0, x1, y1, delay))

    # 复制模拟器,被复制的模拟器不能启动
    @staticmethod
    def copy(name: str, index: int = 0):
        cmd = LdConsole.console + 'copy --name %s --from %d' % (name, index)
        process = os.popen(cmd)
        result = process.read()
        process.close()
        return result

    # 添加模拟器
    @staticmethod
    def add(name: str):
        cmd = LdConsole.console + 'add --name %s' % name
        process = os.popen(cmd)
        result = process.read()
        process.close()
        return result

    # 改变设备信息 imei imsi simserial androidid mac值
    @staticmethod
    def change_device_data(index: int):
        # 改变设备信息
        cmd = LdConsole.console + 'modify --index %d --imei auto --imsi auto --simserial auto --androidid auto --mac auto' % index
        process = os.popen(cmd)
        result = process.read()
        process.close()
        return result

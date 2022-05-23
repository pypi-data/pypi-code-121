#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'xiaobaiauto2Proxy.py'
__create_time__ = '2021/1/12 23:22'
'''
    代理服务器的查看、启动、关闭
'''
from urllib import request, error
from argparse import ArgumentParser
from typing import Union, Optional
from xiaobaiauto2.utils import win_reg_write, win_reg_read
from xiaobaiauto2.__version__ import __version__

class ProxyServer(object):
    proxy: Optional[str] = '127.0.0.1:8080'  # default use mitmproxy
    disProxy: Optional[str] = 'localhost;127.*;192.*;10.*'
    def StartProxy(self):
        ''' 启动系统代理服务器 '''

    def StopProxy(self):
        ''' 关闭系统代理服务器 '''

    def StatusProxy(self):
        ''' 查看系统代理服务器状态 '''

class WindowsProxy(ProxyServer):
    _path = 'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
    _name1 = 'ProxyEnable'
    _name2 = 'ProxyServer'
    _name3 = 'ProxyOverride'
    def _setProxy(self, enable=0, proxy=None, ignoreip=None):
        win_reg_write(self._path, self._name1, enable)
        win_reg_write(self._path, self._name2, proxy)
        win_reg_write(self._path, self._name3, ignoreip)

    def getProxy(self, path, name):
        return win_reg_read(path, name)

    def StartProxy(self):
        try:
            self._setProxy(1, self.proxy, self.disProxy)
            print('启动代理已设置为:', self.proxy)
        except Exception as e:
            print('启动代理失败', e)

    def StopProxy(self):
        try:
            self._setProxy(0, '', '')
            print('代理已关闭成功')
        except Exception as e:
            print('关闭代理失败', e)

    def StatusProxy(self):
        try:
            if self.getProxy(self._path, self._name1)[0] == 1:
                print('代理已启动')
            else:
                print('代理已关闭')
        except Exception as e:
            print('查询代理状态失败', e)

    def LiveProxy(self):
        try:
            f = self.getProxy(self._path, self._name1)[0]
        except Exception as e:
            print(e)
            exit(0)
        if f == 1:
            try:
                response = request.urlopen(url='https://www.baidu.com', timeout=5)
                if bytes('全球最大的中文搜索引擎', 'utf-8') in response.read():
                    print('当前代理有效')
                else:
                    print('当前代理无效')
            except error.URLError as e:
                print('当前代理无效', e)
        else:
            print('未使用代理')


class unixProxy(ProxyServer):
    ''' 暂不支持， 自行配置/etc/profile '''

def cmd():
    arg = ArgumentParser(prog='xiaobaiauto2Proxy',
                         description=f'小白科技·设置系统代理·{__version__}')
    arg.add_argument('-c', '--checkproxy', type=int, default=0, choices=(0, 1),
                     help='校验代理ip是否可用，(默认)0不校验，1校验')
    arg.add_argument('-d', '--disproxy', type=str, default='localhost;127.*;192.*;10.*',
                     help='排除规则，样例：localhost;127.*;192.*;10.*')
    arg.add_argument('-e', '--enable', type=int, default=2, choices=(0, 1, 2),
                     help='0关闭代理服务器, 1启动代理服务器, (默认)2查看代理服务器状态')
    arg.add_argument('-p', '--proxy', type=str, default='127.0.0.1:8080', help='代理IP规则，样例：127.0.0.1:8080')
    par = arg.parse_args()
    wproxy = WindowsProxy()
    wproxy.proxy = par.proxy
    wproxy.disProxy = par.disproxy
    if par.checkproxy == 0:
        if par.enable == 0:
            wproxy.StopProxy()
        elif par.enable == 1:
            wproxy.StartProxy()
        else:
            wproxy.StatusProxy()
    else:
        wproxy.LiveProxy()
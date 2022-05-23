'''
Windows-Specific os_utils.

Copyright (c) 2015 - 2022 Rob "N3X15" Nelson <nexisentertainment@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
import sys
import codecs
import ctypes
from ctypes.wintypes import HWND, UINT, WPARAM, LPVOID, LPARAM

from buildtools.bt_logging import log

LRESULT = LPARAM

cmd_output = None
ENV = None
class RegistryKey(object):
    def __init__(self, hkey, key):
        log.debug('Python version: 0x%0.8X' % sys.hexversion)
        if sys.hexversion > 0x03000000:
            import winreg #IGNORE:import-error
        else:
            import _winreg as winreg #IGNORE:import-error
        self.winreg = winreg
        self.hkey = hkey
        self.key = key

        self._reg=None
        self._key=None

    def __enter__(self):
        self._reg = self.winreg.ConnectRegistry(None, self.hkey)
        self._key = self.winreg.OpenKey(self._reg, self.key, 0, self.winreg.KEY_ALL_ACCESS)
        return self

    def __exit__(self, type, value, traceback):
        self.winreg.CloseKey(self._key)
        self.winreg.CloseKey(self._reg)

    def get(self, name, default=None):
        try:
            value = self.winreg.QueryValueEx(self._key, name)[0]
        except WindowsError:
            #if default is self.NO_DEFAULT_PROVIDED:
            #    raise ValueError("No such registry key", name)
            value = default
        return value

    def set(self, name, reg_type, value):
        if value:
            self.winreg.SetValueEx(self._key, name, 0, reg_type, value)
        else:
            self.winreg.DeleteValue(self._key, name)

class WindowsEnv(object):
    """Utility class to get/set windows environment variable"""
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x1A
    NO_DEFAULT_PROVIDED = object()
    SendMessage = ctypes.windll.user32.SendMessageW
    SendMessage.argtypes = HWND, UINT, WPARAM, LPVOID
    SendMessage.restype = LRESULT

    def __init__(self, scope):
        log.debug('Python version: 0x%0.8X' % sys.hexversion)
        if sys.hexversion > 0x03000000:
            import winreg #IGNORE:import-error
        else:
            import _winreg as winreg #IGNORE:import-error
        self.winreg = winreg
        assert scope in ('user', 'system')
        self.scope = scope
        if scope == 'user':
            self.root = self.winreg.HKEY_CURRENT_USER
            self.subkey = 'Environment'
        else:
            self.root = self.winreg.HKEY_LOCAL_MACHINE
            self.subkey = 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment'

    def get(self, name, default=None):
        with RegistryKey(self.root, self.subkey) as key:
            return key.get(name, default)

    def set(self, name, value):
        with RegistryKey(self.root, self.subkey) as key:
            return key.set(name, self.winreg.REG_EXPAND_SZ, value)

    def notify(self):
        self.SendMessage(self.HWND_BROADCAST, self.WM_SETTINGCHANGE, 0, 'Environment')

def getVSVars(vspath, arch='x86', batfile=None, env=ENV):
    '''
    :param batfile:
        Location to place the batch file.
    '''
    if batfile is None:
        batfile='getvsvars.bat'
    #C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\vcvars32.bat
    with codecs.open(batfile,'w', encoding='utf-8') as f:
        f.write('@echo off\r\n')
        f.write('echo call "{}\\vcvarsall.bat" {}\r\n'.format(vspath,arch))
        f.write('call "{}\\vcvarsall.bat" {}\r\n'.format(vspath,arch))
        f.write('echo ###\r\n')
        f.write('echo INCLUDE=%INCLUDE%\r\n')
        f.write('echo LIB=%LIB%\r\n')
        f.write('echo LIBPATH=%LIBPATH%\r\n')
        f.write('echo PATH=%PATH%\r\n')
    stdout, stderr = cmd_output(['cmd', '/c', batfile], echo=True, critical=True)
    inVSVars=False
    for line in (stdout + stderr).decode('utf-8').splitlines():
        #print(line)
        if inVSVars and '=' in line:
            k,v=line.split('=',1)
            env.set(k,v,noisy=True)
        if line == '###': inVSVars=True

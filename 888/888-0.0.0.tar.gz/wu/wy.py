import os
import subprocess
import time
from subprocess import PIPE
from urllib import parse, request

import requests
# TODO:找不到win32api
# from win10toast import ToastNotifier

def getTime():
    return time.asctime( time.localtime(time.time()) )

def cmd(cmd):
    # 有点问题，自动输出到，还获取不了输出
    # return os.system(cmd)
    return os.popen(cmd).read()

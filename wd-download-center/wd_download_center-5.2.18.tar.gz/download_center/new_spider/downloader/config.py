# -*- coding: utf8 -*-
# from util.util_ping import Ping
from platform import system as system_name  # Returns the system/OS name
from os import system as system_call  # Execute a shell command


def ping(ip):
    try:
        parameters = "-n 1" if system_name().lower() == "windows" else "-c 1"
        return system_call("ping " + parameters + " " + ip + " > log.txt") == 0
    except:
        return False

# request timeout
REQUEST_TIMEOUT = 30

# IP_HOST = '127.0.0.1:9090'                       # 测试地址
IP_HOST = '182.254.155.218:9090'                   # 上線地址
# IP_HOST = '182.254.155.218:9090'                   # 上線地址

# validate_accout
VALIDATE_ACCOUNT_URL = "http://{}/download/login".format(IP_HOST)

ADD_BLACK_IP = "http://{}/download/addBlackIp"         # 添加黑名单

# sendTask
DOWNLOADER_SENDTASK = "http://{}/download/setTask"

# getResult
DOWNLOADER_GETRESULT = "http://{}/download/getResult"

TASK_SCHEDULER_IP = "http://{}/adslGetIp"

REQUEST_RETYR_SLEEP = 2     # 请求异常等待时间

REQUEST_RETYR_MAX_SLEEP = 10    # 请求异常 超過幾次 等待时间

# 内网ip
DOWNLOADER_CENTER_INNER_IP = "10.105.72.2"

DOWNLOADER_CENTER_IP = {
    "inner": "10.105.72.2",
    "outer": "182.254.155.218"
}

if ping(DOWNLOADER_CENTER_INNER_IP):
    ENVIR = 'inner'
else:
    ENVIR = 'outer'

downloader_ip = None
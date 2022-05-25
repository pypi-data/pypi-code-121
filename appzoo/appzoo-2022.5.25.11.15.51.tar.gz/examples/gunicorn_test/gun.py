#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : gunicorn
# @Time         : 2019-11-21 11:00
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : supervisor https://www.cnblogs.com/wxwgk/p/13258401.html
# https://www.jianshu.com/p/fecf15ad0c9a
import os
import re
import multiprocessing
import gevent.monkey

gevent.monkey.patch_all()

dev = True
debug = reload = dev
bind = '0.0.0.0:8000'

# 日志
loglevel = 'debug' if dev else 'info'
accesslog = "./log/access.log"
errorlog = "./log/debug.log"
pidfile = "log/gunicorn.pid"

# 启动的进程数
daemon = not dev  # 开启后台
workers = multiprocessing.cpu_count()
threads = 1
worker_class = 'gevent'  # -k gevent
x_forwarded_for_header = 'X-FORWARDED-FOR'

# if __name__ == '__main__':
#     os.system("gunicorn -c gun.py flask_app:app")

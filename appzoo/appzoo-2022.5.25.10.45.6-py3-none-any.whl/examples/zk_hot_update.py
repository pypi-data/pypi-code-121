#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : zk_hot_update
# @Time         : 2020/12/3 5:33 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

from meutils.zk_utils import *
from meutils.pipe import *

@zk.DataWatch('/mipush/nh_model')
def watcher(data, stat):  # (data, stat, event)
    ZKConfig.info = yaml.safe_load(data)
    print(ZKConfig.info)

logger.info(ZKConfig.info) # 只打印一次


def func(**kwargs):
    return ZKConfig.info


if __name__ == '__main__':
    from appzoo import App

    app = App()
    app.add_route('/', func, method="GET")

    app.run(port=8000, access_log=False)

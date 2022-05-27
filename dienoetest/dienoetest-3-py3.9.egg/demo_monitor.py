#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests,json
# content="模块告警服务：gic-order\n主机地址：10.105.224.91\n异常下线，请检查"
def demo_monitor_api(type_code,target,content):
    data={

        "typeCode":type_code,
        "target":target,
        "content":content,
    }
    headers = {
        'Content-Type': 'application/json'
    }
    res=requests.post(url='http://www.gicdev.com/monitor-web/monitor-log/deal',data=json.dumps(data),headers=headers)
    print(res.text)
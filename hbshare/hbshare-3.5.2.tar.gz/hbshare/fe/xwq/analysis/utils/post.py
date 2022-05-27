# -*- coding: utf-8 -*-

import json
import requests
import sys
import time
import traceback


def curl_request(url, method, data, request_type, max_times=30):
    """
    处理请求的函数
    :return:
    """
    vaild = False
    times = 0
    dic = None
    headers = {'Content-Type': 'application/json;charset=UTF-8',
               'Accept': 'application/json, text/plain, */*',
               'Accept-Language': 'zh-cn',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/73.0.3683.86 Safari/537.36'}
    while not vaild and times < max_times:
        try:
            if method == 'GET':
                r = requests.get(url, headers=headers)
            elif method == 'POST':
                r = requests.post(url, data=json.dumps(data), headers=headers)
            elif method == 'POST JSON':
                r = requests.post(url, json=data, headers=headers)
            else:
                r = requests.put(url, json=data, headers=headers)
            print('[Strategy][{0}] response: {1}'.format(url, r.text))
            dic = json.loads(r.text, encoding='utf-8')
            valid = True
        except Exception as e:
            exc_type, exc_value, exc_trackback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type, exc_value, exc_trackback)))
            print('[Strategy] curl request existed error: {0}'.format(request_type))
            valid = False
            times += 1
            time.sleep(30)
    return dic
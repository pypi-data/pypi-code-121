# -*- coding: utf-8 -*-
"""
@author: DrEDC
"""
import time
import requests

def tryrq(url,retry=1,wait=1,timeout=90,alt=None,request_type='get',data=None,json=None,fake_header=None):
    counter=0
    if fake_header ==0:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    else:
        headers=None
    while counter<=retry:
        if counter !=0:
            time.sleep(wait)
        try:
            if request_type=='get':
                re = requests.get(url,timeout=timeout,headers=headers)
            elif request_type=='post':
                re = requests.post(url,data=data,timeout=timeout,headers=headers,json=json)
            elif request_type=='get':
                re = requests.get(url,data=data,timeout=timeout,headers=headers,json=json)
            else:
                return 'bad request_type'
        except Exception as e:
            mes = e
            counter+=1
            if alt is not None:
                url = alt
            continue
        if re.status_code!=200:
            mes = str(re.status_code)
            counter+=1
            if alt is not None:
                url = alt
            continue
        else:
            return re
    return mes
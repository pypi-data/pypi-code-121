# -*- coding: utf-8 -*-
"""
Created by olgare on 10.09.2021

Copyright 2021 Alpes Lasers SA, Neuchatel, Switzerland
"""
__author__ = 'olgare'
__copyright__ = "Copyright 2021, Alpes Lasers SA"

from time import sleep

import requests
url = 'http://localhost:5555'
if __name__ == '__main__':
    rsp = requests.get(url + '/info')

    rsp.raise_for_status()
    print(rsp.json())
    rsp = requests.post(url + '/scan/start')
    rsp.raise_for_status()
    rsp = requests.get(url + '/info')

    rsp.raise_for_status()
    #rsp = requests.post(url + '/scan/stop')
    rsp.raise_for_status()
    rsp = requests.get(url + '/info')
    print(rsp.json())
    sleep(3.0)
    rsp = requests.get(url + '/info')

    rsp.raise_for_status()
    print(rsp.json())



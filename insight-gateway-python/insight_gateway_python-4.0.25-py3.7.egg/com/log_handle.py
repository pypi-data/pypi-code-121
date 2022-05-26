#!/usr/bin/python3
# -*- coding: utf-8 -*-
from interface.mdc_gateway_head import mdc_gateway_client

class PyLog(mdc_gateway_client.PyLog):
    def __init__(self):
        mdc_gateway_client.PyLog.__init__(self)

    def log(self,line):
        # line中已包含换行符,end='' 替换换行符
        if not str(line).__contains__("heartbeat"):
            print(line.decode(),end='')
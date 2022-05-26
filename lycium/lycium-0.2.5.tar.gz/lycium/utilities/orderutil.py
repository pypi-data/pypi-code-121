#!/usr/bin/env python3.6
#! -*- coding: utf-8 -*-

import os
import time
import math
import random

def gen_order_id(prefix=''):
    ts = time.time()
    timeval = time.strftime('%Y%m%d%H%M%S', time.localtime(ts))
    ts += random.random()
    ms = round((math.modf(ts)[0]) * 10000000000)
    return str(prefix) + timeval + str(ms)

if __name__ == '__main__':
    sn = gen_order_id('E')
    print(sn)
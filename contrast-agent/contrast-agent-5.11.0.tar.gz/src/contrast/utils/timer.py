# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import time


def now_ms_float():
    return time.time() * 1000


def now_ms():
    return int(now_ms_float())

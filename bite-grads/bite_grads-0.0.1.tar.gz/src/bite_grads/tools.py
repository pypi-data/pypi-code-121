# -*- coding: utf-8 -*-
"""

@Author: modabao
@Time: 2022/5/19 10:34
"""
import re

import pandas as pd


def parse_wrf_global_comment(str_attribute_value):
    name, value = [_.strip() for _ in str_attribute_value.split('=')]
    if value.isdigit():
        value = int(value)
    elif re.match(r'\d*\.\d*', value):
        value = float(value)
    return pd.Series([name, value], index=['name', 'value'])



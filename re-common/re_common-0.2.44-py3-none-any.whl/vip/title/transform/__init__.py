# -*- coding:utf-8 -*-
# @Time : 2021/12/2 9:38
# @Author: suhong
# @File : __init__.py.py
# @Function :

from re_common.baselibrary.utils.basetime import BaseTime


x = BaseTime().get_beijin_date_strins("%Y%m%d") + "00"
print(x)
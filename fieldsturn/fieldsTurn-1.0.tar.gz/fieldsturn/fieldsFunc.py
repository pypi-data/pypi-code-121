#!/usr/bin/python
# -*- encoding: utf-8 -*-
#@File    :   fieldsFunc.py
#@Time    :   2022/05/16 23:55:47
#@Author  :   sanwen 
#@Email:   652187661@qq.com
from fieldsturn.funCustom import * 

def fieldsFunc(func,df_data,field,**kwargs):
    """
    @description: 自定义函数
    ---------
    @param1 func: 需要执行的函数名称
    @param2 df_data: 数据源
    @param2 field:需要执行函数的字段名
    -------
    @Returns:
    -------
    """
    
    return globals().get(func)(df_data,field,**kwargs)
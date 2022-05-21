#!/usr/bin/python
# -*- encoding: utf-8 -*-
#@File    :   fieldsReplace.py
#@Time    :   2022/05/15 15:13:05
#@Author  :   sanwen 
#@Email:   652187661@qq.com

import pandas as pd 

# 字段值映射
def fieldsValueMap(df_data,fields,mode,df_value_map=None):
    """
    @description: 字段值映射
    ---------
    @param1 df_data：源数据，要求pandas类型
    @param2 fields: 需要做值映射的字段名
    @param3 df_value_map: 需要做值映射的原值与目标值的map关系
    @param4 mode: 
    -------
    @Returns:
    -------
    """

    # 处理需要做映射的值，其他值不变
    df_data[fields] = df_data[fields].apply(lambda x: df_value_map[x] if x in df_value_map.keys() else x )
    return df_data
    



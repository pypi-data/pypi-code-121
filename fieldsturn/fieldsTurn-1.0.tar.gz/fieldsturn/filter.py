#!/usr/bin/python
# -*- encoding: utf-8 -*-
#@File    :   filter.py
#@Time    :   2022/05/19 01:47:30
#@Author  :   sanwen 
#@Email:   652187661@qq.com

def fieldFilter(df_data,field,type,value):
    """
    @description: 数据筛选器
    ---------
    @param1 df_data:原数据 
    @param2 field:参与筛选字段 
    @param3 type:筛选规则
    @param4 value: 筛选值
    -------
    @Returns: 筛选后数据
    -------
    """
    if type =='等于':
        df_data = df_data[df_data[field] == value ]
    elif type =='不等于':
        df_data = df_data[df_data[field] != value ]
    elif type =='包含':
        df_data = df_data[df_data[field].str.contains(value,na=False) ]
    elif type =='不包含':
        df_data = df_data[~ df_data[field].str.contains(value,na=False) ]
    elif type =='大于':
        df_data = df_data[df_data[field] > float(value) ]
    elif type =='大于等于':
        df_data = df_data[df_data[field] >= float(value) ]
    elif type =='小于':
        df_data = df_data[df_data[field] < float(value) ]
    elif type =='小于等于':
        df_data = df_data[df_data[field] <= float(value) ]
    elif type =='为空':
        df_data = df_data[df_data[field].isnull() ]
    elif type =='不为空':
        df_data = df_data[~ df_data[field].isnull() ]
    elif type =='在...中':
        value = value.split(',')
        df_data = df_data[df_data[field].isin(value) ]       
    elif type =='不在...中':
        value = value.split(',')
        df_data = df_data[~ df_data[field].isin(value) ]  
    return df_data
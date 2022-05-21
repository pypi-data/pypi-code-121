#!/usr/bin/python
# -*- encoding: utf-8 -*-
#@File    :   fieldsTurn.py
#@Time    :   2022/05/14 03:49:32
#@Author  :   sanwen 
#@Email:   652187661@qq.com

import pandas as pd
import json 

# 字段映射
def fieldsMap(df_data,fields_map,header=1,mode ='F'):
    """
    @description:字段映射功能，只支持pandas类型数据映射
    ---------
    @param1 df_data：源数据，要求pandas类型
    @param2 fields_map：目标字段名与源字段名map表，要求json格式
    @param3 header：取第n行作为表头字段行，默认为第一行
    @param4 mode：F（弱映射，当源数据中无源字段时，目标字段为空） S（强映射，当源数据中无源字段时，报错）
    -------
    @Returns df_data_require: 字段映射结果 
    -------
    """
    # 数据初始化，将第n行转换为表头
    
    # 输入校验map表格式是否正确
    # try:
    #     df_map = json.loads(df_map)
    # except:
    #     raise Exception('映射表解析错误，请输入JSON格式数据！')
    
    # 校验需要转换的字段是否都存在源数据
    
    # 字段值替换
    # df_map = df_map[['target_sys_fields','origin_sys_fields']]
    # df_map = df_map[df_map['origin_sys_fields']!='默认值'] 

    
    # 提取需求字段
    df_data_require = pd.DataFrame(columns=list(fields_map.keys()))
    list_require = list(fields_map.keys())
    
    # 遍历需求字段，将原字段数据map过来
    for i in list_require:
        if mode == 'F':
            try:
                df_data_require[i] = df_data[fields_map[i]]
            except:
                df_data_require[i] = ''
        else:
            df_data_require[i] = df_data[fields_map[i]]
    return df_data_require 



# -*- coding: utf-8 -*-
"""
Created on Sun Jul  4 04:31:07 2021

@author: edwin
"""
import pandas as pd
import pytz

def pro_ts(ts,time_format="date",mini_digit=2):
    if isinstance(ts,str):
        ts = pd.Timestamp(ts)
    if time_format=="date":
        return ts.strftime("%Y-%m-%d")
    elif time_format=="date2":
        return ts.strftime("%Y%m%d")
    elif time_format == "week_time":
        return ts.strftime("%A, %Y-%m-%d %H:%M:%S")
    elif time_format == "week_time_CN":
        rt = ts.strftime("%A, %Y-%m-%d %H:%M:%S").replace("Monday","星期一").replace("Tuesday","星期二").replace("Wednesday","星期三").replace(
                        "Thursday","星期四").replace("Friday","星期五").replace("Saturday","星期六").replace("Sunday","星期日")
        return rt
    elif time_format == "time":
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    elif time_format == "minitime":
        return ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-(6-mini_digit)]
    elif time_format == "minitime2": #for file name
        return ts.strftime("%Y%m%d %H%M%S.%f")
    elif time_format == "time-only":
        return ts.strftime("%H:%M:%S")
    elif time_format == "minitime-only":
        return ts.strftime("%H:%M:%S.%f")[:-(6-mini_digit)]
    elif time_format == "nt":
        return ts.strftime("%Y%m%d%H%M%S%f")
    else:
        raise ValueError ("unsupported time format")
        
        
def timenow(CN_time=True):
    if CN_time:
        return pd.Timestamp.today(tz=pytz.timezone('Asia/Shanghai')).replace(tzinfo=None)
    else:
        return pd.Timestamp.today()

def get_codetype(code):
    if not isinstance(code,str) or '.' not in code:
        return 'NA' 
    elif '.CNi' in code:
        return 'index_CN'
    elif '.CNo' in code:
        return 'ETFO_CN'
    elif ('.SHb' in code or '.SZb' in code) and code[0] == '1':
        return 'CB_CN'
    else:
        if ('.SH' in code or '.SZ' in code):
            if code[0] in ['1','5']:
                return 'ETF_CN'
            else:
                if code[0] in ['0','6','3']:
                    return 'stock_A'
                if code[0] in ['2','9']:
                    return 'stock_B'
    return 'NA'
import pandas as pd
import cpca



# 字符串截取函数
def cutStr(df_data,field,**kwargs):
    if kwargs:
        a=kwargs['args'].split(',')
        df_data[field]=df_data[field].str[int(a[0]):int(a[1])]
    return df_data[field]

# 时间转日期
def timeShift(df_data,field,**kwargs):

    df_data[field]=pd.to_datetime(df_data[field])
    df_data[field] = df_data[field].dt.strftime('%Y-%m-%d')

    return df_data[field]

# 获取省市区
def addrMatch(df_data,field,**kwargs):
    try:
        df_data=cpca.transform(df_data[field])
        return df_data[kwargs['args']]
    except :
        df_data[field] = ''
        return df_data[field]

# 取负数
def reverse(df_data,field,**kwargs):
    try:
        df_data[field] = df_data[field].apply(lambda x :-x)
    except:
        pass
    return df_data[field]

# 默认值
def defaultValue(df_data,field,**kwargs):
    if kwargs:
        df_data[field] = kwargs['args']
    return df_data[field]

# 获取分组排序
def groupRank(df_data,field,**kwargs):
    '''
        需要传入分组字段
    '''
    group_field = kwargs['args']
    df_data[field] = df_data[group_field].groupby(df_data[group_field]).rank(ascending=False,method='first')
    return df_data[field]

# 取整数
def getInt(df_data,field,**kwargs):
    df_data[field]=df_data[field].apply(round)    
    return df_data[field]

# 字符串替换
def replaceValue(df_data,field,**kwargs):
    if kwargs:
        a=kwargs['args'].split(',')
        df_data[field]=df_data[field].apply(lambda x :x.replace(a[0],a[1]))
    return df_data[field]
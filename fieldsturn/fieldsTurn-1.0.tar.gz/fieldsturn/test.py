import pandas as pd
from fieldsturn.fieldsTurn import fieldsMap
from fieldsturn.fieldsReplace import fieldsValueMap
from fieldsturn.filter import fieldFilter


# 数据源
df_data = pd.read_excel(r'C:\Users\65218\Documents\WeChat Files\wxid_y7bgkjnjc00022\FileStorage\File\2022-05\苏打优选0513订单.xlsx')
df_data=fieldFilter(df_data=df_data,field='规格',type='等于',value='雾雨蓝')
print(df_data)

# # 字段映射 
df_map = pd.read_excel(r'C:\Users\65218\Desktop\新建 XLSX 工作表.xlsx')
df_map=dict(df_map.values)
print(df_map)

# # 字段值映射
df_value_map = pd.read_excel(r'C:\Users\65218\Desktop\新建 XLSX 工作表 (2).xlsx')
df_value_map =dict(df_value_map.values)
print(df_value_map)



# # 字段映射
df_data=fieldsMap(df_data,df_map)
print(df_data)

# # 字段值映射
df_data = fieldsValueMap(df_data=df_data,fields='receiver_name',mode=6,df_value_map=df_value_map)
print(df_data)
# df_data.to_csv('666.csv')

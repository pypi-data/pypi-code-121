###############################################################
# import pandas as pd
#
# # io = r'C:\Users\xuzhu\Desktop\OutK.xlsx'
# io = r'.\raw.xlsx'
# data = pd.read_excel(io, sheet_name=0)
#
# # print(data.head())
# # print(data.tail())
# # print(data.groupby(["GCH","years"]).groups)
# onedata = data.groupby('GCH').apply(lambda t: t[t.years == t.years.min()])
# print("write excel")
# with pd.ExcelWriter('temp1.xlsx') as writer:
#     onedata.to_excel(writer, sheet_name='Sheet1')

##########################################################

# import pandas as pd
#
# # io = r'C:\Users\xuzhu\Desktop\OutK.xlsx'
# io = r'.\temp1.xlsx'
# data = pd.read_excel(io, sheet_name=0)
#
# # print(data.head())
# # print(data.tail())
# # print(data.groupby(["GCH","years"]).groups)
# onedata = data.groupby('GCH').apply(lambda t: t[t.num == t.num.min()])
# print("write excel")
# with pd.ExcelWriter('temp2.xlsx') as writer:
#     onedata.to_excel(writer, sheet_name='Sheet1')

############################################################

# import pandas as pd
#
# # io = r'C:\Users\xuzhu\Desktop\OutK.xlsx'
# io = r'.\temp2.xlsx'
# data = pd.read_excel(io, sheet_name=0)
#
# def bug_rule(x):
#     gch = x.GCH
#     gch1 = gch[:-1]
#     return gch1
#
# data["gch5"] = data.apply(lambda x: bug_rule(x), axis=1)
# print("write excel")
# with pd.ExcelWriter('temp3.xlsx') as writer:
#     data.to_excel(writer, sheet_name='Sheet1')


###################################################
#
#
# import sys
#
# import pandas as pd
#
# # io = r'C:\Users\xuzhu\Desktop\OutK.xlsx'
# io = r'.\temp3.xlsx'
# io2 = r'.\raw2.xlsx'
# data = pd.read_excel(io, sheet_name=0)
# print(data.dtypes)
# print("****************")
# data2 = pd.read_excel(io2, sheet_name=1)
# print(data2.dtypes)
# data3 = pd.merge(data, data2, on='gch5')
#
# with pd.ExcelWriter('temp4.xlsx') as writer:
#     data3.to_excel(writer, sheet_name='Sheet1')

##########################################################


# import pandas as pd
#
# # io = r'C:\Users\xuzhu\Desktop\OutK.xlsx'
# io = r'.\temp4.xlsx'
# data = pd.read_excel(io, sheet_name=0)
#
# # print(data.head())
# # print(data.tail())
# # print(data.groupby(["GCH","years"]).groups)
# onedata = data.groupby('gch5').apply(lambda t: t[t.years == t.years.min()])
# print("write excel")
# with pd.ExcelWriter('temp5.xlsx') as writer:
#     onedata.to_excel(writer, sheet_name='Sheet1')

##########################################################

# import pandas as pd
#
# # io = r'C:\Users\xuzhu\Desktop\OutK.xlsx'
# io = r'.\temp5.xlsx'
# data = pd.read_excel(io, sheet_name=0)
#
# # print(data.head())
# # print(data.tail())
# # print(data.groupby(["GCH","years"]).groups)
# onedata = data.groupby('gch5').apply(lambda t: t[t.num == t.num.min()])
# print("write excel")
# with pd.ExcelWriter('temp6.xlsx') as writer:
#     onedata.to_excel(writer, sheet_name='Sheet1')

#########################################################

import pandas as pd


io = r'.\temp4.xlsx'
io2 = r'.\raw2.xlsx'
data = pd.read_excel(io, sheet_name=0)
data2 = pd.read_excel(io2, sheet_name=1)

print(type(data["刊名"]))
print(data["刊名"].values.tolist())
print(type(data2["刊名"]))
print(data2["刊名"].values.tolist())

print(set(data2["刊名"].values.tolist()) - set(data["刊名"].values.tolist()))

# onedata = data.groupby('gch5').apply(lambda t: t[t.num == t.num.min()])
# print("write excel")
# with pd.ExcelWriter('temp6.xlsx') as writer:
#     onedata.to_excel(writer, sheet_name='Sheet1')


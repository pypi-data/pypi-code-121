# 通过传入的bool值确定是否打印string
from re_common.baselibrary.utils.core.requests_core import SUCCESS, FAILED

printfunc = lambda LogBool, string: print(string) if LogBool else print("")

# 关闭r对象
closeResult = lambda r: r.close() if 'r' in locals() and r else None

# bools 传入True or False 给出对应的字符串
bools_string = lambda bools: SUCCESS if bools else FAILED

# 判断是否存在并strip()
html_strip = lambda html: html.strip() if html else html

# 根据给的字符串确认是否空,如果x == "" 给y值，否则如果x=="delete" 给"",否则给x的值
# set_value = lambda x, y: y if x == "" else "" if x == "delete" else x

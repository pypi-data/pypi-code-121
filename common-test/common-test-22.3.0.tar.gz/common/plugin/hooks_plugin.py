import datetime
import time

def exec_func(func: str) -> str:
    """执行函数(exec可以执行Python代码)
    :params func 字符的形式调用函数
    : return 返回的将是个str类型的结果
    """
    # 得到一个局部的变量字典，来修正exec函数中的变量，在其他函数内部使用不到的问题
    loc = locals()
    exec(f"result = {func}")
    return str(loc['result'])


def get_current_time():
    """获取当前时间戳"""
    return int(time.time())

def format_current_time(format: format="%Y-%m-%d %H:%M:%S"):
    """获取当前时间戳"""
    return time.strftime(format, time.localtime())


def change_date(date):
    """修改日期
    days为传的日期+n天"""
    new = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M") + datetime.timedelta(days=1)
    str_new = new.strftime("%Y-%m-%d")
    new_date = str(str_new[0:10])
    return new_date


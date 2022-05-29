import time


def get_time_str(time_float=-1):
    """获取当前时间字符串
    格式: 2021.05.17 12:20:20
    """

    if time_float == -1:
        time_float = time.time()
        assert isinstance(time_float, float)
    time_local = time.localtime(time_float)
    return time.strftime("%Y.%m.%d %H:%M:%S", time_local)

def get_time_folder():
    """获取以时间命名的文件夹名称 20210517_122020"""

    time_local = time.localtime(time.time())
    dt = time.strftime("%Y%m%d_%H%M%S", time_local)
    return dt

def get_date_str(time_float=-1):
    """ 获取日期 2021.05.17"""
    return get_time_str(time_float).split(' ')[0]

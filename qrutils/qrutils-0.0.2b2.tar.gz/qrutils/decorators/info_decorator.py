from functools import wraps

class info_decoratoer:
    def __init__(self):
        pass

def fileOperateInfo(func):
    @wraps(func)
    def info_start_end(*args, **kwargs):
        print("-----开始操作文件-----")
        func(*args, **kwargs)
        print("-----结束操作文件-----")
    return info_start_end
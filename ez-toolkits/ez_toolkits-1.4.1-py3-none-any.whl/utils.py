import time
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from os.path import basename
from pathlib import Path

# ----------------------------------------------------------------------

'''
函数内部变量, 变量名一律以 _ (下划线) 开头, 避免改变上层相同名称的变量

except 一律输出 Exception, 即:

    try:
        ...
    except Exception as e:
        print(e)
        return ...
'''

# 重命名 type, 因为某些函数的参数名称为 type
get_type = type

# ----------------------------------------------------------------------

def nums_mam(numbers=[], type=None):
    ''' 返回一组数字中的 最大值, 平均值, 最小值 '''
    _num_max, _num_avg, _num_min = None, None, None
    try:
        if get_type(numbers) == list and numbers != []:
            if type == 'int':
                numbers = [int(i) for i in numbers]
            if type == 'float':
                numbers = [float(i) for i in numbers]
            _num_max = max(numbers)
            _num_avg = sum(numbers) / len(numbers)
            _num_min = min(numbers)
        return _num_max, _num_avg, _num_min
    except Exception as e:
        print(e)
        return _num_max, _num_avg, _num_min

# ----------------------------------------------------------------------

def stat_is(target='', type='file'):
    ''' 检查目标类型 (默认: file) '''
    try:
        _stat = Path(target)
        match True:
            case True if type == 'absolute' and _stat.exists() and _stat.is_absolute():
                return True
            case True if type == 'block_device' and _stat.exists() and _stat.is_block_device():
                return True
            case True if type == 'dir' and _stat.exists() and _stat.is_dir():
                return True
            case True if type == 'fifo' and _stat.exists() and _stat.is_fifo():
                return True
            case True if type == 'file' and _stat.exists() and _stat.is_file():
                return True
            case True if type == 'mount' and _stat.exists() and _stat.is_mount():
                return True
            case True if type == 'relative_to' and _stat.exists() and _stat.is_relative_to():
                return True
            case True if type == 'reserved' and _stat.exists() and _stat.is_reserved():
                return True
            case True if type == 'socket' and _stat.exists() and _stat.is_socket():
                return True
            case True if type == 'symlink' and _stat.exists() and _stat.is_symlink():
                return True
            case _:
                return False
    except Exception as e:
        print(e)
        return False

# ----------------------------------------------------------------------

def list_sort_by_key(data=[], key=None, deduplication=False, **kwargs):
    ''' 列表排序 '''
    try:
        if type(data) == list and data != []:
            # from ipaddress import ip_address
            # _ips = [str(i) for i in sorted(ip_address(ip.strip()) for ip in ips)]
            # 注意: list.sort() 是直接改变 list, 不会返回 list
            _data = deepcopy(data)
            _data.sort(key=key, **kwargs)
            if deduplication == True:
                return list(set(_data))
            else:
                return _data
        else:
            return []
    except Exception as e:
        print(e)
        return []

def list_dict_sorted_by_key(data=[], key='', **kwargs):
    ''' 列表字典排序 '''
    try:
        return sorted(data, key=lambda x: x[key], **kwargs) if type(data) == list and data != [] and type(key) == str and key != '' else []
    except Exception as e:
        print(e)
        return []

# ----------------------------------------------------------------------

def filename(file='', split='.'):
    '''
    获取文件名称
    https://stackoverflow.com/questions/678236/how-do-i-get-the-filename-without-the-extension-from-a-path-in-python
    https://stackoverflow.com/questions/4152963/get-name-of-current-script-in-python
    '''
    try:
        if type(file) == str and file != '' and file[-1] != '/':
            _basename = basename(file)
            _index_of_dot = _basename.index(split)
            return _basename[:_index_of_dot]
        else:
            return ''
    except Exception as e:
        print(e)
        return ''

# ----------------------------------------------------------------------

def work_dir():
    ''' 获取当前目录名称 '''
    try:
        return str(Path().resolve())
    except Exception as e:
        print(e)
        return ''

def parent_dir(path=''):
    ''' 获取父目录名称 '''
    try:
        return str(Path(path).parent.resolve()) if type(path) == str and path != '' else ''
    except Exception as e:
        print(e)
        return ''

# ----------------------------------------------------------------------

def retry(times=3, func=(), *args, **kwargs):
    '''
    重试 (默认重试3次, 0表示无限重试)
    函数传递参数: https://stackoverflow.com/a/803632
    callable() 判断类型是非为函数: https://stackoverflow.com/a/624939
    '''
    _num = 0
    try:
        if callable(func) == True and type(times) == int:
            while True:
                # 重试次数判断
                if times != 0:
                    _num += 1
                    if _num > times:
                        return
                # 执行函数
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(e)
                    continue
                break
        else:
            return None
    except Exception as e:
        print(e)
        return None

# ----------------------------------------------------------------------


'''
日期时间有两种: UTC datetime (UTC时区日期时间) 和 Local datetime (当前时区日期时间)

Unix Timestamp 仅为 UTC datetime 的值

所以这里需要考虑两种情况:
- UTC datetime 和 Local datetime 转化为 Unix Timestamp 的值应该相同
- UTC datetime 和 Local datetime 转化为 Unix Timestamp 的方法应该不同
'''

def datetime_now(*args, **kwargs):
    _utc = kwargs.pop("utc", False)
    try:
        return datetime.utcnow(*args, **kwargs) if _utc == True else datetime.now(*args, **kwargs)
    except Exception as e:
        print(e)
        return None

def datetime_offset(dt=None, *args, **kwargs):
    _utc = kwargs.pop("utc", False)
    try:
        if dt == None:
            return datetime.utcnow() + timedelta(*args, **kwargs) if _utc == True else datetime.now() + timedelta(*args, **kwargs)
        elif isinstance(dt, datetime) == True:
            return dt + timedelta(*args, **kwargs)
        else:
            return None
    except Exception as e:
        print(e)
        return None

def datetime_to_string(dt, format='%Y-%m-%d %H:%M:%S'):
    try:
        return datetime.strftime(dt, format) if isinstance(dt, datetime) == True else None
    except Exception as e:
        print(e)
        return None

def datetime_to_timestamp(dt, utc=False):
    try:
        if isinstance(dt, datetime) == True:
            return int(dt.replace(tzinfo=timezone.utc).timestamp()) if utc == True else int(dt.replace().timestamp())
        else:
            return None
    except Exception as e:
        print(e)
        return None

def string_to_datetime(dt, format='%Y-%m-%d %H:%M:%S'):
    try:
        # return datetime.fromisoformat(datetime_string)
        return datetime.strptime(dt, format) if type(dt) == str else None
    except Exception as e:
        print(e)
        return None

def string_to_timestamp(dt, format='%Y-%m-%d %H:%M:%S'):
    try:
        return int(time.mktime(time.strptime(dt, format))) if type(dt) == str else None
    except Exception as e:
        print(e)
        return None

def timestamp_to_datetime(dt, format='%Y-%m-%d %H:%M:%S'):
    try:
        return datetime.fromisoformat(time.strftime(format, time.gmtime(dt))) if type(dt) == int else None
    except Exception as e:
        print(e)
        return None

def datetime_utc_to_local(dt, format='%Y-%m-%d %H:%M:%S'):
    # return dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
    # return (dt.replace(tzinfo=timezone.utc).astimezone(tz=None)).strftime(format)
    # return string_to_datetime((dt.replace(tzinfo=timezone.utc).astimezone(tz=None)).strftime(format), format)
    try:
        return datetime.fromisoformat((dt.replace(tzinfo=timezone.utc).astimezone(tz=None)).strftime(format)) if isinstance(dt, datetime) == True else None
    except Exception as e:
        print(e)
        return None

# ----------------------------------------------------------------------

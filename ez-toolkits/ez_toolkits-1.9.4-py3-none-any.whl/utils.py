import json
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from os import remove
from os.path import basename
from pathlib import Path
from shutil import rmtree
from subprocess import run
from time import mktime, strptime

from loguru import logger

# ----------------------------------------------------------------------

'''
函数内部变量, 变量名一律以 _ (下划线) 开头, 避免改变上层相同名称的变量

except 一律输出 Exception, 即:

    try:
        ...
    except Exception as e:
        logger.exception(e)
        return None
'''

# 重命名 type, 因为某些函数的参数名称为 type
get_type = type

# ----------------------------------------------------------------------

def nums_mam(numbers=[], type=None):
    ''' 返回一组数字中的 最大值, 平均值, 最小值 '''
    _numbers, _num_max, _num_avg, _num_min = None, None, None, None
    try:
        if get_type(numbers) == list and numbers != []:
            match True:
                case True if type == 'int':
                    _numbers = [int(i) for i in deepcopy(numbers)]
                case True if type == 'float':
                    _numbers = [float(i) for i in deepcopy(numbers)]
            _num_max = max(_numbers)
            _num_avg = sum(_numbers) / len(_numbers)
            _num_min = min(_numbers)
        return _num_max, _num_avg, _num_min
    except Exception as e:
        logger.exception(e)
        return None, None, None

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
        logger.exception(e)
        return False

# ----------------------------------------------------------------------

def list_sort_by_key(data=[], key=None, deduplication=False, **kwargs):
    '''
    列表排序
    https://stackoverflow.com/a/4183538
    https://blog.csdn.net/u013541325/article/details/117530957
    '''
    try:
        if type(data) == list and data != []:
            # from ipaddress import ip_address
            # _ips = [str(i) for i in sorted(ip_address(ip.strip()) for ip in ips)]
            # 注意: list.sort() 是直接改变 list, 不会返回 list
            _data = deepcopy(data)
            if deduplication == True:
                _data_deduplicated = list(set(_data))
                _data_deduplicated.sort(key=key, **kwargs)
                return _data_deduplicated
            else:
                _data.sort(key=key, **kwargs)
                return _data
        else:
            return None
    except Exception as e:
        logger.exception(e)
        return None

def list_dict_sorted_by_key(data=[], key='', **kwargs):
    '''
    列表字典排序
    https://stackoverflow.com/a/73050
    '''
    try:
        return sorted(data, key=lambda x: x[key], **kwargs) if type(data) == list and data != [] and type(key) == str and key != '' else []
    except Exception as e:
        logger.exception(e)
        return None

# ----------------------------------------------------------------------

def dict_nested_update(data, key, value):
    '''
    dictionary nested update
    https://stackoverflow.com/a/58885744
    '''
    try:
        for k, v in data.items():
            # callable() 判断是非为 function
            if (type(key) == str and key == k) or (callable(key) == True and key() == k):
                if callable(value) == True:
                    data[k] = value()
                else:
                    data[k] = value
            elif isinstance(v, dict):
                dict_nested_update(v, key, value)
            elif isinstance(v, list):
                for o in v:
                    if isinstance(o, dict):
                        dict_nested_update(o, key, value)
        return True
    except Exception as e:
        logger.exception(e)
        return False

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
            return None
    except Exception as e:
        logger.exception(e)
        return None

# ----------------------------------------------------------------------

def work_dir():
    ''' 获取当前目录名称 '''
    try:
        return str(Path().resolve())
    except Exception as e:
        logger.exception(e)
        return None

def parent_dir(path=''):
    ''' 获取父目录名称 '''
    try:
        return str(Path(path).parent.resolve()) if type(path) == str and path != '' else ''
    except Exception as e:
        logger.exception(e)
        return None

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
                    logger.exception(e)
                    continue
                break
        else:
            return None
    except Exception as e:
        logger.exception(e)
        return None

# ----------------------------------------------------------------------


'''
日期时间有两种: UTC datetime (UTC时区日期时间) 和 Local datetime (当前时区日期时间)

Unix Timestamp 仅为 UTC datetime 的值

但是, Local datetime 可以直接转换为 Unix Timestamp, UTC datetime 需要先转换到 UTC TimeZone 再转换为 Unix Timestamp

相反, Unix Timestamp 可以直接转换为 UTC datetime, 要获得 Local datetime, 需要再将 UTC datetime 转换为 Local datetime

    https://stackoverflow.com/a/13287083
    https://stackoverflow.com/a/466376
    https://stackoverflow.com/a/7999977
    https://stackoverflow.com/a/3682808
    https://stackoverflow.com/a/63920772
    https://www.geeksforgeeks.org/how-to-remove-timezone-information-from-datetime-object-in-python/

pytz all timezones

    https://stackoverflow.com/a/13867319
    https://stackoverflow.com/a/15692958

    import pytz
    pytz.all_timezones
    pytz.common_timezones
    pytz.timezone('US/Eastern')

timezone

    https://stackoverflow.com/a/39079819
    https://stackoverflow.com/a/1681600
    https://stackoverflow.com/a/4771733
    https://stackoverflow.com/a/63920772
    https://toutiao.io/posts/sin4x0/preview

其它:

    dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    (dt.replace(tzinfo=timezone.utc).astimezone(tz=None)).strftime(format)
    datetime.fromisoformat((dt.replace(tzinfo=timezone.utc).astimezone(tz=None)).strftime(format))
    string_to_datetime((dt.replace(tzinfo=timezone.utc).astimezone(tz=None)).strftime(format), format)

    datetime.fromisoformat(time.strftime(format, time.gmtime(dt)))
'''

def local_timezone():
    ''' 获取当前时区 '''
    return datetime.now(timezone.utc).astimezone().tzinfo

def datetime_now(*args, **kwargs):
    ''' 获取日期和时间 '''
    _utc = kwargs.pop("utc", False)
    try:
        return datetime.utcnow(*args, **kwargs) if _utc == True else datetime.now(*args, **kwargs)
    except Exception as e:
        logger.exception(e)
        return None

def datetime_offset(dt=None, *args, **kwargs):
    ''' 获取 向前或向后特定日期时间 的日期和时间 '''
    _utc = kwargs.pop("utc", False)
    try:
        if dt == None:
            return datetime.utcnow() + timedelta(*args, **kwargs) if _utc == True else datetime.now() + timedelta(*args, **kwargs)
        elif isinstance(dt, datetime) == True:
            return dt + timedelta(*args, **kwargs)
        else:
            return None
    except Exception as e:
        logger.exception(e)
        return None

def datetime_to_string(dt, format='%Y-%m-%d %H:%M:%S'):
    ''' 日期时间格式 转换为 字符串格式 '''
    try:
        return datetime.strftime(dt, format) if isinstance(dt, datetime) == True else None
    except Exception as e:
        logger.exception(e)
        return None

def datetime_to_timestamp(dt, utc=False):
    '''
    Datatime 转换为 Unix Timestamp
    Local datetime 可以直接转换为 Unix Timestamp
    UTC datetime 需要先替换 timezone 再转换为 Unix Timestamp
    '''
    try:
        if isinstance(dt, datetime) == True:
            return int(dt.replace(tzinfo=timezone.utc).timestamp()) if utc == True else int(dt.timestamp())
        else:
            return None
    except Exception as e:
        logger.exception(e)
        return None

def datetime_local_to_timezone(dt, tz=timezone.utc):
    '''
    Local datetime to TimeZone datetime (默认转换为 UTC datetime)
    replace(tzinfo=None) 移除结尾的时区信息
    '''
    try:
        return (datetime.fromtimestamp(dt.timestamp(), tz=tz)).replace(tzinfo=None) if isinstance(dt, datetime) == True else None
    except Exception as e:
        logger.exception(e)
        return None

def datetime_utc_to_timezone(dt, tz=datetime.now(timezone.utc).astimezone().tzinfo):
    '''
    UTC datetime to TimeZone datetime (默认转换为 Local datetime)
    replace(tzinfo=None) 移除结尾的时区信息
    '''
    try:
        return dt.replace(tzinfo=timezone.utc).astimezone(tz).replace(tzinfo=None) if isinstance(dt, datetime) == True else None
    except Exception as e:
        logger.exception(e)
        return None

def timestamp_to_datetime(ts, tz=timezone.utc):
    ''' Unix Timestamp 转换为 Datatime '''
    try:
        return (datetime.fromtimestamp(ts, tz=tz)).replace(tzinfo=None) if type(ts) == int else None
    except Exception as e:
        logger.exception(e)
        return None

def string_to_datetime(dt, format='%Y-%m-%d %H:%M:%S'):
    try:
        return datetime.strptime(dt, format) if type(dt) == str else None
    except Exception as e:
        logger.exception(e)
        return None

def string_to_timestamp(dt, format='%Y-%m-%d %H:%M:%S'):
    try:
        return int(mktime(strptime(dt, format))) if type(dt) == str else None
    except Exception as e:
        logger.exception(e)
        return None

# ----------------------------------------------------------------------


'''
run_cmd = bash('echo ok', universal_newlines=True, stdout=PIPE)

if run_cmd != None:
    returncode = run_cmd.returncode
    outputs = run_cmd.stdout.splitlines()
    print(returncode, type(returncode))
    print(outputs, type(outputs))

# echo 'echo ok' > /tmp/ok.sh
run_script = bash('/tmp/ok.sh', file=True, universal_newlines=True, stdout=PIPE)

if run_script != None:
    returncode = run_script.returncode
    outputs = run_script.stdout.splitlines()
    print(returncode, type(returncode))
    print(outputs, type(outputs))
'''

def bash(cmd=None, file=False, sh='/bin/bash', **kwargs):
    ''' run bash command or script '''
    try:
        match True:
            case True if cmd != None and type(cmd) == str and file == True and sh != None and type(sh) == str:
                return run([sh, cmd], **kwargs) if (stat_is(sh) == True and stat_is(cmd) == True) else None
            case True if cmd != None and type(cmd) == str and file == False and sh != None and type(sh) == str:
                return run([sh, "-c", cmd], **kwargs) if stat_is(sh) == True else None
            case _:
                return None
    except Exception as e:
        logger.exception(e)
        return None

# ----------------------------------------------------------------------


"""
json_raw = '''
{
    "markdown.preview.fontSize": 14,
    "editor.minimap.enabled": false,
    "workbench.iconTheme": "vscode-icons",
    "http.proxy": "http://127.0.0.1:1087"

}
'''

print(json_sort(json_raw))

{
    "editor.minimap.enabled": false,
    "http.proxy": "http://127.0.0.1:1087",
    "markdown.preview.fontSize": 14,
    "workbench.iconTheme": "vscode-icons"
}
"""
def json_sort(string='', **kwargs):
    try:
        return json.dumps(json.loads(string), indent=4, sort_keys=True, **kwargs) if type(string) == str and string != '' else None
    except Exception as e:
        logger.exception(e)
        return None

# ----------------------------------------------------------------------

def delete_files(files=None):
    ''' delete file '''
    try:

        if files != None and type(files) == str and stat_is(files) == True:

            remove(files)
            logger.success('deleted file: {}'.format(files))
            return True

        elif files != None and type(files) == list and files != []:

            for file in files:

                if type(file) == str and stat_is(file) == True:
                    try:
                        remove(file)
                        logger.success('deleted file: {}'.format(file))
                    except Exception as e:
                        logger.error('error file: {} {}'.format(file, e))
                else:
                    logger.error('error file: {}'.format(file))

            return True

        else:

            logger.error('error file: {}'.format(files))
            return False

    except Exception as e:
        logger.error('error file: {} {}'.format(files, e))
        return False

def delete_dirs(dirs=None):
    '''
    delete directory

    https://docs.python.org/3/library/os.html#os.rmdir

        os.rmdir(path, *, dir_fd=None)

    Remove (delete) the directory path.

    If the directory does not exist or is not empty, an FileNotFoundError or an OSError is raised respectively.

    In order to remove whole directory trees, shutil.rmtree() can be used.

    https://docs.python.org/3/library/shutil.html#shutil.rmtree

        shutil.rmtree(path, ignore_errors=False, onerror=None)

    Delete an entire directory tree; path must point to a directory (but not a symbolic link to a directory).

    If ignore_errors is true, errors resulting from failed removals will be ignored;

    if false or omitted, such errors are handled by calling a handler specified by onerror or, if that is omitted, they raise an exception.
    '''
    try:

        if dirs != None and type(dirs) == str and stat_is(dirs, 'dir') == True:

            rmtree(dirs)
            logger.success('deleted directory: {}'.format(dirs))
            return True

        elif dirs != None and type(dirs) == list and dirs != []:

            for dir in dirs:

                if type(dir) == str and stat_is(dir, 'dir') == True:
                    try:
                        rmtree(dir)
                        logger.success('deleted directory: {}'.format(dir))
                    except Exception as e:
                        logger.error('error directory: {} {}'.format(dir, e))
                else:
                    logger.error('error directory: {}'.format(dir))

            return True

        else:

            logger.error('error directory: {}'.format(dirs))
            return False

    except Exception as e:
        logger.error('error directory: {} {}'.format(dirs, e))
        return False

# ----------------------------------------------------------------------

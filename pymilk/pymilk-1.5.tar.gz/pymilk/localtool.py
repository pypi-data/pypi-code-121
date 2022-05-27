import hashlib
from random import choices
from datetime import datetime as datetimeSon
from math import ceil
from pathlib import Path as libpath
from os.path import abspath
from json import dumps as json_dumps
from json import loads as json_loads
from pickle import dumps as pickle_dumps
from pickle import loads as pickle_loads
from decimal import Decimal
from .toolkit.data_structures import undefined


nowdate = lambda : str(datetimeSon.now())[:10]  # -> '2021-10-24'
nowtime = lambda : str(datetimeSon.now())[:19]  # -> '2021-10-24 20:19:10'
pretty_time = lambda : f"[{nowtime()}]"      # -> '[2021-10-24 20:18:57]'

def get_md5(text):
    return hashlib.md5(text.encode(encoding='utf-8')).hexdigest()

def cut_data(data, size):
    return [data[size*(i-1): size*i] for i in range(1, ceil(len(data)/size)+1)]

def GetGroupNumber(size, i):
    '''
    组号和索引都是从1开始
        GetGroupNumber(3, 1) >>> 1
        GetGroupNumber(3, 2) >>> 1
        GetGroupNumber(3, 3) >>> 1
        GetGroupNumber(3, 4) >>> 2
    '''
    return ceil(i / size)

_WindowsPath = type(libpath(''))

def set_path(path):
    if type(path) is not _WindowsPath:
        path = libpath(path)
    return path.mkdir(parents=True, exist_ok=True)

def set_parent_path(path):
    if type(path) is not _WindowsPath:
        path = libpath(path)
    return path.parent.mkdir(parents=True, exist_ok=True)

def json_chinese(data):
    return json_dumps(data, ensure_ascii=False)

def write_json(fpath, data, ensure_ascii=False):
    set_parent_path(fpath)
    data = json_dumps(data, ensure_ascii=ensure_ascii)
    return libpath(fpath).write_text(data, encoding='utf8')

def read_json(fpath, default=undefined):
    try:
        return json_loads(libpath(fpath).read_text(encoding='utf8'))
    except Exception as e:
        if default is undefined:
            raise e
        return default

def write_pickle(fpath, data):
    set_parent_path(fpath)
    return libpath(fpath).write_bytes(pickle_dumps(data))

def read_pickle(fpath, default=undefined):
    try:
        return pickle_loads(libpath(fpath).read_bytes())
    except Exception as e:
        if default is undefined:
            raise e
        return default

def write_text(fpath, text):
    set_parent_path(fpath)
    return libpath(fpath).write_text(text, 'utf8')

def read_text(fpath, default=undefined):
    try:
        return libpath(fpath).read_text('utf8')
    except Exception as e:
        if default is undefined:
            raise e
        return default

def limit_input(prompt='', limit=None):
    if type(limit) in (list, tuple, set, dict, str):
        while True:
            user = input(prompt)
            if user in limit: return user
    elif limit is int:
        while True:
            try:
                return int(input(prompt))
            except: pass
    elif limit is float:
        while True:
            try:
                return float(input(prompt))
            except: pass
    else:
        return input(prompt)

# Python的三元表达式
# ternary(O, T, F) 比 T if O else F 可读性更好不是吗?
def ternary(obj, tv, fv):
    if obj:
        return tv
    return fv

# 把Python对象转化成可被JSON序列化的对象
# 例如：从MySQL数据库提取出来的数据，可能含有Decimal、datetimeSon等数据类型，而这些类型的数据是无法JSON化的。
def can_json(obj, force_key=False, format_time=lambda t: int(t.timestamp())):
    try:
        json_dumps(obj)
        return obj
    except:
        type_ = type(obj)
        if type_ in (list, set, tuple):
            obj = [can_json(x, force_key=force_key, format_time=format_time) for x in obj]
            if type_ in (tuple, ):
                return type_(obj)
            else:
                return obj
        elif type_ is dict:
            newobj = {}
            for k, v in obj.items():
                v = can_json(v, force_key=force_key, format_time=format_time)
                if force_key:
                    k = can_json(k, force_key=force_key, format_time=format_time)
                newobj[k] = v
            return newobj
        elif type_ is Decimal:
            return float(obj)
        elif type_ is datetimeSon:
            return format_time(obj)
        else:
            raise TypeError(f"未知的数据类型: {type_}")

def quick_iter(obj):
    for i, x in enumerate(obj): yield i, x, type(x)

def random_bytes(size):
    return bytes(choices(range(256), k=size))
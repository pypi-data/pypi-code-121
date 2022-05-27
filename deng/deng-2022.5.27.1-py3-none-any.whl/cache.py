#!/usr/bin/env python
# coding:utf-8
"""redis缓存
作者：dengqingyong
邮箱：yu12377@163.com
时间：2020-06-28
"""
import os
import sys
import json
from pathlib import Path
from typing import Union
from redis import Redis, ConnectionPool

from . import logger
from .utils import byte_to_str, get_caller_info
from .encrypt import to_decode, sum_md5
from .file import read_file_content, save_json_to_file


def get_cache_obj(db_index: int = 15):
    """获取缓存对象
    :param db_index: int, redis中数据库索引编号
    """
    if os.environ.get("REDIS_DB_CONNECT"):
        try:
            _redis = MyRedis(db_index)
        except Exception as _e:
            pass
        else:
            logger.debug(f"redis缓存初始成功！")
            return _redis

    if sys.platform == "win32":
        _target_path = Path(os.environ["USERPROFILE"])
    else:
        _target_path = Path(os.environ["HOME"])
    __cache_path__ = _target_path / "MySession.json"
    logger.warning(f"redis缓存不可用，启动本地文件缓存：{__cache_path__}")
    return MyCache(__cache_path__)


def get_redis_pool(db_index=0, max_connections=None):
    """获取redis连接池
    :param db_index: int, redis中数据库索引编号
    :param max_connections: int, 最大连接数
    """
    _connect = json.loads(to_decode(os.environ.get("REDIS_DB_CONNECT")))
    return ConnectionPool(
        host=_connect["host"],
        port=_connect["port"],
        password=_connect["pass"],
        db=db_index,
        max_connections=max_connections,
    )


def get_redis_handler(db_index=0):
    """获取redis连接
    :param db_index: int, redis中数据库索引编号
    """
    try:
        redis_obj = Redis(connection_pool=get_redis_pool(db_index))
        if redis_obj.ping():
            return redis_obj
        else:
            return None
    except Exception:
        return None


def batch_delete_key(db_index: int, name_expression: str):
    """批量删除redis key
    :param db_index: int, redis中数据库索引编号
    :param name_expression: str, key值通配符
    """
    redis = get_redis_handler(db_index)
    temp_lock_list = redis.keys(name_expression)
    if len(temp_lock_list) > 0:
        redis.delete(*temp_lock_list)


class MyRedis(Redis):
    def __init__(self, db_index=0):
        super().__init__(connection_pool=get_redis_pool(db_index))

    def batch_delete(self, name_expression):
        key_list = self.keys(name_expression)
        if len(key_list) > 0:
            self.delete(*key_list)

    def get_to_json(self, name):
        if name:
            value_raw = self.get(name)
            if value_raw:
                try:
                    user = json.loads(value_raw)
                except (TypeError, json.decoder.JSONDecodeError) as e:
                    self.delete(name)
                else:
                    return MyDict(**user)
        return None

    def set_obj(self, prefix: str, value, **kwargs):
        if isinstance(value, (dict, list, tuple)):
            value = json.dumps(value, ensure_ascii=False)
            key = prefix + sum_md5(value)
            self.set(key, value, **kwargs)
            return key
        else:
            raise TypeError("此方法只用于保存对象！")

    def push_obj(self, queue_name: str, value):
        if isinstance(value, (dict, list, tuple)):
            value = json.dumps(value, ensure_ascii=False)
            return self.rpush(queue_name, value)
        else:
            return self.rpush(queue_name, value)

    def pop_obj(self, queue_name: str):
        value = self.lpop(queue_name)
        try:
            return json.loads(value)
        except Exception as e:
            return value

    def hgetall(self, _k):
        _v = super(MyRedis, self).hgetall(_k)
        if isinstance(_v, dict):
            return {
                _k.decode("utf-8"): _v.decode("utf-8")
                for _k, _v in _v.items()
            }
        else:
            return _v

    def lpop(self, name):
        _k = super(MyRedis, self).lpop(name)
        if _k:
            return _k.decode("utf-8")
        else:
            return _k

    def keys(self, pattern='*'):
        _l = super(MyRedis, self).keys(pattern)
        if _l:
            return [_i.decode("utf-8") for _i in _l]
        else:
            return _l

    def get(self, name):
        _v = super(MyRedis, self).get(name)
        if _v:
            _v = _v.decode("utf-8")
        return _v

    def smembers(self, name):
        _l = super(MyRedis, self).smembers(name)
        if _l:
            return [_i.decode("utf-8") for _i in _l]
        else:
            return _l


class MyCache(object):
    """自定义缓存类，redis不可用时替代使用"""

    def __init__(self, cache_path: Union[Path, str]):
        self._dict = dict()
        self.cache_path = Path(cache_path)
        if self.cache_path.exists():
            cache = read_file_content(self.cache_path, encoding="utf-8", _return="json")
            if isinstance(cache, dict):
                self._dict.update(cache)
            else:
                raise ValueError(f"缓存文件内容格式错误，无法转换成python dict对象：{self.cache_path}")
        else:
            self.cache_path.touch()

    def save_cache(self):
        save_json_to_file(self._dict, self.cache_path)

    def exists(self, key: str):
        return key in self._dict

    def get(self, key: str):
        return self._dict.get(key)

    def delete(self, key: str):
        if key in self._dict:
            self._dict.pop(key)
            self.save_cache()

    def set(self, key: str, value):
        self._dict[key] = value
        self.save_cache()

    def setex(self, name, time, value):
        self._dict[name] = value
        self.save_cache()

    def hmset(self, key: str, value):
        self.set(key, value)

    def hgetall(self, key: str):
        return self.get(key)

    def hset(self, name, key=None, value=None, mapping=None):
        if key is None and not mapping:
            raise ValueError("'key'或'mapping'不能同时为空")

        items = dict()
        if key is not None:
            items[key] = value
        if mapping:
            items.update(mapping)
        self._dict[name] = items
        self.save_cache()

    def __getattr__(self, item):
        logger.warning(f"本地文件类缓存没有实现{item}方法，忽略")

        def __temp_func(*args, **kwargs):
            pass

        return __temp_func


class MyDict(dict):
    """自定义的字典类"""

    def __init__(self, *args, **kwargs):
        super(MyDict, self).__init__(*args, **kwargs)

    def __getattr__(self, item):
        return self[item]

    def __delattr__(self, item):
        del self[item]

    def __setattr__(self, key, value):
        self[key] = value


def hget(name, key, default=None, _type=None, db_index=1):
    if _type not in (None, int, float, str, bool, bytes):
        raise TypeError("_type只能是None,int,float,str,bool,bytes之一")

    redis_obj = MyRedis(db_index)
    value = redis_obj.hget(name, key)

    if value is None:
        return default

    if value and _type == bytes:
        return value

    value = byte_to_str(value)
    if _type:
        if _type == bool:
            if str(value).lower() in ("1", "true", "yes"):
                return True
            else:
                return False
        else:
            return _type(value)
    return value

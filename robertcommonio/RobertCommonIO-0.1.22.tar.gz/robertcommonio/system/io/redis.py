from typing import NamedTuple, Optional, Union, Dict, List
from datetime import datetime, timedelta, date
import json

import redis
from bson import ObjectId

from robertcommonbasic.basic.dt.utils import DATETIME_FMT_FULL, DATETIME_FMT_DATE
from robertcommonbasic.basic.error.utils import InputDataError
from robertcommonbasic.basic.log import utils as logutils
from robertcommonbasic.basic.validation import input

class RedisConfig(NamedTuple):
    HOST: str
    PORT: int
    PWD: str
    LOG_ON_ERROR: bool = False
    STRONG_TYPE: bool = False


RedisJson = Union[int, float, bool, str, List, Dict, datetime, date, ObjectId]


class JsonRedis:
    class _SimpleJsonEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.strftime(DATETIME_FMT_FULL)
            elif isinstance(obj, date):
                return obj.strftime(DATETIME_FMT_DATE)
            else:
                return json.JSONEncoder.default(self, obj)

    class _StrongTypeHelper(json.JSONEncoder):
        _PREFIX_DATETIME = "::DATETIME::"
        _PREFIX_DATE = "::DATE::"
        _PREFIX_OBJID = "::OBJID::"

        def default(self, obj):
            text_value = self._try_convert_non_json_obj(obj)
            if text_value is None:
                return json.JSONEncoder.default(self, obj)
            else:
                return text_value

        @classmethod
        def _try_convert_non_json_obj(cls, obj):
            if isinstance(obj, datetime):
                return f"{cls._PREFIX_DATETIME}" \
                       f"{obj.strftime(DATETIME_FMT_FULL)}"
            elif isinstance(obj, date):
                return f"{cls._PREFIX_DATE}{obj.strftime(DATETIME_FMT_DATE)}"
            elif isinstance(obj, ObjectId):
                return f"{cls._PREFIX_OBJID}{obj}"
            else:
                return None

        @classmethod
        def _try_convert_non_json_str(cls, s: str):
            try:
                if s is None or not isinstance(s, str):
                    return None
                if s.startswith(cls._PREFIX_DATETIME):
                    return datetime.strptime(
                        s[len(cls._PREFIX_DATETIME):], DATETIME_FMT_FULL)
                if s.startswith(cls._PREFIX_DATE):
                    dt = datetime.strptime(
                        s[len(cls._PREFIX_DATE):], DATETIME_FMT_DATE)
                    return date(dt.year, dt.month, dt.day)
                if s.startswith(cls._PREFIX_OBJID):
                    return ObjectId(s[len(cls._PREFIX_OBJID):])
                return None
            except Exception:
                logutils.log_unhandled_error()
                raise

        @classmethod
        def _obj_hook(cls, j: dict):
            assert isinstance(j, dict)
            for key, value in j.items():
                if isinstance(value, str):
                    converted = cls._try_convert_non_json_str(value)
                    j[key] = value if converted is None else converted
                elif isinstance(value, list):
                    converted_list = []
                    for item in value:
                        converted = cls._try_convert_non_json_str(item)
                        converted_list.append(
                            item if converted is None else converted)
                    j[key] = converted_list
            return j

        @classmethod
        def convert_obj_to_str(cls, obj):
            converted = cls._try_convert_non_json_obj(obj)
            if converted is None:
                converted = json.dumps(obj, ensure_ascii=False, cls=cls)
            return converted

        @classmethod
        def convert_str_to_obj(cls, s):
            converted = cls._try_convert_non_json_str(s)
            if converted is None:
                try:
                    converted = json.loads(s, object_hook=cls._obj_hook)
                except Exception:
                    logutils.log_unhandled_error()
                    raise
            return converted

    StrongTypeHelper = _StrongTypeHelper

    def __init__(self, config: RedisConfig):
        self.host = input.ensure_not_none_str('host', config.HOST)
        self.port = input.ensure_not_none_int('port', config.PORT)
        self.pwd = input.ensure_not_none_str('pwd', config.PWD)
        self._log_on_error = bool(config.LOG_ON_ERROR)
        # if _strong_type is False (default), JsonRedis tries to convert
        # various types of values to string,
        # but not vice versa. To "get" method return strong typed values,
        # set _strong_type to True.
        self._strong_type = bool(config.STRONG_TYPE)

        try:
            self._redis = redis.StrictRedis(
                host=self.host, port=self.port, password=self.pwd)
        except Exception:
            if self._log_on_error:
                logutils.log_unhandled_error()
            raise

    @property
    def conn(self):
        return self._redis

    @property
    def strong_type(self):
        return self._strong_type

    def decode_value(self, redis_value: Optional[bytes]) -> Optional[RedisJson]:
        if not redis_value:
            value = None
        elif self._strong_type:
            value = self._StrongTypeHelper.convert_str_to_obj(
                redis_value.decode())
        else:
            value = json.loads(redis_value.decode())
        return value

    def encode_value(self, value: Optional[RedisJson]) -> Optional[bytes]:
        if self._strong_type:
            redis_value = self._StrongTypeHelper.convert_obj_to_str(value)
        else:
            if value is None:
                redis_value = None
            else:
                redis_value = json.dumps(
                    value, ensure_ascii=False, cls=self._SimpleJsonEncoder)
        return redis_value

    def get(self, name: str) -> Optional[RedisJson]:
        """
        Gets a REDIS object and try to load it into JSON object.
        :param name:
        :return:
        """
        name = input.ensure_not_none_str('name', name)
        try:
            rt = self._redis.get(name)
            if rt is None:
                return None
            value = self.decode_value(rt)
            return value
        except Exception:
            if self._log_on_error:
                logutils.log_unhandled_error()
            raise

    def expire(self, name: str, expire_seconds: Union[timedelta, int]) -> bool:
        """
        Expires a redis key in specified seconds.
        :param name:
        :param expire_seconds:
        :return: True if operation succeeds. False if the key does not exist.
        """
        key = input.ensure_not_none_str('name', name)
        if not isinstance(expire_seconds, timedelta):
            expire_seconds = input.ensure_not_none_int(
                'expire_seconds', expire_seconds)
        try:
            rt: bool = self._redis.expire(key, expire_seconds)
            return rt
        except Exception:
            if self._log_on_error:
                logutils.log_unhandled_error()
            raise

    def set(self, name: str, value: RedisJson,
            expire_period: timedelta = None) -> bool:
        """
        Set a redis with a JSON object.
        Note that the object will saved in text in REDIS.
        :param name:
        :param value:
        :param expire_period:
        :return: True if operation succeeds.
                 False if the operation condition is not met
                 (e.g. due to XX, NX option).
        """
        name = input.ensure_not_none_str('name', name)
        expire_period = input.ensure_of(
            'expire_period', expire_period, timedelta)
        ex = int(expire_period.total_seconds()) if expire_period else None
        try:
            value_to_set = self.encode_value(value)
            if value_to_set is None:
                # Treat set_to_none as delete operation
                self._redis.delete(name)
                return True
            rt: bool = self._redis.set(name, value_to_set, ex=ex)
            return rt
        except Exception:
            if self._log_on_error:
                logutils.log_unhandled_error()
            raise

    def delete(self, *names: str) -> int:
        """
        Try to delete multiple keys.
        :param names:
        :return: The number of keys successfully deleted.
        """
        keys = input.ensure_list_of(
            'names', list(names), input.ensure_not_none_str)
        try:
            rt: int = self._redis.delete(*keys)
            return rt
        except Exception:
            if self._log_on_error:
                logutils.log_unhandled_error()
            raise

    def keys(self, key_pattern: str) -> List[str]:
        """
        Try to get all keys matching key pattern.
        :return:
        """
        key_pattern = input.ensure_not_none_str('key_pattern', key_pattern)
        try:
            keys_bytes = self._redis.keys(key_pattern)
            rv = [key_byte.decode() for key_byte in keys_bytes]
            return rv
        except Exception:
            if self._log_on_error:
                logutils.log_unhandled_error()
            raise

    def hset(self, name: str, key: str, value: RedisJson) -> bool:
        name = input.ensure_not_none_str('name', name)
        key = input.ensure_not_none_str('key', key)

        try:
            redis_value = self.encode_value(value)
            rt: bool = bool(self._redis.hset(name, key, redis_value))
            return rt
        except Exception:
            if self._log_on_error:
                logutils.log_unhandled_error()
            raise

    def hmset(self, name: str, hash_map: Dict[str, RedisJson]) -> bool:
        name = input.ensure_not_none_str('name', name)
        if not isinstance(hash_map, dict):
            raise InputDataError(f"hash_map is not a dict, but {hash_map}")
        try:
            encoded_hash_map = {hash_key: self.encode_value(hash_value)
                                for hash_key, hash_value in hash_map.items()}
            rt: bool = bool(self._redis.hmset(name, encoded_hash_map))
            return rt
        except Exception:
            if self._log_on_error:
                logutils.log_unhandled_error()
            raise

    def hgetall(self, name: str) -> Dict[str, RedisJson]:
        name = input.ensure_not_none_str('name', name)
        try:
            rt = self._redis.hgetall(name)
            # An empty dict is returned if `name` does not exist
            assert rt is not None
            value = {k.decode(): self.decode_value(v) for k, v in rt.items()}
            return value
        except Exception:
            if self._log_on_error:
                logutils.log_unhandled_error()
            raise

    def hmget(self, name: str, keys: List[str]) -> List[Optional[RedisJson]]:
        name = input.ensure_not_none_str('name', name)
        keys = input.ensure_not_none_list_of(
            'keys', keys, input.ensure_not_none_str)
        try:
            rt = self._redis.hmget(name, keys)
            # An empty list is returned if `name` does not exist
            assert rt is not None
            values = [self.decode_value(v) for v in rt]
            return values
        except Exception:
            if self._log_on_error:
                logutils.log_unhandled_error()
            raise
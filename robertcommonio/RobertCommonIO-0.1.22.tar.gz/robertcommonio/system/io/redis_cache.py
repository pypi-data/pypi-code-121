from datetime import datetime, timedelta

from .redis import JsonRedis

class RedisCache:
    __CACHE__ = {}

    @staticmethod
    def load(redis: JsonRedis, func_name: str, name: str, expires: float = 60 * 60 * 2, decode=True):

        subkey = (redis.host, redis.port, func_name)
        data = RedisCache.__load_cache(name, subkey)
        if not data:
            data = RedisCache.__load_redis(redis, func_name, name, decode)
            if data:
                RedisCache.__set_cache(name, subkey, data, expires)

        return data

    @staticmethod
    def load_hm(redis: JsonRedis, name: str, args=(), expires: float = 60 * 60 * 2, decode=True):
        subkey = (redis.host, redis.port, 'hmget') + \
            tuple(args)
        data = RedisCache.__load_cache(name, subkey)
        if not data:
            data = RedisCache.__load_redis(
                redis, 'hmget', name,  decode, list(args))
            if data:
                RedisCache.__set_cache(name, subkey, data, expires)

        return data

    @staticmethod
    def reset(name: str):
        RedisCache.__CACHE__.pop(name, None)

    @staticmethod
    def clear():
        RedisCache.__CACHE__.clear()

    @staticmethod
    def __load_cache(name: str, subkey):
        values = RedisCache.__CACHE__.get(name, None)
        if values is None:
            values = {}
            RedisCache.__CACHE__[name] = values

        v = values.get(subkey)
        if v and v['expires'] > datetime.now():
            return v['data']

        return None

    @staticmethod
    def __set_cache(name: str, subkey, data, expires: float):
        values = RedisCache.__CACHE__.get(name, None)
        if values is None:
            values = {}
            RedisCache.__CACHE__[name] = values

        values[subkey] = {
            'data': data,
            'expires': datetime.now() + timedelta(seconds=expires)
        }

    @staticmethod
    def __load_redis(redis: JsonRedis, func_name: str, name: str, decode: bool, *args):
        m = getattr(redis if decode else redis.conn, func_name, None)
        if not m:
            raise ValueError(f'invalid redis method name: {func_name}')
        return m(name, *args)
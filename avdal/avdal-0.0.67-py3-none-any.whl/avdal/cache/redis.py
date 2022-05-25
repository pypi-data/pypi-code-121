import redis
from . import Cache


class RedisCache(Cache):
    def __init__(self, host, port, pwd):
        self.host = host
        self.port = port
        self.client = redis.Redis(host=self.host, port=self.port, password=pwd)

    def incr(self, key, amount=1):
        return self.client.incr(key, amount)

    def set(self, key, value, ttl=None):
        self.client.set(key, value, ttl)

    def get(self, key):
        return self.client.get(key)

import redis

#from dequeapp.deque_environment import REDIS_URL

class RedisServices:

    def __init__(self):
        pass

    @classmethod
    def get_redis_connection(cls):

        re = redis.from_url(url=cls.get_redis_url())
        return re

    @classmethod
    def get_redis_url(cls):

        return "redis://localhost:6379"


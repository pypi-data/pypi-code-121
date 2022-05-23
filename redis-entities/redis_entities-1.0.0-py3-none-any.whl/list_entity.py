from src.base_entity import BaseRedisEntity


class RedisListEntity(BaseRedisEntity):

    @classmethod
    def lpush(cls, identifier, *values):
        cls.redis_client.lpush(cls.key_name(identifier), *values)

    @classmethod
    def brpop(cls, identifier, timeout=0):
        return cls.redis_client.brpop(cls.key_name(identifier), timeout=timeout)

    @classmethod
    def get(cls, identifier, index):
        return cls.redis_client.lindex(cls.key_name(identifier), index)

    @classmethod
    def length(cls, identifier):
        return cls.redis_client.llen(cls.key_name(identifier))

    @classmethod
    def clear(cls, identifier):
        return cls.redis_client.delete(cls.key_name(identifier))


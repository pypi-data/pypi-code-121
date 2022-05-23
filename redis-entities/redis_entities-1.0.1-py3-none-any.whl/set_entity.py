from src.base_entity import BaseRedisEntity


class RedisSetEntity(BaseRedisEntity):

    @classmethod
    def add(cls, identifier, *values):
        cls.redis_client.sadd(cls.key_name(identifier), *values)

    @classmethod
    def delete(cls, identifier, *values):
        cls.redis_client.srem(cls.key_name(identifier), *values)

    @classmethod
    def clear(cls, identifier):
        cls.redis_client.delete(cls.key_name(identifier))

    @classmethod
    def exists(cls, identifier, value):
        return bool(cls.redis_client.sismember(cls.key_name(identifier), value))

    @classmethod
    def list_all(cls, identifier):
        return cls.redis_client.smembers(cls.key_name(identifier))

    @classmethod
    def length(cls, identifier):
        return cls.redis_client.scard(cls.key_name(identifier))


from src.parameters import require_string


class BaseRedisEntity:
    redis_client = None
    Prefix = ""
    Expire = None

    @classmethod
    def key_name(cls, identifier):
        return f"{cls.Prefix}:{require_string(identifier)}"

    @classmethod
    def add_expiration(cls, identifier):
        if isinstance(cls.Expire, int) and cls.Expire >= 0:
            cls.redis_client.expire(cls.key_name(identifier), cls.Expire)



import time
from src.base_entity import BaseRedisEntity
from src.secure_integrity_entity import SecureIntegrityEntity
from src.parameters import require_string, require_bytes, b2timestamp, timestamp2b


class RedisHashmapEntity(BaseRedisEntity):
    """
    This class represents a HashMap that is stored in Redis.
    The HashMap is identified by a Prefix that specifies the name of the HashMap.
    A HashMap entry is identified by the Prefix and a unique identifier.
    The RedisHashmapEntity stores and loads all HashMap keys as strings, and all HashMap values as bytes.
    """

    Contents = {}

    @staticmethod
    def _to_kwargs_dict(kwargs_dict):
        return {
            require_string(key): require_bytes(value, int_to_string=True)
            for key, value in kwargs_dict.items()
        }

    @classmethod
    def store(cls, identifier, **kwargs):
        kwargs = cls._to_kwargs_dict(kwargs)
        for keyword_arg in cls.Contents:
            if keyword_arg not in kwargs:
                raise AttributeError(
                    f"Key={keyword_arg} not specified. Please specify it through an keyword argument."
                )
        cls.redis_client.hset(cls.key_name(identifier), mapping=kwargs)
        cls.add_expiration(identifier)
        return cls(identifier, **kwargs)

    @classmethod
    def exists(cls, identifier):
        return cls.redis_client.exists(cls.key_name(identifier)) == 1

    @classmethod
    def load(cls, identifier):
        return cls(
            identifier,
            **cls._to_kwargs_dict(cls.redis_client.hgetall(cls.key_name(identifier))),
        )

    @classmethod
    def length(cls, identifier):
        return cls.redis_client.hlen(cls.key_name(identifier))

    @classmethod
    def delete(cls, identifier):
        return cls.redis_client.delete(cls.key_name(identifier))

    def __init__(self, identifier, **kwargs):
        self.identifier = identifier
        self.items = kwargs
        self._enforce_valid_entity()

    def __getattr__(self, item):
        if item in self.items:
            return self.items.get(item)
        raise AttributeError("Item not Found")

    def __delattr__(self, item):
        if item in self.items:
            self.items.pop(item)

    def _enforce_valid_entity(self):
        for keyword in self.Contents:
            if not hasattr(self, keyword):
                raise AttributeError(f"Key={keyword} not contained in Entity")


class RedisSecureHashmapEntity(RedisHashmapEntity):
    """
    This class is a thin wrapper around the SecureIntegrityEntity, to provide a Redis Hashmap with
    integrity protection. To use it, simply inherit from RedisSecureHashmapEntity instead of RedisHashmapEntity.
    """

    HMACKey = b""

    class SecureIntegrityEntityInformation:
        @classmethod
        def from_secure_integrity_entity(cls, secure_entity):
            return cls(secure_entity.creation_timestamp,  secure_entity.identifier,
                       secure_entity.identifier_hash, secure_entity.salt, secure_entity.mac)

        def __init__(self, creation_timestamp, identifier, identifier_hash, salt, mac):
            self.creation_timestamp = creation_timestamp
            self.identifier = identifier
            self.identifier_hash = identifier_hash
            self.salt = salt
            self.mac = mac

    @classmethod
    def store(cls, identifier, **kwargs):
        salt = kwargs.pop("salt", b"")
        secure_entity = SecureIntegrityEntity.create(
            cls.HMACKey,
            cls.Expire,
            identifier,
            *kwargs.values(),
            salt=salt,
        )
        secure_entity_information = RedisSecureHashmapEntity.SecureIntegrityEntityInformation.\
            from_secure_integrity_entity(secure_entity)
        kwargs["ExpireInterval"] = timestamp2b(cls.Expire)
        kwargs["CreationTimestamp"] = timestamp2b(secure_entity.creation_timestamp)
        kwargs["HMAC"] = secure_entity.mac
        return (
            super().store(secure_entity.identifier_hash.hex(), **kwargs),
            secure_entity_information,
        )

    @classmethod
    def length(cls, identifier, salt=None):
        identifier_hash = SecureIntegrityEntity.hash_identifier(identifier, salt=salt)
        return super().length(identifier_hash.hex())

    @classmethod
    def exists(cls, identifier, salt=None):
        identifier_hash = SecureIntegrityEntity.hash_identifier(identifier, salt=salt)
        return super().exists(identifier_hash.hex())

    @classmethod
    def load(cls, identifier, salt=None):
        identifier_hash = SecureIntegrityEntity.hash_identifier(identifier, salt=salt)
        obj = super().load(identifier_hash.hex())
        if not hasattr(obj, "ExpireInterval"):
            return obj
        expire_interval = obj.ExpireInterval
        creation_timestamp = obj.CreationTimestamp
        mac = obj.HMAC
        extra_args = [getattr(obj, keyword_arg) for keyword_arg in cls.Contents]
        SecureIntegrityEntity.verify_mac(
            cls.HMACKey,
            creation_timestamp,
            expire_interval,
            identifier_hash,
            mac,
            *extra_args,
            salt=salt,
        )
        if int(time.time()) - b2timestamp(creation_timestamp) > b2timestamp(
            expire_interval
        ):
            return cls(identifier)
        del obj.ExpireInterval
        del obj.CreationTimestamp
        del obj.HMAC
        return obj

    @classmethod
    def delete(cls, identifier, salt=None):
        identifier_hash = SecureIntegrityEntity.hash_identifier(identifier, salt=salt)
        return super().delete(identifier_hash.hex())

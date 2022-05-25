try:
    import aioredis

    from dropland.storages.redis.engine import EngineConfig, RedisStorageBackend, RedisStorageEngine
    from dropland.storages.redis.connections import ConnectionManager
    from dropland.storages.redis.model import SimpleRedisModelBase as SimpleRedisModel, \
        HashRedisModelBase as HashRedisModel
    from dropland.storages.redis.settings import RedisSettings

    USE_REDIS = True

except ImportError:
    USE_REDIS = False

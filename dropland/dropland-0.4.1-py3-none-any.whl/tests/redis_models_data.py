from dropland.storages.redis import USE_REDIS

if USE_REDIS:
    from dropland.storages.containers import default_redis_storage
    from dropland.storages.redis import EngineConfig

from tests import REDIS_URI

if USE_REDIS:
    redis_engine = default_redis_storage.create_engine('dropland', EngineConfig(url=REDIS_URI))

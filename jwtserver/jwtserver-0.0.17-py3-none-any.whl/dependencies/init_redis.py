import aioredis
from jwtserver import settings

settings = settings.get_settings()


def create_pool_redis():
    pool = aioredis.ConnectionPool.from_url(
        settings.redis.redis_dsn,
        max_connections=settings.redis.max_connections,
        decode_responses=True,
    )
    redis = aioredis.Redis(connection_pool=pool)
    return redis


def redis_conn():
    r = create_pool_redis().client()
    try:
        yield r
    finally:
        r.close()

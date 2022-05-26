import aioredis


class Redis:
    def __init__(self, **kwargs):
        self.host = kwargs.get('host') or 'localhost'
        self.port = kwargs.get('port') or 6379
        self.password = kwargs.get('password')
        self.db = kwargs.get('db') or 1
        self.pool_size = kwargs.get('pool_size') or 10
        self.user = kwargs.get('user')

    async def get_redis(self, pool_size=None):
        if pool_size and isinstance(pool_size, int):
            self.pool_size = pool_size
        pool = aioredis.ConnectionPool.from_url(f"redis://{self.host}", port=int(self.port), username=self.user, password=self.password,
                                                db=int(self.db), max_connections=int(self.pool_size))
        redis = aioredis.Redis(connection_pool=pool)
        return redis


__all__ = Redis

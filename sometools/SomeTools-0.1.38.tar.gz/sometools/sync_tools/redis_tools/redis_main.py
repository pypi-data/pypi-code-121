from redis import StrictRedis, ConnectionPool
from sometools.sync_tools.base import Base


class RedisMixIn(Base):
    def __init__(self, *args, **kwargs):
        super(RedisMixIn, self).__init__(*args, **kwargs)

    def get_sync_redis_conn(self, **kwargs):
        print(f'sync redis connection pool init...')
        self.redis_host = kwargs.get('redis_host')
        self.redis_port = kwargs.get('redis_port')
        self.redis_db = kwargs.get('redis_db')
        self.redis_pwd = kwargs.get('redis_pwd')
        if self.redis_pwd:
            pool = ConnectionPool(host=self.redis_host, port=self.redis_port, password=self.redis_pwd, db=self.redis_db,
                                  decode_responses=True)
        else:
            pool = ConnectionPool(host=self.redis_host, port=self.redis_port, db=self.redis_db, decode_responses=True)
        return StrictRedis(connection_pool=pool)
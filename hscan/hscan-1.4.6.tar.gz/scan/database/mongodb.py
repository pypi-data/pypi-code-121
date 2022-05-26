from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection


class MongoDB:
    def __init__(self, **kwargs):
        self.host = kwargs.get('host') or 'localhost'
        self.port = kwargs.get('port') or 6379
        self.user = kwargs.get('user') or 'admin'
        self.password = kwargs.get('password') or 'admin'
        self.auth_db = kwargs.get('auth_db') or 'admin'
        self.client = None

    def create_client(self) -> AsyncIOMotorClient:
        if not self.user:
            c = AsyncIOMotorClient(self.host, self.port)
        else:
            url = f'mongodb://{self.user}:{self.password}@{self.host}:{self.port}/?authSource={self.auth_db}'
            c = AsyncIOMotorClient(url)
        return c

    def db(self, db_name) -> AsyncIOMotorDatabase:
        if not self.client:
            self.client = self.create_client()
        db = self.client[db_name]
        return db

    def collection(self, db_name, coll_name) -> AsyncIOMotorCollection:
        db = self.db(db_name)
        coll = db[coll_name]
        return coll


__all__ = MongoDB






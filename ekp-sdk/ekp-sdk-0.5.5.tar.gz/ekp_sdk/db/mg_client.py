from decouple import config
from pymongo import MongoClient

MONGO_URI = config('MONGO_URI', default='mongodb://localhost:27017/')
MONGO_DB_NAME = config('MONGO_DB_NAME', default='dalarnia')


class MgClient:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        print("👍 Connected to MongoDb")

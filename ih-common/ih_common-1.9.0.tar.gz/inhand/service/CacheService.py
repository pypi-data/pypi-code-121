from redis import StrictRedis
import sys

sys.path.append('../../')
from inhand.service.SettingService import Redis
from inhand.service.IHException import ErrorCodeException

class CacheService:
    def __init__(self,settings):
        self.settings = settings

    def connect(self):
        pass

    def close(self):
        pass

    def put(self,key,value,expire=None):
        raise (NameError, "Unsupported!")

    def get(self, key):
        raise (NameError, "Unsupported!")

    def exists(self, key):
        raise (NameError, "Unsupported!")

    @staticmethod
    def createCacheService(settings):
        if isinstance(settings,Redis):
            return RedisCacheService(settings)
        else:
            raise (NameError, "Unsupported cache type: {}".format(database.type))

class RedisCacheService(CacheService):

    def __init__(self,settings):
        super().__init__(settings)
        self.cache=StrictRedis(host=settings.host,
                             port=settings.port,
                             db=settings.database,
                             password=settings.password)

    def put(self,key,value,expire=None):
        if expire is not None:
            self.cache.setex(key,expire,value)
        else:
            self.cache.set(key,value)

    def get(self, key):
        if self.exists(key):
            return  self.cache.get(key)
        else:
            raise ErrorCodeException(404,"no such key")

    def exists(self, key):
        return self.cache.exists(key)
"""
Store
-----

Interface to the key-value store backends such as Redis and Elastic
Search.

"""
import json
import redis
import traceback
import logging

logger = logging.getLogger("app")


class BackendBase(object):
    """
    Base class to handle KV store interface
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the db object

        Args:
            config (dict): Configuration
        """
        self.config = kwargs.pop("config", {})

    def connect(self):
        """
        Initialize the connection to the backend
        """
        pass

    def post(self, key, value):
        """
        Post a kv combination to the backend

        Args:
            key (str): key
            value (dict): document to the posted
        """
        raise Exception("Not implemented")

    def get(self, key):
        """
        Lookup a key at the backend

        Args:
            key (str): key
        """
        raise Exception("Not implemented")


class RedisBackend(BackendBase):
    """
    Redis Backend

    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the db object. Pass redis
        connection parameters as 'params'
        attribute in the config.

        Args:
            config (dict): Configuration
        """
        super().__init__(*args, **kwargs)
        self.r = None

    def connect(self):
        """
        Connect to Redis backend
        """
        params = self.config.get("params", {})
        self.r = redis.Redis(**params)

    def get(self, key):
        """
        Lookup a key at the backend

        Args:
            key (str): key
        """
        try:
            result = self.r.get(key)
            if result is None:
                return {}
            return json.loads(result.decode("utf-8"))
        except:
            traceback.print_exc()
            return {}

    def post(self, key, value):
        """
        Post a kv combination to the backend. If value
        is not a string, then it is serialized using
        json

        Args:
            key (str): key
            value (dict): document to the posted
        """
        try:
            if not isinstance(value, str):
                result = json.dumps(value)
            self.r.set(key, result)
        except:
            logger.exception("Unable to post to redis server")
            raise

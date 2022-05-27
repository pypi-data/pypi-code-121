from typing import ClassVar, AnyStr, ByteString, Union, Dict, Any
from urllib.parse import urlparse

import redis

from offline_model_builder.utils import encode_string


class RedisConnection:

    def __init__(
            self,
            host: str,
            port: int,
            db: int,
            username: str,
            password: str
    ):
        self.host = host
        self.port = port
        self.db = db
        self.username = username
        self.password = password
        self.pool = redis.ConnectionPool(
            host=self.host,
            port=self.port,
            db=self.db,
            username=self.username,
            password=self.password
        )
        self.conn = redis.StrictRedis(self.pool)

    @property
    def get_host(self) -> str:
        """Get current host
        :return: string host
        """
        return self.host

    @property
    def get_port(self) -> int:
        """Get current port redis
        :return: int port
        """
        return self.port

    def set_db(
            self,
            db: int,
    ) -> bool:
        """Set redis db selected
        :param db: int db eg: 0, 1, 2, 3, 4, 5 ...
        :return: none
        """
        self.db = db
        return True

    @property
    def get_db(self) -> int:
        """Get current db selected
        :return: int db selected
        """
        return self.db

    @property
    def get_username(self) -> str:
        """Get current username
        :return: string username
        """
        return self.username

    @property
    def get_password(self) -> str:
        """Get current password
        :return: string password
        """
        return self.password

    @property
    def get_credential(self) -> Dict[str, Any]:
        """Get current credential to connect to redis
        :return: dictionary value
        """
        return {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "username": self.username,
            "password": self.password,
        }

    def __str__(self):
        return "RedisConnection({}, {}, {}, {}, {})".format(
            self.host,
            self.port,
            self.db,
            self.username,
            self.password,
        )

    @classmethod
    def from_uri(
            cls,
            uri: str
    ) -> ClassVar:
        """Create object connection class from uri
        this will receive uri like this:
            redis://example:secret@localhost:6379/0
        :param uri: string redis uri
        :return: class object
        """
        p = urlparse(uri)
        return cls(p.hostname, p.port, int(p.path[1:]), p.username, p.password)

    def get(
            self,
            key: str
    ) -> Union[ByteString, AnyStr, int, float, None]:
        """Get value from specified key
        :param key: string key
        :return: it can be string bytes string, int or float
        """
        hash_key = encode_string(key)
        v = self.conn.get(hash_key)
        # if any value from it then decode to utf 8, cause default data type is bytes
        if v is not None and len(v) > 0:
            return v.decode("utf-8")

        return None

    def set(
            self,
            key: str,
            value: Union[ByteString, AnyStr, int, float],
            ttl: int = 60 * 10,
    ) -> bool:
        """Save data to redis by specified keys
        :param key: string key
        :param value: it can be bytes string, string, int or float
        :param ttl: default value for time to live
        :return: boolean (true, false)
        """
        hash_key = encode_string(key)
        return self.conn.set(hash_key, value, ex=ttl)

import os
import json
import socket
import logging
import redis
from typing import Dict, Optional, Tuple
from ewokscore.events import send_events
from ewokscore.logging_utils.handlers.connection import ConnectionHandler
from ewokscore.events.handlers import EwoksEventHandlerMixIn


RedisRecordType = Tuple[str, Dict[str, str]]


class RedisEwoksEventHandler(EwoksEventHandlerMixIn, ConnectionHandler):
    # TODO: https://redisql.redbeardlab.com/blog/python/using-redisql-with-python/

    def __init__(self, url: str):
        """An example is "redis://localhost:10003?db=2"."""
        self._redis_url = url
        super().__init__()

    def _connect(self, timeout=1) -> None:
        """This is called when no connection exists."""
        client_name = f"ewoks:writer:{socket.gethostname()}:{os.getpid()}"
        self._connection = redis.Redis.from_url(
            self._redis_url, client_name=client_name
        )

    def _disconnect(self) -> None:
        """This is called when a connection exists and is connected."""
        self._connection.close()

    def _serialize_record(self, record: logging.LogRecord) -> RedisRecordType:
        """Convert a record to something that can be given to the connection."""
        job_id = getattr(record, "job_id", None)
        value = {field: self.get_value(record, field) for field in send_events.FIELDS}
        return job_id, value

    @staticmethod
    def get_value(record, field) -> Optional[str]:
        value = getattr(record, field, None)
        return json.dumps(value)

    def _send_serialized_record(self, srecord: RedisRecordType):
        """Send the output from `_serialize_record` to the connection."""
        job_id, value = srecord
        n = self._connection.incrby("ewoks_events_count")
        key = f"ewoks:{job_id}:{n}"
        self._connection.hset(key, mapping=value)

import logging

from jsoncfg.value_mappers import require_string, require_dict

logger = logging.getLogger(__name__)


class PeekFileConfigSqlAlchemyMixin:
    @property
    def dbConnectString(self):
        default = "postgresql://peek:PASSWORD@127.0.0.1/peek"
        with self._cfg as c:
            return c.sqlalchemy.connectUrl(default, require_string)

    @property
    def dbEngineArgs(self):
        default = {
            "echo": False,  # Print every SQL statement executed
            "pool_size": 20,  # Number of connections to keep open
            "max_overflow": 50,
            # Number that the pool size can exceed when required
            "pool_timeout": 60,  # Timeout for getting conn from pool
            "pool_recycle": 600,  # Reconnect?? after 10 minutes
            "executemany_mode": "batch"
            # This supersedes 'use_batch_mode': True,
        }
        with self._cfg as c:
            val = c.sqlalchemy.engineArgs(default, require_dict)
            # Upgrade depreciated psycopg setting.
            if val.get("use_batch_mode") == True:
                del val["use_batch_mode"]
                val["executemany_mode"] = "batch"
                c.sqlalchemy.engineArgs = val

            return val

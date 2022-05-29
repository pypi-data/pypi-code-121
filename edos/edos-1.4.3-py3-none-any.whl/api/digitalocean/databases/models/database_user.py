import dataclasses
from typing import Optional

from edos.api.digitalocean.databases.models.settings import MysqlSettings


@dataclasses.dataclass
class DatabaseUser:
    name: str
    role: str
    password: str
    mysql_settings: Optional[MysqlSettings] = None

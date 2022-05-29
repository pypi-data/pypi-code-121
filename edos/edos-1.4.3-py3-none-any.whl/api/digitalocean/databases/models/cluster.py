import dataclasses
from datetime import datetime
from typing import Optional

from edos.api.digitalocean.databases.models.connections import DatabaseConnection
from edos.api.digitalocean.databases.models.database import Database
from edos.api.digitalocean.databases.models.database_user import DatabaseUser


@dataclasses.dataclass
class DatabaseCluster:
    id: str
    name: str
    engine: str
    version: str
    num_nodes: int
    size: str
    region: str
    status: str
    created_at: datetime
    private_network_uuid: str
    tags: Optional[list[str]]
    db_names: Optional[list[Database]]
    connection: DatabaseConnection
    privateConnection: DatabaseConnection
    users: Optional[list[DatabaseUser]]

from edos.api.digitalocean.databases.models.cluster import DatabaseCluster
from edos.api.digitalocean.databases.models.connections import DatabaseConnection
from edos.api.digitalocean.databases.models.database import Database
from edos.api.digitalocean.databases.models.database_user import DatabaseUser


def parse_one_cluster(cluster: dict) -> DatabaseCluster:
    return DatabaseCluster(
        id=cluster.get("id"),
        name=cluster.get("name"),
        engine=cluster.get("engine"),
        version=cluster.get("version"),
        num_nodes=int(cluster.get("num_nodes", 0)),
        size=cluster.get("size"),
        region=cluster.get("region"),
        status=cluster.get("status"),
        created_at=cluster.get("created_at"),
        private_network_uuid=cluster.get("private_network_uuid"),
        tags=cluster.get("tags", None),
        db_names=[
            Database(db)
            for db in (
                cluster.get("db_names", []) if cluster.get("db_names", []) else []
            )
        ],
        connection=parse_one_connection(cluster.get("connection")),
        privateConnection=parse_one_connection(cluster.get("private_connection")),
        users=[
            parse_one_user(user)
            for user in (cluster.get("users", []) if cluster.get("users", []) else [])
        ],
    )


def parse_one_database(database: dict) -> Database:
    return Database(name=database.get("name"))


def parse_one_user(user: dict) -> DatabaseUser:
    return DatabaseUser(
        name=user.get("name"),
        role=user.get("role"),
        password=user.get("password"),
    )


def parse_one_connection(connection: dict) -> DatabaseConnection:
    return DatabaseConnection(
        uri=connection.get("uri"),
        database=connection.get("database"),
        host=connection.get("host"),
        port=int(connection.get("port")),
        user=connection.get("user"),
        password=connection.get("password"),
        ssl=connection.get("ssl"),
    )

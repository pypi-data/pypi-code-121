from edos.api.digitalocean.databases.api import DatabaseApi
from edos.api.digitalocean.databases.models.cluster import DatabaseCluster
from edos.api.digitalocean.databases.models.database import Database
from edos.api.digitalocean.databases.models.database_user import DatabaseUser
from edos.exceptions import DatabaseCreationError, DatabaseEngineNotSupported


class DatabaseService:
    def __init__(self):
        self.api = DatabaseApi()

    def get_clusters(self) -> dict[str, str]:
        """
        :return: {cluster_id, cluster_name}
        """
        clusters = self.api.get_clusters()
        res = {}
        for cluster in clusters:
            res[cluster.id] = cluster.name
        return res

    def get_cluster(self, cluster_id: str) -> DatabaseCluster:
        return self.api.get_one_cluster(cluster_id)

    def get_databases(self, cluster_id: str) -> list[str]:
        """
        :param cluster_id: cluster where is database stored
        :return: list of database names
        """
        databases = self.api.get_databases(cluster_id)
        return [db.name for db in databases]

    def get_database(self, cluster_id: str, database_name: str) -> Database:
        return self.api.get_database(cluster_id, database_name)

    def create_database(self, cluster_id: str, project_name: str) -> str:
        """
        this command creates a database and user

        so this command will be doing this:
            - creates a database
            - creates a database user
            - get cluster
            - create db_url from private connection from cluster
                and database user/password

        In case, that create user fail, you must delete database, for consistency

        :param cluster_id: cluster where database will be stored
        :param project_name: name of database and user
        :return: database url for secrets
        """
        database = self.api.create_database(cluster_id, project_name)
        try:
            user = self.api.create_database_user(cluster_id, project_name)
        except Exception as e:
            self.api.delete_database(cluster_id, project_name)
            raise DatabaseCreationError(str(e))
        cluster = self.api.get_one_cluster(cluster_id)
        private_connection = cluster.privateConnection

        if cluster.engine == "pg":
            prefix = "postgresql://"
        elif cluster.engine == "mysql":
            prefix = "mysql://"
        else:
            raise DatabaseEngineNotSupported(
                "Bad cluster. Only PG and Mysql clusters are supported"
            )

        return (
            f"{prefix}{user.name}:{user.password}@{private_connection.host}:"
            f"{private_connection.port}/{database.name}"
        )

    def get_database_user(self, cluster_id, username) -> DatabaseUser:
        return self.api.get_database_user(cluster_id, username)

    # def recreate_database(self, cluster_id: str, db_name: str):
    #     """
    #     this command just deletes database and create it again
    #     (when it needs to be deleted like uploading a dump)
    #     :param cluster_id: cluster where is database stored
    #     :param db_name: name of database
    #     :return: None - because db_url is the same
    #     """
    #     self.api.delete_database(cluster_id, db_name)
    #     self.api.create_database(cluster_id, db_name)

from edos.api.digitalocean.base_api import DigitalOceanApi
from edos.api.digitalocean.databases.helpers import (
    parse_one_cluster,
    parse_one_database,
    parse_one_user,
)
from edos.api.digitalocean.databases.models.cluster import DatabaseCluster
from edos.api.digitalocean.databases.models.database import Database
from edos.api.digitalocean.databases.models.database_user import DatabaseUser


class DatabaseApi(DigitalOceanApi):
    path = "/v2/databases"

    def get_clusters(self) -> list[DatabaseCluster]:
        url = self.build_url()
        resp = self.get_request(url)["databases"]
        clusters = []
        for item in resp:
            clusters.append(parse_one_cluster(item))
        return clusters

    def get_one_cluster(self, cluster_id: str) -> DatabaseCluster:
        cluster_path = f"/{cluster_id}"
        url = self.build_url() + cluster_path
        resp = self.get_request(url)["database"]
        return parse_one_cluster(resp)

    def get_databases(self, cluster_id: str) -> list[Database]:
        cluster_path = f"/{cluster_id}/dbs"
        url = self.build_url() + cluster_path
        resp = self.get_request(url)["dbs"]
        databases = []
        for item in resp:
            databases.append(parse_one_database(item))
        return databases

    def get_database(self, cluster_id: str, database_name: str) -> Database:
        url = self.build_url() + f"/{cluster_id}/dbs/{database_name}"
        resp = self.get_request(url)["db"]
        print(resp)
        return parse_one_database(resp)

    def create_database(self, cluster_id: str, database_name: str) -> Database:
        cluster_path = f"/{cluster_id}/dbs"
        url = self.build_url() + cluster_path
        payload = {
            "name": database_name,
        }
        resp = self.post_request(url, payload)
        return parse_one_database(resp["db"])

    def create_database_user(self, cluster_id: str, user_name: str) -> DatabaseUser:
        cluster_path = f"/{cluster_id}/users"
        url = self.build_url() + cluster_path
        payload = {
            "name": user_name,
        }
        resp = self.post_request(url, payload)
        return parse_one_user(resp["user"])

    def delete_database(self, cluster_id: str, database_name: str):
        cluster_path = f"/{cluster_id}/dbs/{database_name}"
        url = self.build_url() + cluster_path
        self.delete_request(url)

    def get_database_user(self, cluster_id: str, username: str) -> DatabaseUser:
        cluster_path = f"/{cluster_id}/users/{username}"
        url = self.build_url() + cluster_path
        resp = self.get_request(url)
        return parse_one_user(resp["user"])

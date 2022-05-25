import requests
from http import HTTPStatus
from typing import Dict, Any, Optional
from requests import Response
from gigapipe.exceptions import GigapipeServerError, GigapipeClientError
from gigapipe.api_client.api import Base
from gigapipe.api_client.gigapipe_api import GigapipeApi


class Clickhouse(Base):
    """
    Clickhouse Class
    """

    def __init__(self, api):
        """
        Clickhouse Constructor
        :param api: The API instance
        """
        super(Clickhouse, self).__init__(api)

    @GigapipeApi.autorefresh_access_token
    def create_user(self, cluster_slug: str, *, user: Dict[str, str]) -> Response:
        """
        Creates a user on clickhouse
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/users"

        try:
            response: Response = requests.post(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json=user)
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        except TypeError:
            raise GigapipeClientError(
                status_code=HTTPStatus.BAD_REQUEST,
                message=f"Wrong Payload"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def get_users(self, cluster_slug: str) -> Response:
        """
        Obtains the clickhouse users
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/users"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def update_user(self, cluster_slug: str, *, user: Dict[str, Any]) -> Response:
        """
        Updates a Clickhouse user
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/users"

        try:
            response: Response = requests.patch(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json=user)
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        except TypeError:
            raise GigapipeClientError(
                status_code=HTTPStatus.BAD_REQUEST,
                message=f"Wrong Payload"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def delete_user(self, cluster_slug: str, username: str) -> Response:
        """
        Deletes a Clickhouse user
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/users?username={username}"

        try:
            response: Response = requests.delete(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def explore_tables(
        self, cluster_slug: str, *, table_name: Optional[str] = None, engine: Optional[str] = None
    ):
        """
        Displays the cluster tables according to a name and engine
        :param cluster_slug: the slug of the cluster
        :param table_name: the name of the table
        :param engine: the engine
        :return: the tables exploration
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/explore/tables"

        if table_name is not None and engine is None:
            url = f"{url}?table={table_name}"
        elif engine is not None and table_name is None:
            url = f"{url}?engine={engine}"
        elif table_name is not None and engine is not None:
            url = f"{url}?table={table_name}&engine={engine}"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def get_formats(self) -> Response:
        """
        Obtains the clickhouse formats
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clickhouse/formats"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def get_versions(self) -> Response:
        """
        Obtains the clickhouse versions available in Gigapipe
        :return: A list of ClickHouse version names with their corresponding ids
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clickhouse/versions"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

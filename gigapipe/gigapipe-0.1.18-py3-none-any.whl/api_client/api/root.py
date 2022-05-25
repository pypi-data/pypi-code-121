import requests
from http import HTTPStatus
from requests import Response
from gigapipe.exceptions import GigapipeServerError
from gigapipe.api_client.api import Base
from gigapipe.api_client.gigapipe_api import GigapipeApi


class Root(Base):
    """
    Root Class
    """

    def __init__(self, api):
        """
        Root Constructor
        :param api: The API instance
        """
        super(Root, self).__init__(api)

    @GigapipeApi.autorefresh_access_token
    def get_machines(self, provider_id: int, region_id: int) -> Response:
        """
        Obtains all the machines per provider and region
        :return: A list of machines
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/machines?provider={provider_id}&region={region_id}"

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
    def get_machine(self, machine_id: int) -> Response:
        """
        Obtains a specific machine based on the id passed as a parameter
        :return: A dictionary containing the machine info
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/machines/{machine_id}"

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
    def get_providers(self) -> Response:
        """
        Obtains all the providers
        :return: A list containing all the providers
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/providers"

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
    def get_regions(self, provider_id: int) -> Response:
        """
        Obtains all the regions according to the provider passed as a parameter
        :return: A list containing the regions
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/regions?provider={provider_id}"

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
    def get_disk_types(self, provider_id: int, region_id: int) -> Response:
        """
        Obtains all the disk types per provider and region
        :return: A list of disk types
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/disk-types?provider={provider_id}&region={region_id}"

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

import requests
from http import HTTPStatus
from typing import Dict
from requests import Response
from gigapipe.exceptions import GigapipeServerError
from gigapipe.api_client.api import Base
from gigapipe.api_client.gigapipe_api import GigapipeApi


class Integrations(Base):
    """
    Integrations Class
    """

    def __init__(self, api):
        """
        Integrations Constructor
        :param api: The API instance
        """
        super(Integrations, self).__init__(api)

    @GigapipeApi.autorefresh_access_token
    def get_integration_types(self) -> Response:
        """
        Obtains the list of integrations types
        :return: A list containing the integration types
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/integrations/types"

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
    def get_integrations(self) -> Response:
        """
        Obtains the list of integrations
        :return: A list containing the integrations
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/integrations"

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
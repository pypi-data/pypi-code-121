from typing import Dict

import requests
from http import HTTPStatus
from requests import Response
from gigapipe.exceptions import GigapipeServerError
from gigapipe.api_client.api import Base
from gigapipe.api_client.gigapipe_api import GigapipeApi


class Roles(Base):
    """
    Roles Class
    """

    def __init__(self, api):
        """
        Roles Constructor
        :param api: The API instance
        """
        super(Roles, self).__init__(api)

    @GigapipeApi.autorefresh_access_token
    def switch(self, role_object: Dict[str, str]) -> Response:
        """
        Switches the role of the passed user
        :return: A message response or an error dict
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/roles/switch"

        try:
            response: Response = requests.post(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json=role_object)
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

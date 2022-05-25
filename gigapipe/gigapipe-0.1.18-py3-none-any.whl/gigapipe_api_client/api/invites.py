import requests
from http import HTTPStatus
from typing import Dict
from requests import Response
from gigapipe.exceptions import GigapipeServerError
from gigapipe.api_client.api import Base
from gigapipe.api_client.gigapipe_api import GigapipeApi


class Invites(Base):
    """
    Users Class
    """

    def __init__(self, api):
        """
        Users Constructor
        :param api: The API instance
        """
        super(Invites, self).__init__(api)

    @GigapipeApi.autorefresh_access_token
    def send_invite(self, invite_object: Dict[str, str]) -> Response:
        """
        Sends an invite to a user
        :return: A Message Response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/invites"

        try:
            response: Response = requests.post(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json=invite_object)
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def delete_invite(self, email: str) -> Response:
        """
        Deletes a user invite
        :return: A Message Response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/invites"

        try:
            response: Response = requests.delete(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json={"email": email})
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

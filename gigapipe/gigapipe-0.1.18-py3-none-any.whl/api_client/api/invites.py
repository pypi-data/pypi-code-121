import requests
from http import HTTPStatus
from typing import Dict
from requests import Response
from gigapipe.exceptions import GigapipeServerError, GigapipeClientError
from gigapipe.api_client.api import Base
from gigapipe.api_client.gigapipe_api import GigapipeApi


class Invites(Base):
    """
    Invites Class
    """

    def __init__(self, api):
        """
        Invites Constructor
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
        except TypeError:
            raise GigapipeClientError(
                status_code=HTTPStatus.BAD_REQUEST,
                message=f"Wrong Payload"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def get_invite(self, token: str) -> Response:
        """
        Obtains an invite that has been sent to a user
        :return: An invite object
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/invites?token={token}"

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

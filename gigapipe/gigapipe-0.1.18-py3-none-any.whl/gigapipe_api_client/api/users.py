import requests
from http import HTTPStatus
from typing import Dict
from requests import Response
from gigapipe.exceptions import GigapipeServerError
from gigapipe.api_client.api import Base
from gigapipe.api_client.gigapipe_api import GigapipeApi


class Users(Base):
    """
    Users Class
    """

    def __init__(self, api):
        """
        Users Constructor
        :param api: The API instance
        """
        super(Users, self).__init__(api)

    @GigapipeApi.autorefresh_access_token
    def get_info(self) -> Response:
        """
        Obtains the user-in-session info
        :return: A dictionary containing the user info
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/users/me"

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
    def change_password(self, password_object: Dict[str, str]) -> Response:
        """
        Changes the user password
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/users/change-password"

        try:
            response: Response = requests.patch(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json=password_object)
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def update_name(self, user_object: Dict[str, str]) -> Response:
        """
        Changes the user first and last name
        :return: A dictionary containing the user-in-session info with the new name
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/users"

        try:
            response: Response = requests.patch(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json=user_object)
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def get_permissions(self) -> Response:
        """
        Obtains the user-in-session info
        :return: A dictionary containing the user permissions
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/users/me/permissions"

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
    def get_upcoming_invoice(self) -> Response:
        """
        Obtains the user organization upcoming invoice
        :return: A dictionary containing the invoice values
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/users/upcoming-invoice"

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


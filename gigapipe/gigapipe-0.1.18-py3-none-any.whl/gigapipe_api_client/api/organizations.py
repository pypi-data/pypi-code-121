import requests
from http import HTTPStatus
from requests import Response
from gigapipe.exceptions import GigapipeServerError

from gigapipe.api_client.api import Base
from gigapipe.api_client.gigapipe_api import GigapipeApi


class Organizations(Base):
    """
    Organizations Class
    """

    def __init__(self, api):
        """
        Organizations Constructor
        :param api: The API instance
        """
        super(Organizations, self).__init__(api)

    @GigapipeApi.autorefresh_access_token
    def get_users(self) -> Response:
        """
        Obtains the users of the organization
        :return: A dictionary containing the users of the organization
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/organizations/users"

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
    def get_invites(self) -> Response:
        """
        Obtains the invites of the organization. (Future users who are not users yet)
        :return: A dictionary containing the invites send by the organization
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/organizations/invites"

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
    def delete_organization(self) -> Response:
        """
        Deletes the organization
        The returned dictionary depends on whether the organization could be deleted or not:
        - organization_deleted=true and payment_link=null means the organization was deleted
        - organization_deleted=false and payment_link='some_link' means there are invoices to pay
        :return: A dictionary containing the deleted organization info
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/organizations"

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
    def get_upcoming_invoice(self) -> Response:
        """
        Obtains the user organization upcoming invoice
        :return: A dictionary containing the invoice values
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/organizations/upcoming-invoice"

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

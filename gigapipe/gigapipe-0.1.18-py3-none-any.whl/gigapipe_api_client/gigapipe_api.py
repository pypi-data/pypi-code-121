import functools
import requests
from gigapipe import client_prefix
from http import HTTPStatus
from json import JSONDecodeError
from typing import Optional, Dict, Any, Callable
from requests import Response
from gigapipe.exceptions import GigapipeClientError, GigapipeServerError
from gigapipe.api_client.api import Base


class GigapipeApi(object):
    """
    Gigapipe Python API
    """
    version: str = "v1"

    def __init__(self, url: str, *, client_id: str) -> None:
        """
        GigapipeApi Constructor
        :param url: URL of the api
        :param client_id: The Gigapipe Client ID
        """
        self.url: str = url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.client_id: Optional[str] = client_id

        # Authorizes the session upon creating an instance
        self.authorize()

    def authorize(self) -> None:
        """
        Authorizes the Gigapipe Python Client
        """
        from gigapipe import client_secret
        url: str = f"{self.url}/{self.__class__.version}/{client_prefix}/authorize"

        try:
            response: Response = requests.post(url, json={
                "client_id": self.client_id,
                "client_secret": client_secret
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise GigapipeClientError(
                status_code=HTTPStatus.NOT_FOUND,
                message="Resource Not found."
            )

        response: Dict[str, str] = response.json()
        self.access_token = response.get("access_token", None)
        self.refresh_token = response.get("refresh_token", None)

        if self.access_token is None:
            raise GigapipeClientError(
                status_code=HTTPStatus.UNAUTHORIZED,
                message="Invalid Authorization Token."
            )

    @staticmethod
    def should_refresh_access_token(response: Response) -> bool:
        """
        Whether the access token should be refreshed
        :param response: The response with a 401 Unauthorized error
        :return: true if the token needs refreshing, false otherwise
        """
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            response_data: Dict[str, Any] = response.json()
            return response_data.get("description") == "Authorization token has expired"
        return False

    def refresh_access_token(self) -> None:
        """
        Refreshes the access token. This method is called automatically if the system detects that the
        current access token is expired
        """
        url: str = f"{self.url}/{self.__class__.version}/refresh"

        try:
            response = requests.post(url, json={
                "token": self.refresh_token
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        try:
            response_data: Dict[str, Any] = response.json()
        except JSONDecodeError as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Could not parse JSON Response: {e}"
            )
        self.access_token = response_data["access_token"]
        self.refresh_token = response_data["refresh_token"]

    @staticmethod
    def autorefresh_access_token(method: Callable) -> Callable:
        """
        Refreshes the access token upon receiving 401 Unauthorized when the token is expired
        :param method: The caller method which calls the decorator
        :return: A call to the wrapper function
        """

        @functools.wraps(method)
        def wrapper(obj: Base, *args, **kwargs) -> Any:
            """
            Checks the token and applies the logic that will return the response
            :param obj: The object that contains the caller function. It will always inherit from Base
            :return: The JSON parsed response
            """
            response: Response = method(obj, *args, **kwargs)

            if obj.api.should_refresh_access_token(response=response):
                obj.api.refresh_access_token()
                response = method(obj, *args, **kwargs)
            try:
                response_data: ... = response.json()
            except JSONDecodeError as e:
                raise GigapipeServerError(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    message=f"Could not parse JSON Response: {e}"
                )
            return response_data

        return wrapper


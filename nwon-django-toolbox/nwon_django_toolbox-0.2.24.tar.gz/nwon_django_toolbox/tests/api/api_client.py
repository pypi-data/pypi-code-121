from typing import Dict, Optional

from rest_framework.response import Response
from rest_framework.test import APIClient as RestApiClient

from nwon_django_toolbox.settings import NWON_DJANGO_SETTINGS
from nwon_django_toolbox.typings import RequestBodyFormat


class ApiClient:
    """
    Facilitating request against URLs.

    Easy to set authentication token on initialization.
    """

    api_client: RestApiClient

    def __init__(
        self,
        token: Optional[str],
        authorization_prefix: str = NWON_DJANGO_SETTINGS.authorization_prefix,
    ):
        self.api_client = RestApiClient()

        if token:
            self.set_bearer_token(token, authorization_prefix)

    def set_bearer_token(
        self,
        token: str,
        authorization_prefix: str = NWON_DJANGO_SETTINGS.authorization_prefix,
    ):
        self.api_client.credentials(
            HTTP_AUTHORIZATION=f"{authorization_prefix} {token}"
        )

    def get(self, url: str) -> Response:
        return self.api_client.get(url)

    def post(
        self, url: str, body: Dict[str, str], body_format: RequestBodyFormat
    ) -> Response:
        return self.api_client.post(url, body, format=body_format.value)

    def put(
        self, url: str, body: Dict[str, str], body_format: RequestBodyFormat
    ) -> Response:
        return self.api_client.put(url, body, format=body_format.value)

    def patch(
        self, url: str, body: Dict[str, str], body_format: RequestBodyFormat
    ) -> Response:
        return self.api_client.patch(url, body, format=body_format.value)

    def delete(self, url: str) -> Response:
        return self.api_client.delete(url)

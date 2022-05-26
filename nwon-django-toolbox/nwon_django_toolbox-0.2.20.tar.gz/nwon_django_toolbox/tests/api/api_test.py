# pylint: disable=too-many-public-methods
import logging
from typing import Optional

from rest_framework.response import Response

from nwon_django_toolbox.settings import NWON_DJANGO_SETTINGS
from nwon_django_toolbox.tests.api.api_client import ApiClient
from nwon_django_toolbox.typings import RequestBodyFormat

LOGGER = logging.getLogger(NWON_DJANGO_SETTINGS.logger_name)


class ApiTest:
    """
    Facilitates testing an API.

    Provide convenience function for testing API calls and their outcomes.
    """

    def __init__(
        self,
        token: Optional[str] = None,
        authorization_prefix: str = NWON_DJANGO_SETTINGS.authorization_prefix,
    ):
        self.client = ApiClient(token, authorization_prefix)

    def set_bearer_token(
        self,
        token: str,
        authorization_prefix: str = NWON_DJANGO_SETTINGS.authorization_prefix,
    ):
        self.client.set_bearer_token(token, authorization_prefix)

    # get methods
    def get(self, url: str) -> Response:
        return self.client.get(url)

    def get_successful(self, url: str) -> dict:
        response = self.get(url)
        return self.__check_response(response, 200, url)

    def get_unauthorized(self, url: str) -> dict:
        response = self.get(url)
        return self.__check_response(response, 401, url)

    def get_forbidden(self, url: str) -> dict:
        response = self.get(url)
        return self.__check_response(response, 403, url)

    def get_bad_request(self, url: str) -> dict:
        response = self.get(url)
        return self.__check_response(response, 400, url)

    def get_not_found(self, url: str) -> dict:
        response = self.get(url)
        return self.__check_response(response, 404, url)

    def get_method_not_allowed(self, url: str) -> dict:
        response = self.get(url)
        return self.__check_response(response, 405, url)

    # post methods

    def post(self, url: str, body: dict, body_format: RequestBodyFormat) -> Response:
        return self.client.post(url, body=body, body_format=body_format)

    def post_successful(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.post(url, body, body_format)
        return self.__check_response(response, 200, url)

    def post_create_successful(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.post(url, body, body_format)
        return self.__check_response(response, 201, url)

    def post_no_content(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.post(url, body, body_format)
        return self.__check_response(response, 204, url)

    def post_bad_request(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.post(url, body, body_format)
        return self.__check_response(response, 400, url)

    def post_unauthorized(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.post(url, body, body_format)
        return self.__check_response(response, 401, url)

    def post_forbidden(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.post(url, body, body_format)
        return self.__check_response(response, 403, url)

    def post_not_found(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.post(url, body, body_format)
        return self.__check_response(response, 404, url)

    def post_method_not_allowed(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.post(url, body, body_format)
        return self.__check_response(response, 405, url)

    # put methods
    def put(self, url: str, body: dict, body_format: RequestBodyFormat) -> Response:
        return self.client.put(url, body, body_format=body_format)

    def put_successful(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.put(url, body, body_format)
        return self.__check_response(response, 200, url)

    def put_bad_request(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.put(url, body, body_format)
        return self.__check_response(response, 400, url)

    def put_unauthorized(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.put(url, body, body_format)
        return self.__check_response(response, 401, url)

    def put_forbidden(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.put(url, body, body_format)
        return self.__check_response(response, 403, url)

    def put_not_found(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.put(url, body, body_format)
        return self.__check_response(response, 404, url)

    def put_method_not_allowed(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.put(url, body, body_format)
        return self.__check_response(response, 405, url)

    # patch methods
    def patch(self, url: str, body: dict, body_format: RequestBodyFormat) -> Response:
        return self.client.patch(url, body, body_format=body_format)

    def patch_successful(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.patch(url, body, body_format)
        return self.__check_response(response, 200, url)

    def patch_bad_request(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.patch(url, body, body_format)
        return self.__check_response(response, 400, url)

    def patch_unauthorized(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.patch(url, body, body_format)
        return self.__check_response(response, 401, url)

    def patch_forbidden(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.patch(url, body, body_format)
        return self.__check_response(response, 403, url)

    def patch_not_found(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.patch(url, body, body_format)
        return self.__check_response(response, 404, url)

    def patch_method_not_allowed(
        self,
        url: str,
        body: dict,
        body_format: RequestBodyFormat = RequestBodyFormat.Json,
    ) -> dict:
        response = self.patch(url, body, body_format)
        return self.__check_response(response, 405, url)

    # delete methods
    def delete(self, url: str) -> Response:
        return self.client.delete(url)

    def delete_successful(self, url: str) -> dict:
        response = self.delete(url)
        return self.__check_response(response, 204, url)

    def delete_bad_request(self, url: str) -> dict:
        response = self.delete(url)
        return self.__check_response(response, 400, url)

    def delete_unauthorized(self, url: str) -> dict:
        response = self.delete(url)
        return self.__check_response(response, 401, url)

    def delete_forbidden(self, url: str) -> dict:
        response = self.delete(url)
        return self.__check_response(response, 403, url)

    def delete_not_found(self, url: str) -> dict:
        response = self.delete(url)
        return self.__check_response(response, 404, url)

    def delete_method_not_allowed(self, url: str) -> dict:
        response = self.delete(url)
        return self.__check_response(response, 405, url)

    def __check_response(
        self, response: Response, expected_status_code: int, url: str
    ) -> dict:

        # output response for debugging purposes
        if response.status_code != expected_status_code:
            LOGGER.debug(
                "\nURL: "
                + url
                + "\nExpected status code: "
                + expected_status_code.__str__()
                + "\nReceived status code:"
                + response.status_code.__str__()
            )

            try:
                LOGGER.debug("\nResponse:\n %s", response.json().__str__())
            except (TypeError, UnicodeDecodeError):
                LOGGER.debug("\nNo response json: %s", response.__str__())
                LOGGER.debug(response.content)
            except (ValueError):
                LOGGER.debug("\nValue Error: %s", response.__str__())
                LOGGER.debug(response.content)

        assert response.status_code == expected_status_code  # nosec

        try:
            return response.json()
        except Exception:
            return {}

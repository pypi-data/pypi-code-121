import os
import requests


class ApiManager:
    """Sends authenticated requests to API.

    This class is designed to simplify queries sent to the Classy API
    by the SDK – from initial settings such as authentication,
    to extending timeout or checking for possible exceptions.

    Args:
        api_url (optional):
            A url to Classy API. It can be supplied
            as an argument or through environment variables.
        api_token (optional):
            An authorization token. It can be supplied
            as an argument or through environment variables.
        timeout (optional):
            A server response timeout in seconds, defaults to 30.
    """

    def __init__(
        self, api_url: str = None, api_token: str = None, timeout: int = 30
    ) -> None:
        self.api_url = os.environ["API_URL"] if api_url is None else api_url
        self.api_token = os.environ["API_TOKEN"] if api_token is None else api_token
        self.timeout = timeout
        self._headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_token,
        }

    def query(
        self, req_type: str, url: str, data: dict = None, params: dict = None
    ) -> requests.Response:
        """Sends API requests.

        Args:
            req_type:
                The type of request, e.g. 'GET', 'POST', 'PATCH'.
            url:
                The API url to query.
            data (optional):
                Optional data to send as a serialiezed JSON.
            params (optional):
                Additional arguments passed to the url.
        """
        response = requests.request(
            req_type.upper(),
            url,
            json=data,
            params=params,
            headers=self._headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response

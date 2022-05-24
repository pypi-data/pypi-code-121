import requests

from chaingrep.constants import BASE_URL, CLIENT_SIGNALING
from chaingrep.exceptions import APIError, AuthenticationError
from chaingrep.utils.format import standardize_response


class Requester:
    def __init__(self, auth):
        self.auth = auth

    def _error_handler(self, status_code, response):
        error_message = response.get("detail", "Error")

        if status_code == 404 and error_message == "API key not found":
            raise AuthenticationError("Invalid API key.")

        if status_code == 500:
            raise APIError("Unidentified API error.")

        # Handle method-specific errors outside of _error_handler
        return {"status_code": status_code, "response": error_message}

    def get(self, endpoint, params=None):
        parameters = CLIENT_SIGNALING

        if params:
            parameters = {**parameters, **params}

        response = requests.get(f"{BASE_URL}{endpoint}", params=parameters, auth=self.auth, timeout=5)
        status_code = response.status_code
        response = response.json()

        if status_code != 200:
            return self._error_handler(status_code, response)

        response = standardize_response(response.get("response"))

        return {"status_code": status_code, "response": response}

    def post(self, endpoint, body=None, params=None):
        parameters = CLIENT_SIGNALING

        if params:
            parameters = {**parameters, **params}

        if not body:
            body = {}

        response = requests.post(f"{BASE_URL}{endpoint}", json=body, params=parameters, auth=self.auth, timeout=5)
        status_code = response.status_code
        response = response.json()

        if status_code != 200:
            return self._error_handler(status_code, response)

        response = standardize_response(response.get("response"))

        return {"status_code": status_code, "response": response}

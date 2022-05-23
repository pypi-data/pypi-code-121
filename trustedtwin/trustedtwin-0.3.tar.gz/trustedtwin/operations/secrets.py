"""Definition of Secrets access methods."""
import urllib.parse
from typing import TYPE_CHECKING, Dict, Any

from trustedtwin.misc import RESTMethod
from trustedtwin.models.responses import process_response

if TYPE_CHECKING:
    from trustedtwin.service import RestService


class SecretsOperations:
    """Interfaces for accessing Secrets API operations"""

    def __init__(self, service: "RestService"):
        """Initialize object"""
        self._service = service
        self._http_client = self._service.http_client

    def get(self, user: str) -> Dict:
        """Execute getUserSecret API operation"""

        endpoint = "users/{user}/secrets".format(user=user)
        endpoint = urllib.parse.quote(endpoint)

        resp = self._http_client.execute_request(
            method=RESTMethod.GET,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "getUserSecret", **self._service.kwargs)

    def update_secret(self, user: str, **kwargs: Any) -> Dict:
        """Execute updateUserSecret API operation"""

        endpoint = "users/{user}/secrets".format(user=user)
        endpoint = urllib.parse.quote(endpoint)

        body = {
            "validity_ts": kwargs.get("validity_ts")
        }
        body = {x: y for x, y in body.items() if y}

        resp = self._http_client.execute_request(
            method=RESTMethod.PATCH,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            body=body,
        )

        return process_response(resp, "updateUserSecret", **self._service.kwargs)

    def delete(self, user: str) -> Dict:
        """Execute deleteUserSecret API operation"""

        endpoint = "users/{user}/secrets".format(user=user)
        endpoint = urllib.parse.quote(endpoint)

        resp = self._http_client.execute_request(
            method=RESTMethod.DELETE,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "deleteUserSecret", **self._service.kwargs)

    def create_secret(
        self, account: str, pin: str
    ) -> Dict:
        """Execute createUserSecret API operation"""

        endpoint = "secrets/{account}/{pin}".format(account=account, pin=pin)
        endpoint = urllib.parse.quote(endpoint)

        resp = self._http_client.execute_request(
            method=RESTMethod.POST,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "createUserSecret", **self._service.kwargs)

    def create_secret_pin(
        self, user: str, **kwargs   : Any
    ) -> Dict:
        """Execute createUserSecret API operation"""

        endpoint = "users/{user}/secrets".format(user=user)
        endpoint = urllib.parse.quote(endpoint)

        body = {
            "account": kwargs.get("account"),
            "user": kwargs.get("user"),
            "secret": kwargs.get("secret"),
            "validity_ts": kwargs.get("validity_ts"),
        }
        body = {x: y for x, y in body.items() if y}

        resp = self._http_client.execute_request(
            method=RESTMethod.POST,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            body=body,
        )

        return process_response(resp, "createUserSecretPIN", **self._service.kwargs)

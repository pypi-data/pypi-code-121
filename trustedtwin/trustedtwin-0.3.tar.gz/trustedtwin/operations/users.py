"""Definition of Users access methods."""
import urllib.parse
from typing import TYPE_CHECKING, Dict, Any

from trustedtwin.misc import RESTMethod
from trustedtwin.models.responses import process_response

if TYPE_CHECKING:
    from trustedtwin.service import RestService


class UsersOperations:
    """Interfaces for accessing Users API operations"""

    def __init__(self, service: "RestService"):
        """Initialize object"""
        self._service = service
        self._http_client = self._service.http_client

    def create(self, **kwargs: Any) -> Dict:
        """Execute createUser API operation"""

        endpoint = "users"
        endpoint = urllib.parse.quote(endpoint)

        body = {
            "name": kwargs.get("name"),
            "role": kwargs.get("role"),
            "description": kwargs.get("description"),
        }
        body = {x: y for x, y in body.items() if y}

        resp = self._http_client.execute_request(
            method=RESTMethod.POST,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            body=body,
        )

        return process_response(resp, "createUser", **self._service.kwargs)

    def get(self, user: str) -> Dict:
        """Execute getUser API operation"""

        endpoint = "users/{user}".format(user=user)
        endpoint = urllib.parse.quote(endpoint)

        resp = self._http_client.execute_request(
            method=RESTMethod.GET,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "getUser", **self._service.kwargs)

    def delete(self, user: str) -> Dict:
        """Execute deleteUser API operation"""

        endpoint = "users/{user}".format(user=user)
        endpoint = urllib.parse.quote(endpoint)

        resp = self._http_client.execute_request(
            method=RESTMethod.DELETE,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "deleteUser", **self._service.kwargs)

    def update(self, user: str, **kwargs: Any) -> Dict:
        """Execute updateUser API operation"""

        endpoint = "users/{user}".format(user=user)
        endpoint = urllib.parse.quote(endpoint)

        body = {
            "name": kwargs.get("name"),
            "role": kwargs.get("role"),
            "description": kwargs.get("description"),
        }
        body = {x: y for x, y in body.items() if y}

        resp = self._http_client.execute_request(
            method=RESTMethod.PATCH,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            body=body,
        )

        return process_response(resp, "updateUser", **self._service.kwargs)

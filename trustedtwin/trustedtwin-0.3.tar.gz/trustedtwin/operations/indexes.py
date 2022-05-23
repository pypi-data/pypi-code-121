"""Definition of Indexes access methods."""
import urllib.parse
from typing import TYPE_CHECKING, Dict, Any

from trustedtwin.misc import RESTMethod
from trustedtwin.models.responses import process_response

if TYPE_CHECKING:
    from trustedtwin.service import RestService


class IndexesOperations:
    """Interfaces for accessing Indexes API operations"""

    def __init__(self, service: "RestService"):
        """Initialize object"""
        self._service = service
        self._http_client = self._service.http_client

    def get_table(self, index: str) -> Dict:
        """Execute getIndexesTable API operation"""

        endpoint = "account/services/indexes/{index}".format(
            index=index
        )
        endpoint = urllib.parse.quote(endpoint)

        resp = self._http_client.execute_request(
            method=RESTMethod.GET,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "getIndexesTable", **self._service.kwargs)

    def delete_table(self, index: str) -> Dict:
        """Execute deleteIndexesTable API operation"""

        endpoint = "account/services/indexes/{index}".format(
            index=index
        )
        endpoint = urllib.parse.quote(endpoint)

        resp = self._http_client.execute_request(
            method=RESTMethod.DELETE,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "deleteIndexesTable", **self._service.kwargs)

    def update_table(self, index: str, **kwargs: Any) -> Dict:
        """Execute updateIndexesTable API operation"""

        endpoint = "account/services/indexes/{index}".format(
            index=index
        )
        endpoint = urllib.parse.quote(endpoint)

        body = {
            "rule": kwargs.get("rule"),
        }
        body = {x: y for x, y in body.items() if y}

        resp = self._http_client.execute_request(
            method=RESTMethod.PATCH,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            body=body,
        )

        return process_response(resp, "updateIndexesTable", **self._service.kwargs)

    def get_tables(self) -> Dict:
        """Execute getIndexesTables API operation"""

        endpoint = "account/services/indexes"
        endpoint = urllib.parse.quote(endpoint)

        resp = self._http_client.execute_request(
            method=RESTMethod.GET,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "getIndexesTables", **self._service.kwargs)

    def update_access(self, **kwargs: Any) -> Dict:
        """Execute updateIndexesAccess API operation"""

        endpoint = "account/services/indexes"
        endpoint = urllib.parse.quote(endpoint)

        body = {
            "users": kwargs.get("users")
        }
        body = {x: y for x, y in body.items() if y}

        resp = self._http_client.execute_request(
            method=RESTMethod.PATCH,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            body=body,
        )

        return process_response(resp, "updateIndexesAccess", **self._service.kwargs)

    def create_table(self, **kwargs: Any) -> Dict:
        """Execute createIndexesTable API operation"""

        endpoint = "account/services/indexes"
        endpoint = urllib.parse.quote(endpoint)

        body = {
            "indexes": kwargs.get("indexes")
        }
        body = {x: y for x, y in body.items() if y}

        resp = self._http_client.execute_request(
            method=RESTMethod.POST,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            body=body,
        )

        return process_response(resp, "createIndexesTable", **self._service.kwargs)

    def truncate_table(self, index: str) -> Dict:
        """Execute truncateIndexesTable API operation"""

        endpoint = "account/services/indexes/{index}/data".format(
            index=index
        )
        endpoint = urllib.parse.quote(endpoint)

        resp = self._http_client.execute_request(
            method=RESTMethod.DELETE,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "truncateIndexesTable", **self._service.kwargs)

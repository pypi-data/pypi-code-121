"""Definition of Timeseries access methods."""
import urllib.parse
from typing import TYPE_CHECKING, Dict, Any

from trustedtwin.misc import RESTMethod
from trustedtwin.models.responses import process_response

if TYPE_CHECKING:
    from trustedtwin.service import RestService


class TimeseriesOperations:
    """Interfaces for accessing Timeseries API operations"""

    def __init__(self, service: "RestService"):
        """Initialize object"""
        self._service = service
        self._http_client = self._service.http_client

    def get_table(self, timeseries: str) -> Dict:
        """Execute getTimeseriesTable API operation"""

        endpoint = "account/services/timeseries/{timeseries}".format(
            timeseries=timeseries
        )
        endpoint = urllib.parse.quote(endpoint)

        resp = self._http_client.execute_request(
            method=RESTMethod.GET,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "getTimeseriesTable", **self._service.kwargs)

    def delete_table(self, timeseries: str) -> Dict:
        """Execute deleteTimeseriesTable API operation"""

        endpoint = "account/services/timeseries/{timeseries}".format(
            timeseries=timeseries
        )
        endpoint = urllib.parse.quote(endpoint)

        resp = self._http_client.execute_request(
            method=RESTMethod.DELETE,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "deleteTimeseriesTable", **self._service.kwargs)

    def update_table(self, timeseries: str, **kwargs: Any) -> Dict:
        """Execute updateTimeseriesTable API operation"""

        endpoint = "account/services/timeseries/{timeseries}".format(
            timeseries=timeseries
        )
        endpoint = urllib.parse.quote(endpoint)

        body = {
            "defaults": kwargs.get("defaults"),
            "retention": kwargs.get("retention"),
            "chunk": kwargs.get("chunk"),
        }
        body = {x: y for x, y in body.items() if y}

        resp = self._http_client.execute_request(
            method=RESTMethod.PATCH,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            body=body,
        )

        return process_response(resp, "updateTimeseriesTable", **self._service.kwargs)

    def get_tables(self) -> Dict:
        """Execute getTimeseriesTables API operation"""

        endpoint = "account/services/timeseries"
        endpoint = urllib.parse.quote(endpoint)

        resp = self._http_client.execute_request(
            method=RESTMethod.GET,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "getTimeseriesTables", **self._service.kwargs)

    def update_access(self, **kwargs: Any) -> Dict:
        """Execute updateTimeseriesAccess API operation"""

        endpoint = "account/services/timeseries"
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

        return process_response(resp, "updateTimeseriesAccess", **self._service.kwargs)

    def create_table(self, **kwargs: Any) -> Dict:
        """Execute createTimeseriesTable API operation"""

        endpoint = "account/services/timeseries"
        endpoint = urllib.parse.quote(endpoint)

        body = {
            "timeseries": kwargs.get("timeseries")
        }
        body = {x: y for x, y in body.items() if y}

        resp = self._http_client.execute_request(
            method=RESTMethod.POST,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            body=body,
        )

        return process_response(resp, "createTimeseriesTable", **self._service.kwargs)

    def truncate_table(self, timeseries: str) -> Dict:
        """Execute truncateTimeseriesTable API operation"""

        endpoint = "account/services/timeseries/{timeseries}/data".format(
            timeseries=timeseries
        )
        endpoint = urllib.parse.quote(endpoint)

        resp = self._http_client.execute_request(
            method=RESTMethod.DELETE,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "truncateTimeseriesTable", **self._service.kwargs)

"""Definition of Log access methods."""
import urllib.parse
from typing import TYPE_CHECKING, Dict, Optional

from trustedtwin.misc import RESTMethod
from trustedtwin.models.responses import process_response

if TYPE_CHECKING:
    from trustedtwin.service import RestService


class LogOperations:
    """Interfaces for accessing Log API operations"""

    def __init__(self, service: "RestService"):
        """Initialize object"""
        self._service = service
        self._http_client = self._service.http_client

    def get_log(self, fragment: Optional[str] = None) -> Dict:
        """Execute getLog API operation"""

        endpoint = "log"
        endpoint = urllib.parse.quote(endpoint)

        params = {
            "fragment": fragment,
        }
        params = {k: v for k, v in params.items() if v is not None}

        resp = self._http_client.execute_request(
            method=RESTMethod.GET,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            params=params,
        )

        return process_response(resp, "getLog", **self._service.kwargs)

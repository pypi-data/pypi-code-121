"""Definition of Docs access methods."""
import urllib.parse
from typing import TYPE_CHECKING, Dict, Optional, Any

from trustedtwin.misc import RESTMethod
from trustedtwin.models.responses import process_response

if TYPE_CHECKING:
    from trustedtwin.service import RestService


class DocsOperations:
    """Interfaces for accessing Docs API operations"""

    def __init__(self, service: "RestService"):
        """Initialize object"""
        self._service = service
        self._http_client = self._service.http_client

    def get_twin_docs(self, twin: str, view: Optional[str] = None) -> Dict:
        """Execute getTwinDocs API operation"""

        endpoint = "twins/{twin}/docs".format(twin=twin)
        endpoint = urllib.parse.quote(endpoint)

        params = {
            "view": view,
        }
        params = {k: v for k, v in params.items() if v is not None}

        resp = self._http_client.execute_request(
            method=RESTMethod.GET,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            params=params
        )

        return process_response(resp, "getTwinDocs", **self._service.kwargs)

    def attach_twin_doc(self, twin: str, **kwargs: Any) -> Dict:
        """Execute attachTwinDoc API operation"""

        endpoint = "twins/{twin}/docs".format(twin=twin)
        endpoint = urllib.parse.quote(endpoint)

        body = {
            "docs": kwargs.get("docs")
        }
        body = {x: y for x, y in body.items() if y}

        resp = self._http_client.execute_request(
            method=RESTMethod.POST,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            body=body,
        )

        return process_response(resp, "attachTwinDoc", **self._service.kwargs)

    def delete_twin_docs(self, twin: str) -> Dict:
        """Execute deleteTwinDocs API operation"""

        endpoint = "twins/{twin}/docs".format(twin=twin)
        endpoint = urllib.parse.quote(endpoint)

        resp = self._http_client.execute_request(
            method=RESTMethod.DELETE,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "deleteTwinDocs", **self._service.kwargs)

    def get_twin_doc(
        self, twin: str, doc_name: str, download: Optional[bool] = None
    ) -> Dict:
        """Execute getTwinDoc API operation"""

        doc_name = urllib.parse.quote(doc_name, safe='')
        endpoint = "twins/{twin}/docs/{doc_name}".format(twin=twin, doc_name=doc_name)

        params = {"download": download}
        params = {k: v for k, v in params.items() if v is not None}

        resp = self._http_client.execute_request(
            method=RESTMethod.GET,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            params=params,
        )

        return process_response(resp, "getTwinDoc", **self._service.kwargs)

    def update_twin_doc(
        self, twin: str, doc_name: str, **kwargs: Any
    ) -> Dict:
        """Execute updateTwinDoc API operation"""

        doc_name = urllib.parse.quote(doc_name, safe='')
        endpoint = "twins/{twin}/docs/{doc_name}".format(twin=twin, doc_name=doc_name)

        body = {
            "description": kwargs.get("description")
        }

        resp = self._http_client.execute_request(
            method=RESTMethod.PATCH,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            body=body,
        )

        return process_response(resp, "updateTwinDoc", **self._service.kwargs)

    def delete_twin_doc(self, twin: str, doc_name: str) -> Dict:
        """Execute deleteTwinDoc API operation"""

        doc_name = urllib.parse.quote(doc_name, safe='')
        endpoint = "twins/{twin}/docs/{doc_name}".format(twin=twin, doc_name=doc_name)

        resp = self._http_client.execute_request(
            method=RESTMethod.DELETE,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "deleteTwinDoc", **self._service.kwargs)

    def create_upload_url(self) -> Dict:
        """Execute createUploadURL API operation"""

        endpoint = "cache"
        endpoint = urllib.parse.quote(endpoint)

        resp = self._http_client.execute_request(
            method=RESTMethod.POST,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "createUploadURL", **self._service.kwargs)

    def invalidate_upload_url(self, handler: str) -> Dict:
        """Execute invalidateUploadURL API operation"""

        endpoint = "cache/{handler}".format(handler=handler)
        endpoint = urllib.parse.quote(endpoint)

        resp = self._http_client.execute_request(
            method=RESTMethod.DELETE,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
        )

        return process_response(resp, "invalidateUploadURL", **self._service.kwargs)

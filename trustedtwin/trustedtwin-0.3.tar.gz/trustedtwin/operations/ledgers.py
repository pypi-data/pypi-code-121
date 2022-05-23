"""Definition of Ledgers access methods."""
import urllib.parse
from typing import TYPE_CHECKING, Dict, Optional, List, Any

from trustedtwin.misc import RESTMethod
from trustedtwin.models.responses import process_response

if TYPE_CHECKING:
    from trustedtwin.service import RestService


class LedgersOperations:
    """Interfaces for accessing Ledgers API operations"""

    def __init__(self, service: "RestService"):
        """Initialize object"""
        self._service = service
        self._http_client = self._service.http_client

    def add_twin_ledger_entry(
        self, twin: str, ledger: str = "personal", **kwargs: Any
    ) -> Dict:
        """Execute addTwinLedgerEntry API operation"""

        endpoint = "twins/{twin}/ledgers/{ledger}".format(twin=twin, ledger=ledger)
        endpoint = urllib.parse.quote(endpoint)

        body = {
            "entries": kwargs.get("entries")
        }
        body = {x: y for x, y in body.items() if y}

        resp = self._http_client.execute_request(
            method=RESTMethod.POST,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            body=body,
        )

        return process_response(resp, "addTwinLedgerEntry", **self._service.kwargs)

    def get_twin_ledger_entry(
        self,
        twin: str,
        ledger: str = "personal",
        show_references: Optional[bool] = None,
        show_public: Optional[bool] = None,
        show_private: Optional[bool] = None,
        entries: Optional[List[str]] = None,
    ) -> Dict:
        """Execute getTwinLedgerEntry API operation"""

        endpoint = "twins/{twin}/ledgers/{ledger}".format(twin=twin, ledger=ledger)
        endpoint = urllib.parse.quote(endpoint)
        params = {
            "entries": entries,
            "show_private": show_private,
            "show_public": show_public,
            "show_references": show_references,
        }
        params = {k: v for k, v in params.items() if v is not None}

        resp = self._http_client.execute_request(
            method=RESTMethod.GET,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            params=params,
        )

        return process_response(resp, "getTwinLedgerEntry", **self._service.kwargs)

    def update_twin_ledger_entry(
        self, twin: str, ledger: str = "personal", **kwargs: Any
    ) -> Dict:
        """Execute updateTwinLedgerEntry API operation"""

        endpoint = "twins/{twin}/ledgers/{ledger}".format(twin=twin, ledger=ledger)
        endpoint = urllib.parse.quote(endpoint)

        body = {
            "entries": kwargs.get("entries")
        }
        body = {x: y for x, y in body.items() if y}

        resp = self._http_client.execute_request(
            method=RESTMethod.PATCH,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            body=body,
        )

        return process_response(resp, "updateTwinLedgerEntry", **self._service.kwargs)

    def delete_twin_ledger_entry(
        self, twin: str, ledger: str = "personal", entries: Optional[List[str]] = None
    ) -> Dict:
        """Execute deleteTwinLedgerEntry API operation"""

        endpoint = "twins/{twin}/ledgers/{ledger}".format(twin=twin, ledger=ledger)
        endpoint = urllib.parse.quote(endpoint)
        params = {"entries": entries}
        params = {k: v for k, v in params.items() if v is not None}

        resp = self._http_client.execute_request(
            method=RESTMethod.DELETE,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            params=params,
        )

        return process_response(resp, "deleteTwinLedgerEntry", **self._service.kwargs)

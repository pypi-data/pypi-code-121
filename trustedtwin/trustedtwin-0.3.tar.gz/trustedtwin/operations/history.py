"""Definition of History access methods."""
import urllib.parse
from typing import TYPE_CHECKING, Dict, Optional, List, Any

from trustedtwin.misc import RESTMethod
from trustedtwin.models.responses import process_response

if TYPE_CHECKING:
    from trustedtwin.service import RestService


class HistoryOperations:
    """Interfaces for accessing History API operations"""

    def __init__(self, service: "RestService"):
        """Initialize object"""
        self._service = service
        self._http_client = self._service.http_client

    def get_twin_ledger_entry_history(
            self,
            twin: str,
            ledger: str = "personal",
            ge: Optional[str] = None,
            le: Optional[str] = None,
            limit: int = 100,
            entries: Optional[List[str]] = None,
    ) -> Dict:
        """Execute getTwinLedgerEntryHistory API operation"""

        endpoint = "twins/{twin}/ledgers/{ledger}/history".format(twin=twin, ledger=ledger)
        endpoint = urllib.parse.quote(endpoint)
        params = {
            "entries": entries,
            "ge": ge,
            "le": le,
            "limit": limit,
        }
        params = {k: v for k, v in params.items() if v is not None}

        resp = self._http_client.execute_request(
            method=RESTMethod.GET,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            params=params,
        )

        return process_response(resp, "getTwinLedgerEntryHistory", **self._service.kwargs)

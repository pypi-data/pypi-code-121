"""RestService access operations"""
import logging
from typing import Any, Optional

from trustedtwin.http_client import HTTPClient
from trustedtwin.operations.docs import DocsOperations
from trustedtwin.operations.history import HistoryOperations
from trustedtwin.operations.identities import IdentitiesOperations
from trustedtwin.operations.indexes import IndexesOperations
from trustedtwin.operations.ledgers import LedgersOperations
from trustedtwin.operations.log import LogOperations
from trustedtwin.operations.roles import RolesOperations
from trustedtwin.operations.secrets import SecretsOperations
from trustedtwin.operations.timeseries import TimeseriesOperations
from trustedtwin.operations.twins import TwinsOperations
from trustedtwin.operations.users import UsersOperations

logger = logging.getLogger("trusted_twin")


DEFAULT_TT_API_HOST = "https://rest.trustedtwin.com"

# WARNING: This code has been generated automatically, do not modify unless you know what you are doing.


class RestService:
    """Represents client accessing API"""

    def __init__(self, auth: Optional[str] = None, api_host: str = DEFAULT_TT_API_HOST, **kwargs: Any):
        """Initialize object

        :param api_host: url to api host
        :param auth: Authorization secret
        """
        self.http_client = HTTPClient(host_name=api_host, auth=auth)
        self.kwargs = kwargs

    @property
    def twins(self) -> TwinsOperations:
        """Return Twins related API operations"""
        return TwinsOperations(self)

    @property
    def identities(self) -> IdentitiesOperations:
        """Return Identities related API operations"""
        return IdentitiesOperations(self)

    @property
    def ledgers(self) -> LedgersOperations:
        """Return Ledgers related API operations"""
        return LedgersOperations(self)

    @property
    def roles(self) -> RolesOperations:
        """Return Roles related API operations"""
        return RolesOperations(self)

    @property
    def secrets(self) -> SecretsOperations:
        """Return Secrets related API operations"""
        return SecretsOperations(self)

    @property
    def timeseries(self) -> TimeseriesOperations:
        """Return Timeseries related API operations"""
        return TimeseriesOperations(self)

    @property
    def docs(self) -> DocsOperations:
        """Return Docs related API operations"""
        return DocsOperations(self)

    @property
    def users(self) -> UsersOperations:
        """Return Users related API operations"""
        return UsersOperations(self)

    @property
    def log(self) -> LogOperations:
        """Return Log related API operations"""
        return LogOperations(self)

    @property
    def history(self) -> HistoryOperations:
        """Return History related API operations"""
        return HistoryOperations(self)

    @property
    def indexes(self) -> IndexesOperations:
        """Return Indexes related API operations"""
        return IndexesOperations(self)

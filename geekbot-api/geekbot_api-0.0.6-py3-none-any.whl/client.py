from .clients.reports import _ReportsAsyncClient
from .clients.reports import _ReportsClient
from .clients.standups import _StandupsAsyncClient
from .clients.standups import _StandupsClient
from .clients.teams import _TeamsAsyncClient
from .clients.teams import _TeamsClient
from .config import GeekbotAPIConfig


class GeekbotAPIClient:
    def __init__(self, config: GeekbotAPIConfig):
        self.config = config
        self.teams = _TeamsClient(
            base_api_path=config.base_api_path,
            api_version=config.api_version,
            path="teams/",
            api_key=config.api_key,
        )
        self.reports = _ReportsClient(
            base_api_path=config.base_api_path,
            api_version=config.api_version,
            path="reports/",
            api_key=config.api_key,
        )
        self.standups = _StandupsClient(
            base_api_path=config.base_api_path,
            api_version=config.api_version,
            path="standups/",
            api_key=config.api_key,
        )
        self.async_teams = _TeamsAsyncClient(
            base_api_path=config.base_api_path,
            api_version=config.api_version,
            path="teams/",
            api_key=config.api_key,
        )
        self.async_reports = _ReportsAsyncClient(
            base_api_path=config.base_api_path,
            api_version=config.api_version,
            path="reports/",
            api_key=config.api_key,
        )
        self.async_standups = _StandupsAsyncClient(
            base_api_path=config.base_api_path,
            api_version=config.api_version,
            path="standups/",
            api_key=config.api_key,
        )

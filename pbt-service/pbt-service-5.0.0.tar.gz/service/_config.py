"""Environment config factory.

Use cases:
    CI/CD & Docker etc:
        Set the config through environment variables in any convenient way
    Develop and tests:
        create local `.env` consider .env.example for auto load
        create local `.env.test` consider .env.example for local test config

"""

from typing import Any, Sequence, Optional
from pathlib import Path
from pydantic import BaseSettings, Field

from . import fn
from .i18n import locales
from .ext import api

from ._sentry import Env


class Config(BaseSettings):
    """Environment service config."""

    secret: str

    service_host: str
    service_port: int

    service_name: str = 'Service'
    service_info: str = 'Service information'

    environment: Env = Field(default=Env.develop)
    debug: bool = Field(default_factory=fn.is_debug)
    testing: bool = Field(default_factory=fn.is_testing)

    routers: Sequence[api.Router] = Field(default_factory=list)
    middleware: Sequence[Any] = Field(default_factory=list)

    sentry_dsn: Optional[str]
    log_config: Path = Field(default_factory=fn.log_config_path)

    locales: Sequence[str] = locales

    skip_doc: bool = False
    rpc_mode: bool = False

    @staticmethod
    def create(
        routers: Sequence[api.Router] = None,
        middleware: Sequence[Any] = None,
        **options,  # noqa:
    ):
        """Create from env with runtime."""
        return Config(
            routers=routers if routers else [],
            middleware=middleware if middleware else [],
        )

    class Config:
        """Config meta."""

        case_sensitive = False
        validate_all = True


all = ('Config', 'Env')

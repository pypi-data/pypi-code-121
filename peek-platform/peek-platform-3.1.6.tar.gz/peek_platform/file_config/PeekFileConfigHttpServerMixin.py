import logging
import os
from typing import Optional

from jsoncfg.value_mappers import require_string, require_bool, require_integer
from peek_platform.file_config.PeekFileConfigPlatformMixin import (
    PeekFileConfigPlatformMixin,
)

logger = logging.getLogger(__name__)


class PeekFileConfigHttpMixin:
    def __init__(
        self, config: PeekFileConfigPlatformMixin, name: str, defaultPort: int
    ):
        self._config = config
        self._name = name
        self._defaultPort = defaultPort

    ### SERVER SECTION ###
    @property
    def sitePort(self) -> int:
        with self._config._cfg as c:
            return c.httpServer[self._name].sitePort(self._defaultPort, require_integer)

    @property
    def enableHttps(self) -> int:
        with self._config._cfg as c:
            return c.httpServer[self._name].enableHttps(False, require_bool)

    @property
    def redirectFromHttpPort(self) -> int:
        with self._config._cfg as c:
            return c.httpServer[self._name].redirectFromHttpPort(None)

    @property
    def sslBundleFilePath(self) -> Optional[str]:
        default = os.path.join(self._config._homePath, "peek-ssl-bundle.pem")
        with self._config._cfg as c:
            file = c.httpServer[self._name].sslBundleFilePath(default, require_string)
            if os.path.exists(file):
                return file
            return None

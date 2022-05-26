from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from sym.shared.cli.data.global_options_base import GlobalOptionsBase

from sym.flow.cli.helpers.constants import DEFAULT_API_URL, DEFAULT_AUTH_URL


@dataclass
class GlobalOptions(GlobalOptionsBase):
    api_url: str = DEFAULT_API_URL
    auth_url: str = DEFAULT_AUTH_URL
    access_token: Optional[str] = None

    @property
    def sym_api(self):
        from sym.flow.cli.helpers.api import SymAPI

        return SymAPI(self.api_url, self.access_token)

    def set_access_token(self, sym_jwt):
        self.access_token = sym_jwt.strip()

    def set_api_url(self, url):
        url = url.rstrip("/")
        if not self._validate_url(url):
            raise ValueError("Specified API URL '{}' is not valid.".format(url))

        self.api_url = url

    def set_auth_url(self, url):
        url = url.rstrip("/")
        if not self._validate_url(url):
            raise ValueError("Specified Auth URL '{}' is not valid.".format(url))

        self.auth_url = url

    def _validate_url(self, url):
        try:
            parts = urlparse(url)
            if parts.scheme not in ("http", "https"):
                return False
            if not parts.netloc:
                return False
            if parts.fragment or parts.query or parts.params:
                return False
            return True
        except ValueError:
            return False

    def to_dict(self):
        return {
            **super().to_dict(),
            "api_url": self.api_url,
            "auth_url": self.auth_url,
        }

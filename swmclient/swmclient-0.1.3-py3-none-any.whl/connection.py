"""Contains class required to establish connections over SwmQuery"""

import pathlib
import ssl
from typing import Any, Dict, Optional, Union

from .generated.client import AuthenticatedClient


class SwmConnection:

    _client = None

    def __init__(self, url: str, key_file: str, cert_file: str, ca_file: str) -> None:
        self._ca_file = pathlib.Path(ca_file).expanduser()
        self._key_file = pathlib.Path(key_file).expanduser()
        self._cert_file = pathlib.Path(cert_file).expanduser()
        self._url = url

        if not self._ca_file.exists():
            raise FileNotFoundError(f"No such file: {self._ca_file}")
        if not self._key_file.exists():
            raise FileNotFoundError(f"No such file: {self._key_file}")
        if not self._cert_file.exists():
            raise FileNotFoundError(f"No such file: {self._cert_file}")

    def establish(self, headers: Dict[str, Any], password: Union[str, None] = None) -> None:
        if not self._client:
            ssl_context: ssl.SSLContext = ssl.create_default_context()
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            ssl_context.load_verify_locations(cafile=str(self._ca_file))
            ssl_context.load_cert_chain(certfile=str(self._cert_file), keyfile=str(self._key_file), password=password)
            self._client = AuthenticatedClient(base_url=self._url, headers=headers, verify_ssl=ssl_context, token="swm")

    def get_auth_client(self) -> Optional[AuthenticatedClient]:
        return self._client

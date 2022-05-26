import re
import logging
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from dataclasses import dataclass
from toml import load, dump
from openapi_client import Configuration, ApiClient
from openapi_client.models import KeyLoginParams, UserData
from openapi_client.apis import DefaultApi
from leapcli.exceptions import MalformedKeys, KeysMixedUp, LoginFailed, CredentialsNotFound, InvalidOrgName, InvalidUrl
from leapcli.project import Project

CREDENTIALS_FILENAME = 'credentials.toml'

TENSORLEAP_BACKEND_DOMAIN = 'tensorleap.ai'

VALID_ORG_REGEX = r'^[a-zA-Z0-9][a-zA-Z0-9\-]+[a-zA-Z0-9]$'


_log = logging.getLogger(__name__)


@dataclass
class Credentials:
    api_id: str
    api_key: str
    api_url: str


class _Authenticator:
    def __init__(self):
        self._credentials: Optional[Credentials] = None
        self._api_client: Optional[DefaultApi] = None
        self.user: Optional[UserData] = None
        self.cookie: Optional[str] = None
        self.is_initialized = False

    def initialize(self, credentials: Optional[Credentials] = None, should_write_credentials=False):
        if self.is_initialized:
            return

        self._credentials = credentials
        if not self._credentials:
            self._credentials = _Authenticator.read_credentials()

        if not self._credentials:
            raise CredentialsNotFound()

        if not _Authenticator.is_valid_api_id(self._credentials.api_id):
            if _Authenticator.is_valid_api_key(self._credentials.api_id):
                raise KeysMixedUp()
            raise MalformedKeys()

        if not _Authenticator.is_valid_api_key(self._credentials.api_key):
            raise MalformedKeys()

        if not _Authenticator._is_valid_url(self._credentials.api_url):
            raise InvalidUrl()

        self.authenticated_api()

        if should_write_credentials:
            self.write_credentials(self._credentials)

        self.is_initialized = True

    @staticmethod
    def redact_key(key: str) -> str:
        assert len(key) > 3
        # Mask the first 19 characters of a key
        return '*' * 19 + key[-3:]

    @staticmethod
    def is_valid_api_key(api_key: str) -> bool:
        return re.match(r'^k0\w{20}$', api_key) is not None

    @staticmethod
    def is_valid_api_id(api_id: str) -> bool:
        return re.match(r'^i0\w{20}$', api_id) is not None

    @staticmethod
    def credentials_file_path() -> Path:
        return Project.config_dir().joinpath(CREDENTIALS_FILENAME)

    @staticmethod
    def has_credentials() -> bool:
        credentials = _Authenticator.read_credentials()
        return credentials is not None

    @staticmethod
    def read_credentials() -> Optional[Credentials]:
        # TODO: more robust handling of corrupted file
        path = _Authenticator.credentials_file_path()
        if path.is_file():
            _log.debug('reading credentials from %s', path)
            with path.open('r') as f:
                dictionary = load(f)
                return Credentials(**dictionary)
        return None

    @staticmethod
    def write_credentials(credentials: Credentials) -> None:
        _log.info('writing credentials')
        with _Authenticator.credentials_file_path().open('w') as f:
            return dump(dict(credentials.__dict__), f)

    @staticmethod
    def validate_org_name(name: str) -> None:
        if not name or re.match(VALID_ORG_REGEX, name) is None \
                or '--' in name or len(name) < 3:
            raise InvalidOrgName()

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        result = urlparse(url)
        return all([result.scheme, result.netloc])

    @staticmethod
    def validate_organization_or_url(organization_or_url: str):
        if not _Authenticator._is_valid_url(organization_or_url):
            _Authenticator.validate_org_name(organization_or_url)

    def detect_backend_url(self) -> str:
        return self._credentials.api_url

    def key_login(self) -> None:
        host = self.detect_backend_url()
        cfg = Configuration(host=host)
        unauthenticated_client = ApiClient(cfg)
        api = DefaultApi(unauthenticated_client)
        params = KeyLoginParams(self._credentials.api_id, self._credentials.api_key)
        user, status, headers = api.key_login(params, _return_http_data_only=False)
        if status != 200 or not 'Set-Cookie' in headers:
            _log.info('login failed with api_id: %s, api_key: %s', self._credentials.api_id,
                      self.redact_key(self._credentials.api_key))
            raise LoginFailed()
        self.user = user
        self.cookie = headers['Set-Cookie']

    def logged_in(self) -> bool:
        return self.cookie is not None

    def authenticated_api(self) -> DefaultApi:
        if not self.logged_in():
            self.key_login()
        host = self.detect_backend_url()
        cfg = Configuration(host=host)
        cookie_client = ApiClient(cfg, cookie=self.cookie)

        return DefaultApi(cookie_client)


Authenticator = _Authenticator()

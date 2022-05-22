import logging
from typing import Optional

import keyring
from keyring.backends import fail

_logger = logging.getLogger(__name__)


class PasswordManager:
    _SERVICE_NAME: str = "classiqTokenService"
    _ACCESS_TOKEN_KEY: str = "classiqTokenAccount"
    _REFRESH_TOKEN_KEY: str = "classiqRefershTokenAccount"

    def __init__(self) -> None:
        self._pm_available = is_password_manager_available()

    @property
    def access_token(self) -> Optional[str]:
        return self._get(key=self._ACCESS_TOKEN_KEY)

    @access_token.setter
    def access_token(self, access_token: Optional[str]) -> None:
        self._set(key=self._ACCESS_TOKEN_KEY, value=access_token)

    @property
    def refresh_token(self) -> Optional[str]:
        return self._get(key=self._REFRESH_TOKEN_KEY)

    @refresh_token.setter
    def refresh_token(self, refresh_token: Optional[str]) -> None:
        self._set(key=self._REFRESH_TOKEN_KEY, value=refresh_token)

    def _get(self, key: str) -> Optional[str]:
        if not self._pm_available:
            _logger.info("Called get with unavailable password manager")
            return None
        return keyring.get_password(service_name=self._SERVICE_NAME, username=key)

    def _set(self, key: str, value: Optional[str]) -> None:
        if not self._pm_available:
            _logger.info("Called set with unavailable password manager")
            return

        if value is None:
            self._clear(key)
            return
        keyring.set_password(
            service_name=self._SERVICE_NAME,
            username=key,
            password=value,
        )

    def _clear(self, key: str) -> None:
        if not self._pm_available:
            _logger.info("Called clear with unavailable password manager")
            return

        keyring.delete_password(
            service_name=self._SERVICE_NAME,
            username=key,
        )


class DummyPasswordManager(PasswordManager):
    def _get(self, key: str) -> Optional[str]:
        return None

    def _set(self, key: str, value: Optional[str]) -> None:
        return

    def _clear(self, key: str) -> None:
        return


PASSWORD_MANAGER_AVAILABLE = None


def is_password_manager_available() -> bool:
    global PASSWORD_MANAGER_AVAILABLE
    if PASSWORD_MANAGER_AVAILABLE is None:
        PASSWORD_MANAGER_AVAILABLE = not isinstance(keyring.get_keyring(), fail.Keyring)

    return PASSWORD_MANAGER_AVAILABLE

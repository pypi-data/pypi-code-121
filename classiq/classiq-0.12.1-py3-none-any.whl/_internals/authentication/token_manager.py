import argparse
import logging
import threading
import warnings
from typing import Optional

from classiq._internals.authentication import password_manager as pm
from classiq._internals.authentication.auth0 import Auth0
from classiq._internals.authentication.device import DeviceRegistrar, Tokens
from classiq.exceptions import ClassiqAuthenticationError

_logger = logging.getLogger(__name__)


class TokenManager:
    def __init__(self, password_manager: Optional[pm.PasswordManager] = None):
        if password_manager is None:
            password_manager = self._make_password_manager()
        # We use threading.Lock instead of asyncio.Lock because the latter is coupled
        # to a specific event loop, which is undesirable
        self._lock = threading.Lock()
        self._password_manager: pm.PasswordManager = password_manager
        self._access_token: Optional[str] = self._password_manager.access_token
        self._refresh_token: Optional[str] = self._password_manager.refresh_token
        if self._access_token is None and self._refresh_token is not None:
            _logger.info(
                "Inconsistent state, access token is absent and refresh token is present."
            )

    @classmethod
    def _make_password_manager(cls) -> pm.PasswordManager:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--skip-authentication", action="store_true", required=False
        )
        args, _ = parser.parse_known_args()

        if args.skip_authentication:
            return pm.DummyPasswordManager()
        else:
            return pm.PasswordManager()

    def get_access_token(self) -> Optional[str]:
        return self._access_token

    async def _refresh(self) -> None:
        assert self._refresh_token is not None
        tokens = await Auth0.refresh_access_token(self._refresh_token)
        self._save_tokens(tokens)

    async def update_expired_access_token(self) -> None:
        if self._refresh_token is not None:
            await self._refresh()
            return
        self._clear_tokens()
        raise ClassiqAuthenticationError(
            "Please call `classiq.authenticate()` to manually log in."
        )

    async def manual_authentication(self, overwrite: bool) -> None:
        if self._refresh_token is None:
            await self._authentication_helper()
            return
        # Note, this function warns using warnings because https://stackoverflow.com/q/9595009
        if overwrite:
            warnings.warn(
                "Overwriting an existing refresh token should only be done if "
                "it is compromised. Make sure this operation is necessary, "
                "and if not, remove the call to device registration."
            )
            await self._authentication_helper()
        else:
            warnings.warn(
                "Device is already registered.\nGenerating a new refresh token should only "
                "be done if the current refresh token is compromised.\nTo do so, set the "
                "overwrite parameter to true"
            )
            if self._access_token is None:
                await self._refresh()

    def _save_tokens(
        self, tokens: Tokens, force_override_refresh_token: bool = False
    ) -> None:
        with self._lock:
            self._access_token = tokens.access_token
            self._password_manager.access_token = tokens.access_token
            if tokens.refresh_token is not None or force_override_refresh_token:
                self._refresh_token = tokens.refresh_token
                self._password_manager.refresh_token = tokens.refresh_token

    def _clear_tokens(self) -> None:
        with self._lock:
            self._access_token = None
            self._password_manager.access_token = None
            self._refresh_token = None
            self._password_manager.refresh_token = None

    async def _authentication_helper(self) -> None:
        # TODO: consider using refresh token rotation
        #  (https://auth0.com/docs/tokens/refresh-tokens/refresh-token-rotation)
        tokens = await DeviceRegistrar.register(
            get_refresh_token=pm.is_password_manager_available()
        )
        self._save_tokens(tokens, force_override_refresh_token=True)

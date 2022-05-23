import json
import os.path
import time
import webbrowser
import logging
from datetime import datetime
from typing import Optional
from autoretouch.api_client.model import Credentials, DeviceCodeResponse

logger = logging.getLogger("autoretouch-python-client")

__all__ = [
    "Authenticator"
]


def _open_browser_for_verification(device_code_response: DeviceCodeResponse):
    logger.info(
        f"Open verification url {device_code_response.verification_uri_complete} in the browser "
        f"and confirm the user code '{device_code_response.user_code}'."
    )
    try:
        webbrowser.open(device_code_response.verification_uri_complete)
    except Exception as e:
        logger.error("Failed to open the browser. Exception was :")
        logger.error(str(e))


def _poll_credentials_while_user_confirm(
    api: "AutoRetouchAPIClient", device_code_response: DeviceCodeResponse
) -> Credentials:
    seconds_waited = 0
    logger.info("Waiting for user confirmation...")
    while seconds_waited < device_code_response.expires_in:
        try:
            return api.get_credentials_from_device_code(
                device_code_response.device_code
            )
        except:
            seconds_waited += device_code_response.interval
            time.sleep(device_code_response.interval)
    raise RuntimeError(f"Device Code not confirmed after {seconds_waited} seconds")


class Authenticator:
    def __init__(
        self,
        api: "AutoRetouchAPIClient",
        credentials_path: Optional[str] = None,
        refresh_token: Optional[str] = None,
        save_credentials: bool = True,
    ):
        self.api: "AutoRetouchAPIClient" = api
        self.credentials_path: str = credentials_path
        self.refresh_token: str = refresh_token
        self.save_credentials: bool = save_credentials
        self.credentials: Optional[Credentials] = None

    def authenticate(self):
        if self.refresh_token is not None:
            logger.info("authenticating from refresh token")
            self.credentials = self.api.get_credentials_from_refresh_token(
                self.refresh_token
            )
        elif self.credentials_path is not None and os.path.isfile(self.credentials_path):
            logger.debug(f"found stored credentials at {self.credentials_path}")
            self.credentials = self._read_credentials_file()
            self._refresh_credentials_if_expired()
        else:
            logger.info(f"authenticating with new device flow")
            device_code_response = self.api.get_device_code()
            _open_browser_for_verification(device_code_response)
            self.credentials = _poll_credentials_while_user_confirm(
                self.api, device_code_response
            )
            logger.info("Login was successful")
            self._save_credentials()
        return self

    @property
    def access_token(self):
        return self.credentials.access_token

    @property
    def token_expired(self) -> bool:
        now = int(datetime.utcnow().timestamp())
        return now + 30 > self.credentials.expires_at

    def refresh_credentials(self):
        logger.info("refreshing credentials")
        self.credentials = self.api.get_credentials_from_refresh_token(
            refresh_token=self.credentials.refresh_token
        )
        self._save_credentials()
        return self

    def revoke_refresh_token(self) -> int:
        return self.api.revoke_refresh_token(self.credentials.refresh_token)

    def _refresh_credentials_if_expired(self):
        if not self.credentials.access_token or self.token_expired:
            logger.info("access token expired, refreshing ...")
            self.refresh_credentials()

    def _read_credentials_file(self) -> Credentials:
        with open(self.credentials_path, "r") as credentials_file:
            return Credentials(**json.load(credentials_file))

    def _save_credentials(self):
        if not self.save_credentials:
            return
        if not self.credentials_path:
            logger.warning("Can not save credentials, no credentials path given")
            return
        logger.info(f"successfully stored credentials at {self.credentials_path}")
        if not os.path.exists(os.path.dirname(self.credentials_path)):
            os.makedirs(os.path.dirname(self.credentials_path), exist_ok=True)
        with open(self.credentials_path, "w") as credentials_file:
            json.dump(
                self.credentials,
                credentials_file,
                default=lambda o: o.__dict__,
                indent=4,
            )

    def logout(self):
        if os.path.isfile(self.credentials_path):
            os.remove(self.credentials_path)
            logger.info(f"removed credentials at {self.credentials_path}")
        self.credentials = None
        self.refresh_token = None
        return self

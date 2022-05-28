import logging
import os
import typing

from mlfoundry import env_vars
from mlfoundry.login import get_stored_api_key
from mlfoundry.tracking.auth_service import AuthService

logger = logging.getLogger(__name__)


class Session:
    def __init__(self, auth_service: AuthService, tracking_uri: str):
        self.auth_service: AuthService = auth_service
        self.tracking_uri = tracking_uri

    def init_session(
        self,
        api_key: typing.Optional[str] = None,
    ):
        final_api_key = (
            api_key
            or os.getenv(env_vars.API_KEY)
            or get_stored_api_key(self.tracking_uri)
        )

        if final_api_key is None:
            # if API key is not present,
            # then take a look if MLFLOW_TRACKING_TOKEN itself has been set.
            # this will be used in sfy.
            existing_token = os.getenv(env_vars.TRACKING_TOKEN, "")
            if existing_token:
                logger.info("API key is not present. Using existing tracking token")
                return
            logger.info(
                "Session was not set as api key was neither passed, not set via env var"
            )
            return

        token = self.auth_service.get_token(api_key=final_api_key)
        os.environ[env_vars.TRACKING_TOKEN] = token

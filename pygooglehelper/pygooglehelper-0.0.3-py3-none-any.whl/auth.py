import os
import pickle
import logging
from typing import List
from functools import partial

from pytconf import register_function

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from pygooglehelper.util import str_list_md5, ensure_folder
from pygooglehelper.configs import ConfigAuth
from pygooglehelper.static import LOGGER_NAME


def get_credentials(
    app_name: str,
    scopes: List[str],
    host: str = ConfigAuth.host,
    port: int = ConfigAuth.port,
    authorization_prompt_message: str = ConfigAuth.authorization_prompt_message,
    force: bool = ConfigAuth.force,
) -> Credentials:
    """
    The file token.pickle stores the user's access and refresh tokens, and is
    created automatically when the authorization flow completes for the first
    time.
    It is also updated when refreshing or when the scopes change.
    """
    logger = logging.getLogger(LOGGER_NAME)
    credentials = None
    md5_of_scopes = str_list_md5(scopes)
    token_filename = os.path.expanduser(f"~/.config/google_tokens/token-{md5_of_scopes}.pickle")
    logger.debug(f"reading credentials from [{token_filename}]")
    if force:
        if os.access(token_filename, os.R_OK):
            os.unlink(token_filename)
    if os.access(token_filename, os.R_OK):
        with open(token_filename, "rb") as token_stream:
            credentials = pickle.load(token_stream)
    if credentials is None or not credentials.valid:
        if credentials is not None:
            if credentials.expired and credentials.refresh_token:
                logger.debug("refreshing credentials")
                credentials.refresh(Request())
        else:
            client_secret = os.path.expanduser(f"~/.config/{app_name}/client_secret.json")
            if not os.path.isfile(client_secret):
                raise IOError(f"missing client secret file [{client_secret}] for application [{app_name}]")
            logger.debug(f"creating credentials from client secret at {client_secret}")
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret, scopes,
            )
            credentials = flow.run_local_server(
                host=host,
                port=port,
                authorization_prompt_message=authorization_prompt_message,
            )
        logger.debug(f"creating a new token file [{token_filename}]")
        # there is a need to remove the old file if it exists since we chmod them so we can't overwrite them
        if os.access(token_filename, os.R_OK):
            os.unlink(token_filename)
        ensure_folder(token_filename)
        with open(token_filename, "wb") as token_stream:
            os.fchmod(token_stream.fileno(), 0o400)
            pickle.dump(credentials, token_stream)
    else:
        logger.debug(f"have valid credentials in [{token_filename}]")
    return credentials


def register_functions(scopes: List[str], app_name: str):
    register_function(
        function=partial(
            get_credentials,
            scopes=scopes,
            app_name=app_name
        ),
        description="Do the authentication procedure and get token for your app",
        name="auth",
        configs=[ConfigAuth],
    )

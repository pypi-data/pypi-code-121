from typing import Optional

import rich_click as click

from servicefoundry.internal.clients.auth_service_client import AuthServiceClient
from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.console import console
from servicefoundry.internal.const import DEFAULT_TENANT_ID, SESSION_FILE
from servicefoundry.internal.exceptions import BadRequestException
from servicefoundry.internal.lib.messages import (
    PROMPT_ALREADY_LOGGED_OUT,
    PROMPT_LOGIN_INFO,
    PROMPT_LOGIN_SUCCESSFUL,
    PROMPT_LOGOUT_SUCCESSFUL,
)
from servicefoundry.internal.model.entity import Cluster
from servicefoundry.internal.model.session import ServiceFoundrySession
from servicefoundry.internal.session_factory import get_session, logout_session


def _set_cluster_if_only_one():
    client = ServiceFoundryServiceClient.get_client()
    clusters = client.list_cluster()
    if len(clusters) == 1:
        cluster = Cluster.from_dict(clusters[0])
        client.session.set_cluster(cluster.to_dict_for_session())
        client.session.save_session()


def _login_using_device_code() -> ServiceFoundrySession:
    auth_client = AuthServiceClient()
    url, user_code, device_code = auth_client.get_device_code(DEFAULT_TENANT_ID)
    console.print(f"Login Code: {user_code}")
    console.print(
        f"Waiting for authentication. Go to the following url to complete the authentication: {url}"
    )
    click.launch(url)
    session = auth_client.poll_for_auth(DEFAULT_TENANT_ID, device_code)
    session.save_session()
    console.print(PROMPT_LOGIN_SUCCESSFUL)
    console.print(f"Session file stored at {SESSION_FILE}")
    return session


def _login_with_api_key(api_key: str) -> ServiceFoundrySession:
    session = AuthServiceClient().login_with_api_token(
        client_id=DEFAULT_TENANT_ID, api_key=api_key
    )
    console.print(PROMPT_LOGIN_SUCCESSFUL)
    return session


def login(api_key: Optional[str] = None, interactive: bool = False):
    try:
        session = get_session()
    except BadRequestException:
        if interactive:
            session = _login_using_device_code()
        else:
            if not api_key:
                raise ValueError("`api_key` is required in non interactive mode")
            session = _login_with_api_key(api_key=api_key)
        # TODO (chiragjn): Done to have user make one less choice till we only have one cluster on backend
        _set_cluster_if_only_one()
    user = session.get_user_details()
    console.print(
        PROMPT_LOGIN_INFO.format(username=user["username"], email=user["email"])
    )


def logout():
    try:
        logout_session()
    except BadRequestException:
        console.print(PROMPT_ALREADY_LOGGED_OUT)
    else:
        console.print(PROMPT_LOGOUT_SUCCESSFUL)

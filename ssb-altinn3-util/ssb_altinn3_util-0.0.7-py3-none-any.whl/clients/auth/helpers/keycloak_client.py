import json

import ssb_altinn3_util.clients.auth.helpers.http_helper as http_client
from ssb_altinn3_util.clients.decorators.simple_exception_wrapper import (
    exception_handler,
)


class KeycloakClient:
    def __init__(self, platform_environment: str):
        self.token_endpoint = "auth/realms/ssb/protocol/openid-connect/token"
        self.base_url = f"https://keycloak.{platform_environment}-bip-app.ssb.no/"

    @exception_handler("Keycloak Client")
    def get_token(self, maskinport_client_id: str, client_secret: str) -> str:
        url = self.base_url + self.token_endpoint
        client_id = f"maskinporten-{maskinport_client_id}"
        request_data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        content = http_client.post(url, headers, request_data)

        token: str = json.loads(content)["access_token"]

        return token

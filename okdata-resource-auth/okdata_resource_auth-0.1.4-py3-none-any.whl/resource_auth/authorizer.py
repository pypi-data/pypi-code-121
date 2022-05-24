import os
import urllib.parse

from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class ResourceAuthorizer:
    def __init__(
        self, keycloak_server_url=None, keycloak_realm=None, resource_server_name=None
    ):
        self.keycloak_server_url = keycloak_server_url or os.environ["KEYCLOAK_SERVER"]
        self.keycloak_realm = keycloak_realm or os.environ["KEYCLOAK_REALM"]
        self.resource_server_name = (
            resource_server_name or os.environ["RESOURCE_SERVER_CLIENT_ID"]
        )
        self.keycloak_timeout = (
            int(os.environ.get("KEYCLOAK_TIMEOUT_MS", 2000)) / 1000.0
        )

    def has_access(self, bearer_token, scope, resource_name=None, use_whitelist=False):
        payload = [
            ("grant_type", "urn:ietf:params:oauth:grant-type:uma-ticket"),
            ("audience", self.resource_server_name),
            ("response_mode", "decision"),
            ("permission", "#".join([resource_name or "", scope])),
        ]
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        session = Session()
        retry = Retry(total=3, backoff_factor=0.5, allowed_methods=None)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        response = session.post(
            url=urllib.parse.urljoin(
                self.keycloak_server_url,
                f"/auth/realms/{self.keycloak_realm}/protocol/openid-connect/token",
            ),
            data=payload,
            headers=headers,
            timeout=self.keycloak_timeout,
        )

        has_access = False
        if response.status_code == 200:
            has_access = response.json()["result"]
        elif 400 <= response.status_code < 500:
            pass
        else:
            response.raise_for_status()

        if not has_access and use_whitelist:
            return self.has_access(
                bearer_token, scope="okdata:dataset:whitelist", use_whitelist=False
            )

        return has_access

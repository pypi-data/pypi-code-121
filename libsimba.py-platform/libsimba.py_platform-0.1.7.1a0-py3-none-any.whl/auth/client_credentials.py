import requests

from libsimba.auth import AuthProvider
from libsimba.settings import (
    CLIENT_ID,
    CLIENT_SECRET,
    SCOPE,
    BASE_AUTH_URL,
    AUTH_ENDPOINT,
    BASE_API_URL,
)
from libsimba.utils import build_url, save_token, get_saved_token

import logging

log = logging.getLogger(__name__)


class ClientCredentials(AuthProvider):

    access_token = None

    @staticmethod
    def main():
        ClientCredentials.login()

    @staticmethod
    def login():
        if ClientCredentials._is_authenticated():
            return ClientCredentials.access_token
        log.info("Failed ClientCredentials._is_authenticated()")

        payload = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": SCOPE,
        }

        access_token = None
        try:
            log.info("Redoing auth")
            auth_url = build_url(BASE_AUTH_URL, "{}token".format(AUTH_ENDPOINT), {})
            r = requests.post(auth_url, data=payload, allow_redirects=True)

            access_token = r.json()["access_token"]
        except Exception as e:
            log.error(e)
            return None

        if access_token is not None:
            save_token(client_id=CLIENT_ID, token_data=r.json())

        ClientCredentials.access_token = access_token

        return access_token

    @staticmethod
    def _is_authenticated():
        if ClientCredentials.access_token is not None:
            return True
        try:
            access_token = get_saved_token(CLIENT_ID)["access_token"]
        except:
            return False

        whoami_url = build_url(BASE_API_URL, "/user/whoami/", {})
        try:
            r = requests.get(
                whoami_url, headers={"Authorization": "Bearer {}".format(access_token)}
            )
            if r.status_code != 200:
                return False
            ClientCredentials.access_token = access_token
            return True
        except:
            return False


if __name__ == "__main__":
    ClientCredentials.main()

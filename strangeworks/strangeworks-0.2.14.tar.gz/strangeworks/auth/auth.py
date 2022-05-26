import os, requests, time


class SWAuth(object):
    """
    SWAuth allows for a user to authenticate utilizing
    their standard Strangeworks login via Auth0
    """

    def __init__(
        self,
        auth0_url: str = "https://auth.quantumcomputing.com",
        auth0_client_id: str = "TZN22C2vD1OW8pPPAomhgWqiKxpgUKnJ",
        auth0_audience: str = "https://strangeworks.com/login",
        timeout_secs: int = 300,
        frequency_secs: int = 5,
    ):
        self.auth0_url = (
            os.getenv("STRANGEWORKS_AUTH_URL", default=None)
            if auth0_url is None
            else auth0_url
        )
        self.auth0_client_id = (
            os.getenv("STRANGEWORKS_AUTH_CLIENT_ID", default=None)
            if auth0_client_id is None
            else auth0_client_id
        )
        self.auth0_audience = (
            os.getenv("STRANGEWORKS_AUTH_AUDIENCE", default=None)
            if auth0_audience is None
            else auth0_audience
        )
        self.timeout_secs = (
            os.getenv("STRANGEWORKS_AUTH_TIMEOUT_SECS", default=None)
            if timeout_secs is None
            else timeout_secs
        )
        self.frequency_secs = (
            os.getenv("STRANGEWORKS_AUTH_FREQUENCY", default=None)
            if frequency_secs is None
            else frequency_secs
        )

    def _get_device_code(self):
        url = f"{self.auth0_url}/oauth/device/code"

        res = requests.post(
            url=url,
            data={
                "client_id": self.auth0_client_id,
                "audience": self.auth0_audience,
                "scope": "openid",
            },
            headers={"ContentType": "application/json; charset=utf-8"},
        )
        return res.json()

    def _get_token_loop(self, device_code):
        timeout = time.time() + self.timeout_secs

        while True:
            time.sleep(self.frequency_secs)
            res = self._get_token(device_code)

            if res.status_code == requests.codes.ok:
                raw = res.json()
                return (raw["access_token"], raw["id_token"])

            if time.time() > timeout:
                break

        return None

    def _get_token(self, device_code):
        url = f"{self.auth0_url}/oauth/token"
        res = requests.post(
            url=url,
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": device_code,
                "client_id": self.auth0_client_id,
            },
            headers={"ContentType": "application/json; charset=utf-8"},
        )
        return res


def Login():
    c = SWAuth()
    dc = c._get_device_code()
    print(
        f"Complete authentication by visiting this url: {dc['verification_uri_complete']}"
    )
    return c._get_token_loop(dc["device_code"])

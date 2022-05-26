import requests
from strangeworks.errors.error import StrangeworksError


class StrangeworksRestClient:
    __default_host = "https://api.quantumcomputing.com"

    def __init__(
        self,
        headers: dict = None,
        host: str = None,
        username: str = None,
        api_key: str = None,
        auth_token: str = None,
        session: requests.Session = None,
        default_timeout: int = None,
        version: str = "",
    ):
        self.__username = username
        self.__api_key = api_key
        self.headers = headers
        self.__auth_token = auth_token
        self.__default_timeout = default_timeout
        if headers is None:
            self.headers = {
                "X-Strangeworks-API-Version": "0",
                "X-Strangeworks-Client-ID": "strangeworks-sdk-python",
                "X-Strangeworks-Client-Version": version,
                "x-strangeworks-provider-account": "",
                "Authorization": f"Bearer {auth_token}",
            }

        self.__host = host
        if host is None:
            self.__host = self.__default_host

        self.__session = session
        if session is None:
            self.__session = requests.Session()

        # set up re-authentication hook!
        self.__session.hooks["response"].append(self.__reauthenticate)

        # if a user has passed in authentication vars but has not generated a token
        # do so now, otherwise pass along
        if (
            self.__auth_token is None
            and self.__username is not None
            and self.__api_key is not None
        ):
            self.authenticate(self.__username, self.__api_key)

    def post(
        self,
        url: str = "",
        json: dict = None,
        files: dict = None,
        expected_response: int = 200,
    ):
        r = self.__session.post(
            url=f"{self.__host}{url}",
            json=json,
            files=files,
            timeout=self.__default_timeout,
        )
        res = r.json()
        if r.status_code != expected_response:
            self.__parse_error(r)
        return res

    def delete(
        self,
        url: str = "",
        expected_response: int = 200,
    ):
        r = self.__session.delete(
            url=f"{self.__host}{url}",
            timeout=self.__default_timeout,
        )
        if r.status_code != expected_response:
            self.__parse_error(r)

    def get(
        self,
        url: str = "",
    ) -> dict:
        r = self.__session.get(url=f"{self.__host}{url}")
        res = r.json()
        if r.status_code != 200:
            self.__parse_error(r)
        return res

    def authenticate(self, username: str = None, api_key: str = None):
        if username is None or len(username) == 0:
            raise StrangeworksError.authentication_error(
                message="Missing username. Use strangeworks.authenticate(username, api_key) and try again.",
            )
        if api_key is None or len(api_key) == 0:
            raise StrangeworksError.authentication_error(
                message="Missing api_key. Use strangeworks.authenticate(username, api_key) and try again.",
            )

        # Exchange api key for token to use with local SDK requests
        url = f"{self.__host}/users/{username}/token"
        self.headers["x-strangeworks-api-key"] = api_key
        res = requests.post(url, json={}, headers=self.headers, timeout=30)
        if not res.ok:
            print(
                f"Auth error: status code {res.status_code}, text {res.text} URL: {url}"
            )
            raise StrangeworksError.authentication_error(
                f"Error getting token: {res.status_code} text: {res.text} URL: {url}"
            )
        response = res.json()
        self.__auth_token = response["accessToken"]
        self.__session.auth = self.__StrangeworksAuth(token=self.__auth_token)
        self.__username = username
        self.__api_key = api_key

    def __reauthenticate(self, res: requests.Response = None, *args, **kwargs):
        if res.status_code == requests.codes.unauthorized:
            seen_before_header = "X-SW-SDK-Re-Auth"
            # we've tried once before but no luck. maybe they've changed their api_key?
            if res.request.headers.get(seen_before_header):
                raise StrangeworksError(
                    "Unable to re-authenticate your request. Utilize strangeworks.authenticate(username, api_key) with your most up to date credentials and try again."
                )
            self.authenticate(self.__username, self.__api_key)
            # self.session.send just sends the prepared request, so we must manually ensure that the new token is part of the header
            res.request.headers["Authorization"] = f"Bearer {self.__auth_token}"
            res.request.headers[seen_before_header] = True
            return self.__session.send(res.request)

    def __parse_error(self, response: requests.Response = None):
        print(f"Error from plugin: {response.text}, json: {response.json()}")
        error_payload = response.json()
        if "message" in error_payload and error_payload["message"] != "":
            raise StrangeworksError.bad_response(error_payload["message"])
        raise StrangeworksError.bad_response(
            f"Error status code: {response.status_code} text: {response.text}"
        )

    class __StrangeworksAuth(requests.auth.AuthBase):
        """
        StrangeworksAuth is used to authenticate requests to the Strangeworks
        server. Token used may be a regular Strangeworks auth token (same one
        used for API's, etc.) or a token obtained using the api key which is
        limited in scope.
        """

        def __init__(
            self,
            token: str = None,
        ):
            self.token = token

        def __call__(self, req):
            if self.token is None:
                raise StrangeworksError(
                    message="No authentication method detected. Utilize strangeworks.authenticate(username, api_key) and try again",
                )
            # utilize the authorization header with bearer token
            req.headers["Authorization"] = f"Bearer {self.token}"
            return req

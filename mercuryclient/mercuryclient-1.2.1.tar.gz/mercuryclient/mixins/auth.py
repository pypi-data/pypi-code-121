import time

import jwt

# Token validity threshold (in seconds). If token expires within the given
# threshold, we will get a new one access/refresh
REFRESH_TOKEN_THRESHOLD = 300
ACCESS_TOKEN_THRESHOLD = 120


class AuthMixin:
    """
    Mixin for client Authorization
    """

    def _authorize_client(self):
        """
        Authorize Mercury Client
        :return:
        """
        api = "api/v1/token/"

        if all([self.username, self.password]):
            data = {"username": self.username, "password": self.password}

            _, r = self._post_json_http_request(
                api, data=data, send_request_id=True, add_bearer_token=False
            )

            if r.status_code == 200:
                resp = r.json()
                self._access_token = resp["access"]
                self._refresh_token = resp["refresh"]
            else:
                raise Exception("Error Authorizing to Mercury")

    @staticmethod
    def is_token_valid(token, threshold):
        """
        Checks if a given token is valid past the threshold period
        :param token: string
        :param threshold: int
        :return:
        """
        decoded = jwt.decode(token, verify=False)
        return decoded["exp"] - int(time.time()) >= threshold

    def is_access_token_valid(self):
        if self._access_token:
            return self.is_token_valid(self._access_token, ACCESS_TOKEN_THRESHOLD)
        return False

    def is_refresh_token_valid(self):
        if self._refresh_token:
            return self.is_token_valid(self._refresh_token, REFRESH_TOKEN_THRESHOLD)
        return False

    @property
    def access_token(self):
        """
        Returns a valid access token
        :return:
        """
        if not self.is_access_token_valid():
            if self.is_refresh_token_valid():
                self.set_access_token()
            else:
                self._authorize_client()

        return self._access_token

    def set_access_token(self):
        """
        Sets the Access token using a valid refresh token
        :return:
        """
        api = "api/v1/token/refresh/"
        body = {"refresh": self._refresh_token}

        _, r = self._post_json_http_request(
            api, data=body, send_request_id=True, add_bearer_token=False
        )
        if r.status_code == 200:
            resp = r.json()
            self._access_token = resp["access"]
        else:
            raise Exception("Failed to get Access token")

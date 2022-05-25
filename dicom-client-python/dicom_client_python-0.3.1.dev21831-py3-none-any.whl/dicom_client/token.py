from threading import Lock
import jwt
import adal
import time


class TokenRefreshError(Exception):
    pass


class TokenCache(object):
    """Manages adding tokens to the request header, as well as refreshing expired tokens"""

    DELTA = 10  # amount of seconds prior to expiration to refresh the token

    # get_token is simply a function that returns an access token.
    def __init__(self, get_token_func):
        """Constructor for TokenCache"""
        self.get_token_func = get_token_func
        self.token = None
        self.exp = None
        self._lock = Lock()

    def get_token(self):
        """Retrieve an oauth token"""
        if self.should_refresh():
            self.refresh()
        return self.token

    def should_refresh(self):
        """Check to see if oauth token needs refreshing"""
        return self.token is None or self.exp is None or self.exp <= time.time() + self.DELTA

    def refresh(self):
        """Retrieve a new oauth token"""
        with self._lock:
            self.token = self.get_token_func()
            self.exp = jwt.decode(self.token, verify=False)["exp"]
            if self.token is None:
                raise TokenRefreshError


def make_get_token_func(args):
    """Setup authentication context to enable token creation"""
    context = adal.AuthenticationContext(args["authority"])
    resource = args["oauth_resource"]
    client_secret = args["client_secret"]
    client_id = args["client_id"]

    def get_token_func():
        """Acquire token using authentication context"""
        resp = context.acquire_token_with_client_credentials(resource, client_id, client_secret)
        # print(resp)
        return resp["accessToken"]

    return get_token_func

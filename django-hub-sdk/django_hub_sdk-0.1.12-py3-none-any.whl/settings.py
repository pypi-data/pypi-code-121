import os

HUB_APP_SLUG = ""

HUB_BASE_URI = os.environ.get("HUB_BASE_URI", "")
HUB_BASE_PREFIX = os.environ.get("HUB_BASE_PREFIX", "/api")
HUB_BASE_FRONT_URI = os.environ.get(
    "HUB_BASE_FRONT_URI", ""
)

HUB_PROGRAMMATIC_PREFIX = os.environ.get("HUB_PROGRAMMATIC_PREFIX", "/programmatic")
HUB_PROGRAMMATIC_CLIENT = os.environ.get("HUB_PROGRAMMATIC_CLIENT", "")
HUB_PROGRAMMATIC_SECRET = os.environ.get("HUB_PROGRAMMATIC_SECRET", "")

HUB_OAUTH_CLIENT_ID = os.environ.get("HUB_OAUTH_CLIENT_ID", "")
HUB_OAUTH_CLIENT_SECRET = os.environ.get("HUB_OAUTH_CLIENT_SECRET", "")
HUB_OAUTH_REDIRECT = os.environ.get("HUB_OAUTH_REDIRECT", "")
HUB_OAUTH_SCOPES = os.environ.get("HUB_OAUTH_SCOPES", "profile")
HUB_OAUTH_AUTHORIZE_URI = os.environ.get("HUB_OAUTH_AUTHORIZE_URI", "/auth/authorize")
HUB_OAUTH_TOKEN_URI = os.environ.get("HUB_OAUTH_TOKEN_URI", "/oauth/token")
HUB_OAUTH_USERINFO_URI = os.environ.get("HUB_OAUTH_USERINFO_URI", "/users/me")

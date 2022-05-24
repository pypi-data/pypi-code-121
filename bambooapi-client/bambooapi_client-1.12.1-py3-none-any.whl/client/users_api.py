"""Users are those with access to Bamboo API."""

from bambooapi_client.openapi.apis import UsersApi as _UsersApi
from bambooapi_client.openapi.models import User


class UsersApi(object):
    """Implementation for '/v1/users' endpoint."""

    def __init__(self, bambooapi_client):
        """Initialize defaults."""
        self._bambooapi_client = bambooapi_client
        self._api_instance = _UsersApi(bambooapi_client.api_client)

    def me(self, **kwargs) -> User:
        """Return the current authenticated user."""
        return self._api_instance.read_users_me(**kwargs)

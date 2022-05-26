from anyscale.authenticate import get_auth_api_client
from anyscale.client.openapi_client.api.default_api import DefaultApi
from anyscale.sdk.anyscale_client.api.default_api import DefaultApi as AnyscaleApi


class BaseController:
    """
    Base controller which all CLI command controllers should inherit from. Implements
    common functionality of:
        - Authenticating and getting internal and external API clients
    """

    def __init__(self, initialize_auth_api_client: bool = True) -> None:
        self.initialize_auth_api_client = initialize_auth_api_client
        if self.initialize_auth_api_client:
            self.auth_api_client = get_auth_api_client()
            self.api_client = self.auth_api_client.api_client
            self.anyscale_api_client = self.auth_api_client.anyscale_api_client

    @property
    def api_client(self) -> DefaultApi:
        assert self.initialize_auth_api_client, (
            "This command uses `api_client`. Please call the CLI command controller "
            "with initialize_auth_api_client=True to initialize the `api_client`"
        )
        return self._api_client

    @api_client.setter
    def api_client(self, value: DefaultApi) -> None:
        self._api_client = value

    @property
    def anyscale_api_client(self) -> AnyscaleApi:
        assert self.initialize_auth_api_client, (
            "This command uses `anyscale_api_client`. Please call the CLI command controller "
            "with initialize_auth_api_client=True to initialize the `anyscale_api_client`"
        )
        return self._anyscale_api_client

    @anyscale_api_client.setter
    def anyscale_api_client(self, value: AnyscaleApi) -> None:
        self._anyscale_api_client = value

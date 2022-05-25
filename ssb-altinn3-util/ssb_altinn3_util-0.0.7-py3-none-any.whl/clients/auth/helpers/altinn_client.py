import ssb_altinn3_util.clients.auth.helpers.http_helper as http_client
from ssb_altinn3_util.clients.decorators.simple_exception_wrapper import (
    exception_handler,
)


class AltinnClient:
    def __init__(self, altinn_base_url: str):
        self.base_url = altinn_base_url
        self.token_exchange_endpoint = (
            "authentication/api/v1/exchange/maskinporten?test=true"
        )

    @exception_handler("Altinn Client")
    def get_altinn_token(self, access_token: str) -> str:
        url = self.base_url + self.token_exchange_endpoint
        headers = {"Authorization": f"Bearer {access_token}"}

        response = http_client.get(url, headers)

        return response

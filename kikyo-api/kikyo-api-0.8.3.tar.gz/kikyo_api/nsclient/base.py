from requests import Session

from kikyo_api.client import KikyoClient


class NamespacedClient:
    def __init__(self, client: KikyoClient):
        self.client = client

    @property
    def session(self) -> Session:
        self.client.ping()
        return self.client.session

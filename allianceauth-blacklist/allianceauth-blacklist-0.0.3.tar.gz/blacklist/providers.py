from esi.clients import esi_client_factory


class EsiResponseClient:
    def __init__(self, token=None):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = esi_client_factory()  # all groups latest
        return self._client


esi = EsiResponseClient()

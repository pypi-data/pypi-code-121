from .client import ApiClient


class APIBase():

    def __init__(self, client: ApiClient):
        self.client = client

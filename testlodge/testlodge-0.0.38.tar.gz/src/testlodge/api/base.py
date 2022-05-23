from abc import ABC


class BaseAPI(ABC):
    """Abstract Base Class for an API"""

    name: str = 'api'

    def __init__(self, client):

        self.client = client

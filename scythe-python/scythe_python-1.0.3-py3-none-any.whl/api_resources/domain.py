from scythe.api_resources.abstract import AbstractObject, AbstractResource
from typing import Dict, List


class Domain(AbstractResource):
    OBJECT_NAME = "domain"

    def fetch(self, params: Dict, api_key: str = None) -> AbstractObject:
        return super().fetch(params, api_key)

    def list(self, params: Dict = None, api_key: str = None) -> List[AbstractObject]:
        return super().list(params, api_key)

    def create(self, data: Dict, api_key: str = None) -> AbstractObject:
        return super().create(data, api_key)

    def update(self, data: Dict, api_key: str = None) -> AbstractObject:
        return super().update(data, api_key)

    def delete(self, data: Dict, api_key: str = None) -> AbstractObject:
        return super().delete(data, api_key)

from scythe.api_resources.abstract import AbstractObject, AbstractResource, AbstractListObject
from typing import Dict, List


class Subscriber(AbstractResource):
    OBJECT_NAME = "subscriber"
    attrs = ["subscriber_key", "description"]

    def fetch(self, raise_exception: bool = False, **kwargs, ) -> AbstractObject:
        return super().fetch(raise_exception=raise_exception, **kwargs)

    def list(self, raise_exception: bool = False, **kwargs) -> AbstractListObject:
        return super().list(raise_exception=raise_exception, **kwargs)

    def create(self, data: Dict, raise_exception: bool = False) -> AbstractObject:
        return super().create(data=data, raise_exception=raise_exception)

    def update(self, data: Dict, raise_exception: bool = False) -> AbstractObject:
        return super().update(data=data, raise_exception=raise_exception)

    def deactivate(self, data: Dict, raise_exception: bool = False) -> AbstractObject:
        return super().deactivate(data=data, raise_exception=raise_exception)

    def activate(self, data: Dict, raise_exception: bool = False) -> AbstractObject:
        return super().activate(data=data, raise_exception=raise_exception)

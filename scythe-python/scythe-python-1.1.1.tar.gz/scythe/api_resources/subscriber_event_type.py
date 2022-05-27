from scythe.api_resources.abstract import AbstractObject, AbstractResource, AbstractListObject
from typing import Dict, List


class SubscriberEventType(AbstractResource):
    OBJECT_NAME = "subscriber_event_type"
    attrs = ["subscriber_url_id", "event_type_id", "access_key", "description"]

    def fetch(self, raise_exception: bool = False, **kwargs, ) -> AbstractObject:
        return super().fetch(raise_exception=raise_exception, **kwargs)

    def list(self, raise_exception: bool = False, **kwargs) -> AbstractListObject:
        return super().list(raise_exception=raise_exception, **kwargs)

    def create(self, data: Dict, raise_exception: bool = False) -> AbstractObject:
        return super().create(data=data, raise_exception=raise_exception)

    def update(self, data: Dict, raise_exception: bool = False) -> AbstractObject:
        return super().update(data=data, raise_exception=raise_exception)

    def delete(self, data: Dict, raise_exception: bool = False) -> AbstractObject:
        return super().delete(data=data, raise_exception=raise_exception)

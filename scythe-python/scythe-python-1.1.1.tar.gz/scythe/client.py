from .api_resources import *
from .defaults import api_base, api_version
from .request_resource import RequestClient


class ScytheClient(object):
    def __init__(self,
                 api_key: str,
                 api_base: str = api_base,
                 **kwargs):
        self.api_key = api_key
        # Default allowed to update
        self.api_base = api_base
        self.api_version = kwargs.get('api_version', api_version)
        self._build_client()

    def _build_client(self):
        self.client = RequestClient(
            api_key=self.api_key,
            api_base=self.api_base,
            api_version=self.api_version
        )
        self.Domain = Domain(client=self.client)
        self.EventType = EventType(client=self.client)
        self.SubscriberEventType = SubscriberEventType(client=self.client)
        self.SubscriberUrl = SubscriberUrl(client=self.client)
        self.Subscriber = Subscriber(client=self.client)

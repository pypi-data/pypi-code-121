import requests
from urllib.parse import urlencode
from typing import Optional 

from django.conf import settings

from dnoticias_services.subscriptions.base import BaseSubscriptionRequest
from dnoticias_services.utils.request import get_headers


class GetSubscriptions(BaseSubscriptionRequest):
    def __call__(self, api_key: Optional[str] = None, **kwargs):
        _api_key = api_key or self.api_key
        params = urlencode(kwargs)

        response = requests.get(
            settings.GET_SUBSCRIPTIONS_API_URL + f'?{params}',
            headers=get_headers(_api_key),
        )

        response.raise_for_status()

        return response


get_subscriptions = GetSubscriptions()

__all__ = ("get_subscriptions", )

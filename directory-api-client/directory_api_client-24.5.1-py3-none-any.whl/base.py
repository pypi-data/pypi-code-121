import directory_client_core.base
import pkg_resources
from directory_client_core.helpers import fallback
from django.core.cache import caches


class AbstractAPIClient(directory_client_core.base.AbstractAPIClient):

    version = pkg_resources.get_distribution(__package__).version

    @fallback(cache=caches['api_fallback'])
    def fallback_cache_get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def get(self, *args, use_fallback_cache=False, **kwargs):
        if use_fallback_cache:
            return self.fallback_cache_get(*args, **kwargs)
        return super().get(*args, **kwargs)

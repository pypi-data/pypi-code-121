from .constants import *
from .logger import Logger



class RemoteConfigService():

    def list(self, filter=None, uninherited=False):
        from .providers import Providers
        provider = Providers.RemoteConfigProvider()
        response = provider.list(filter=filter, uninherited=uninherited)
        return response


    def add(self, key, value):
        # self.validate_key(key)
        from .providers import Providers
        provider = Providers.RemoteConfigProvider()
        return provider.add(key=key, value=value)


    def get(self, key, revision=None, uninherited=False, rendered=True):
        from .providers import Providers
        provider = Providers.RemoteConfigProvider()
        return provider.get(key=key, revision=revision, uninherited=uninherited, rendered=rendered)


    def history(self, key):
        from .providers import Providers
        provider = Providers.RemoteConfigProvider()
        return provider.history(key)


    def delete(self, key):
        from .providers import Providers
        provider = Providers.RemoteConfigProvider()
        return provider.delete(key=key)


RemoteConfig = RemoteConfigService()

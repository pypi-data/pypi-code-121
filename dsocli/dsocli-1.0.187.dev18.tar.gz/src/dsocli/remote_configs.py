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


    # def history(self, key):
    #   from .configs import Config
    #     self.config = config
    #     from .providers import Providers
    # provider = Providers.RemoteConfigProvider()
    #     Logger.debug(f"Fetching history of configuration '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
    #     return provider.history(service key)


    def delete(self, key):
        from .providers import Providers
        provider = Providers.RemoteConfigProvider()
        return provider.delete(key=key)


RemoteConfig = RemoteConfigService()

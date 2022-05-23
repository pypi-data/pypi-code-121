from .constants import *
from .providers import KeyValueStoreProvider, Providers
from .logger import Logger
from .contexts import ContextMode




class ConfigProvider(KeyValueStoreProvider):
    def list(self, service, uninherited, filter):
        raise NotImplementedError()
    def add(self, key, value, service):
        raise NotImplementedError()
    def get(self, key, revision, service):
        raise NotImplementedError()
    def history(self, key, service):
        raise NotImplementedError()
    def delete(self, key, service):
        raise NotImplementedError()


class ConfigService():

    def list(self, filter=None, uninherited=False):
        from .appconfigs import AppConfigs
        provider = Providers.ConfigProvider()
        Logger.debug(f"Listing configuration settings: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        response = provider.list(filter=filter, uninherited=uninherited)
        return response


    def add(self, key, value):
        from .appconfigs import AppConfigs
        # self.validate_key(key)
        provider = Providers.ConfigProvider()
        Logger.debug(f"Adding configuration setting '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        return provider.set(key=key, value=value)


    def get(self, key, revision=None, uninherited=False, rendered=True):
        from .appconfigs import AppConfigs
        provider = Providers.ConfigProvider()
        Logger.debug(f"Getting configuration setting '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        return provider.get(key=key, revision=revision, uninherited=uninherited, rendered=rendered)


    # def history(self, key):
    #   from .appconfigs import AppConfigs
    #     self.config = config
    #     provider = Providers.ConfigProvider()
    #     Logger.debug(f"Fetching history of configuration '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
    #     return provider.history(service=service, key)


    def delete(self, key):
        from .appconfigs import AppConfigs
        provider = Providers.ConfigProvider()
        Logger.debug(f"Deleting configuration setting '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        return provider.unset(key=key)


Configs = ConfigService()

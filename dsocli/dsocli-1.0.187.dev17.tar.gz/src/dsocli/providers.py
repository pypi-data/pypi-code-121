import os
import imp
from .configs import Config
from .constants import *
from .logger import Logger
from .exceptions import DSOException

class ProviderBase():
    def __init__(self, id):
        self.__id = id
    @property
    def id(self):
        return self.__id

class KeyValueStoreProvider(ProviderBase):

    # def validate_key(self, key):
    #     Logger.debug(f"Validating: key={key}")
    #     pattern = self.get_key_validator()
    #     if not re.match(pattern, key):
    #         raise DSOException(MESSAGES['InvalidKeyPattern'].format(key, pattern))

    # def get_key_validator(self, key):
    #     raise NotImplementedError()

    def list(self):
        raise NotImplementedError()
    def add(self):
        raise NotImplementedError()
    def delete(self):
        raise NotImplementedError()
    def get(self):
        raise NotImplementedError()
    def history(self):
        raise NotImplementedError()


class ArtifactoryProvider(ProviderBase):
    def list(self):
        raise NotImplementedError()
    def upload(self):
        raise NotImplementedError()
    def download(self):
        raise NotImplementedError()
    def history(self):
        raise NotImplementedError()
    def delete(self):
        raise NotImplementedError()


class RemoteConfigProvider(KeyValueStoreProvider):
    def list(self, filter=None, uninherited=False):
        raise NotImplementedError()
    def add(self, key, value):
        raise NotImplementedError()
    def get(self, key, revision=None, uninherited=False, rendered=True):
        raise NotImplementedError()
    def history(self, key):
        raise NotImplementedError()
    def delete(self, key):
        raise NotImplementedError()


class ProviderService():
    __providers = {}

    # def load_all_providers(self):
    #     __import__(AppConfigsroot_path + 'lib/dso/provider')
    #     # importdir.do(os.path.dirname(__file__)+'/secret_providers', globals())
    #     # importdir.do(os.path.dirname(__file__)+'/template_providers', globals())

    def load_provider(self, provider_slug):
        Logger.debug(f"Loading provider '{provider_slug}'...")
        providerPackagePath = os.path.join(Config.install_path, 'provider', provider_slug)
        if not os.path.exists(providerPackagePath):
            raise DSOException(f"Provider '{provider_slug}' not found.")
        imp.load_package(provider_slug, providerPackagePath).register()

    def register(self, provider: ProviderBase):
        if not provider.id in self.__providers:
            self.__providers[provider.id] = provider
            Logger.debug(f"Provider registered: id={provider.id}")

    def get_provider(self, provider_slug):
        if not provider_slug in self.__providers:
            self.load_provider(provider_slug)

        ### make sure provider has registered, and return it
        if provider_slug in self.__providers:
            return self.__providers[provider_slug] 
        else:
            raise DSOException(f"No provider has registered for '{provider_slug}'.")

    def RemoteConfigProvider(self):
        if not Config.config_provider:
            raise DSOException(MESSAGES['ProviderNotSet'].format('Config'))
        return self.get_provider('config/' + Config.config_provider)

    def ParameterProvider(self):
        if not Config.parameter_provider:
            raise DSOException(MESSAGES['ProviderNotSet'].format('Parameter'))
        return self.get_provider('parameter/' + Config.parameter_provider)

    def SecretProvider(self):
        if not Config.secret_provider:
            raise DSOException(MESSAGES['ProviderNotSet'].format('Secret'))
        return self.get_provider('secret/' + Config.secret_provider)

    def TemplateProvider(self):
        if not Config.template_provider:
            raise DSOException(MESSAGES['ProviderNotSet'].format('Template'))
        return self.get_provider('template/' + Config.template_provider)

    def ArtifactoryProvider(self):
        if not Config.artifactory_provider:
            raise DSOException(MESSAGES['ProviderNotSet'].format('Artifactory'))
        return self.get_provider('artifactory/' + Config.artifactory_provider)

    def PackageProvider(self):
        if not Config.package_provider:
            raise DSOException(MESSAGES['ProviderNotSet'].format('Package'))
        return self.get_provider('package/' + Config.package_provider)

    def ReleaseProvider(self):
        if not Config.release_provider:
            raise DSOException(MESSAGES['ProviderNotSet'].format('Release'))
        return self.get_provider('release/' + Config.release_provider)

Providers = ProviderService()

import os
import imp
from .appconfigs import AppConfigs
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


class ProviderService():
    __providers = {}

    # def load_all_providers(self):
    #     __import__(AppConfigsroot_path + 'lib/dso/provider')
    #     # importdir.do(os.path.dirname(__file__)+'/secret_providers', globals())
    #     # importdir.do(os.path.dirname(__file__)+'/template_providers', globals())

    def load_provider(self, provider_slug):
        Logger.debug(f"Loading provider '{provider_slug}'...")
        providerPackagePath = os.path.join(AppConfigs.install_path, 'provider', provider_slug)
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

    def ConfigProvider(self):
        if not AppConfigs.config_provider:
            raise DSOException(MESSAGES['ProviderNotSet'].format('Config'))
        return self.get_provider('config/' + AppConfigs.config_provider)

    def ParameterProvider(self):
        if not AppConfigs.parameter_provider:
            raise DSOException(MESSAGES['ProviderNotSet'].format('Parameter'))
        return self.get_provider('parameter/' + AppConfigs.parameter_provider)

    def SecretProvider(self):
        if not AppConfigs.secret_provider:
            raise DSOException(MESSAGES['ProviderNotSet'].format('Secret'))
        return self.get_provider('secret/' + AppConfigs.secret_provider)

    def TemplateProvider(self):
        if not AppConfigs.template_provider:
            raise DSOException(MESSAGES['ProviderNotSet'].format('Template'))
        return self.get_provider('template/' + AppConfigs.template_provider)

    def ArtifactoryProvider(self):
        if not AppConfigs.artifactory_provider:
            raise DSOException(MESSAGES['ProviderNotSet'].format('Artifactory'))
        return self.get_provider('artifactory/' + AppConfigs.artifactory_provider)

    def PackageProvider(self):
        if not AppConfigs.package_provider:
            raise DSOException(MESSAGES['ProviderNotSet'].format('Package'))
        return self.get_provider('package/' + AppConfigs.package_provider)

    def ReleaseProvider(self):
        if not AppConfigs.release_provider:
            raise DSOException(MESSAGES['ProviderNotSet'].format('Release'))
        return self.get_provider('release/' + AppConfigs.release_provider)

Providers = ProviderService()

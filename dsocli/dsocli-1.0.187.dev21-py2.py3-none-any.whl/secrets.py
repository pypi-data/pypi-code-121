import re
from .logger import Logger
from .providers import KeyValueStoreProvider, Providers
from .stages import Stages
from .constants import *
from .exceptions import *
from .configs import Config, ContextMode



key_regex_pattern = r"^[a-zA-Z]([.a-zA-Z0-9_-]*[a-zA-ZA-Z0-9])?$"

class SecretProvider(KeyValueStoreProvider):
    def list(self, uninherited=False, decrypt=False, filter=None):
        raise NotImplementedError()
    def add(self, key, value):
        raise NotImplementedError()
    def get(self, key, decrypt=False, revision=None):
        raise NotImplementedError()
    def history(self, key, decrypt=False):
        raise NotImplementedError()
    def delete(self, key):
        raise NotImplementedError()


class SecretService():

    def validate_key(self, key):
        Logger.info(f"Validating secret key '{key}'...")
        if not key:
            raise DSOException(MESSAGES['KeyNull'])
        if key == 'dso' or key.startswith('dso.'):
            raise DSOException(MESSAGES['DSOReserverdKey'].format(key))
        if not re.match(key_regex_pattern, key):
            raise DSOException(MESSAGES['InvalidKeyPattern'].format(key, key_regex_pattern))
        if '..' in key:
            raise DSOException(MESSAGES['InvalidKeyStr'].format(key, '..'))

    def list(self, uninherited=False, decrypt=False, filter=None):
        provider = Providers.SecretProvider()
        Logger.info(f"Listing secrets: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        from operator import itemgetter
        return {'Secrets': sorted(provider.list(uninherited, decrypt, filter), key=itemgetter('Key'))}        

    def add(self, key, value):
        self.validate_key(key)
        provider = Providers.SecretProvider()
        Logger.info(f"Adding secret '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        return provider.add(key, value)

    def get(self, key, revision=None, uninherited=False, decrypt=False):
        # self.validate_key(key)
        provider = Providers.SecretProvider()
        Logger.info(f"Getting secret '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        return provider.get(key, revision, uninherited, decrypt)

    def history(self, key, decrypt=False):
        # self.validate_key(key)
        provider = Providers.SecretProvider()
        Logger.info(f"Fetching history of secret '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        return provider.history(key, decrypt)

    def delete(self, key):
        # self.validate_key(key)
        provider = Providers.SecretProvider()
        Logger.info(f"Deleting secret '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        return provider.delete(key)

Secrets = SecretService()

import os
from dsocli.logger import Logger
from dsocli.appconfigs import AppConfigs, ContextMode
from dsocli.providers import Providers
from dsocli.secrets import SecretProvider
from dsocli.constants import *
from dsocli.exceptions import DSOException
from dsocli.local_utils import *
from dsocli.settings import *


__default_spec = {
    'path': os.path.join(AppConfigs.config_dir, 'secret/'),
    'store': 'local.json',
}


def get_default_spec():
    return __default_spec.copy()



class LocalSecretProvider(SecretProvider):

    def __init__(self):
        super().__init__('secret/local/v1')

    @property
    def root_path(self):
        return AppConfigs.secret_spec('path')


    def get_path_prefix(self):
        # return self.root_path + os.sep
        return self.root_path


    @property
    def namespace(self):
        return AppConfigs.secret_spec('namespace')


    @property
    def store_name(self):
        return AppConfigs.secret_spec('store')


    def add(self, key, value):
        Logger.warn("Secret provider 'loval/v1' does not support encryption.")
        Logger.debug(f"Adding local secret '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        response = add_local_parameter(key=key, value=value, store_name=self.store_name, path_prefix=self.get_path_prefix())
        return response


    def list(self, uninherited=False, decrypt=False, filter=None):
        Logger.debug(f"Listing local secrets: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        secrets = load_context_local_parameters(store_name=self.store_name, path_prefix=self.get_path_prefix(), uninherited=uninherited, filter=filter)
        result = []
        for key, details in secrets.items():
            item = {
                'Key': key,
            }
            item.update(details)
            result.append(item)

        return result


    def get(self, key, revision=None, uninherited=False, decrypt=False):
        if revision:
            Logger.warn(f"Secret provider 'local/v1' does not support versioning. Revision request ignored.")
        Logger.debug(f"Getting local secret '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        found = locate_parameter_in_context_hierachy(key=key, store_name=self.store_name, path_prefix=self.get_path_prefix(), uninherited=uninherited)
        if not found:
            raise DSOException(f"Secret '{key}' not found in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        result = {
                'Key': key, 
            }
        result.update(found[key])
        return result


    def history(self, key, decrypt=False):
        Logger.warn(f"Secret provider 'local/v1' does not support versioning.")

        Logger.debug(f"Getting local secret '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        found = locate_parameter_in_context_hierachy(key=key, store_name=self.store_name, path_prefix=self.get_path_prefix(), uninherited=False)
        if not found:
            raise DSOException(f"Secret '{key}' not found in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        result = { "Revisions":
            [{
                'RevisionId': '0',
                'Date': get_file_modified_date(found[key]['Path']),
            }]
        }
        result['Revisions'][0].update(found[key])
        return result


    def delete(self, key):
        Logger.debug(f"Locating secret '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        ### only secrets owned by the config can be deleted, hence uninherited=True
        found = locate_parameter_in_context_hierachy(key=key, store_name=self.store_name, path_prefix=self.get_path_prefix(), uninherited=True)
        if not found:
            raise DSOException(f"Secret '{key}' not found in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        Logger.info(f"Deleting secret: path={found[key]['Path']}")
        delete_local_parameter(found[key]['Path'], key=key)
        result = {
                'Key': key,
                'Stage': AppConfigs.short_stage,
                'Scope': found[key]['Scope'], 
                'Origin': found[key]['Origin'], 
                'Path': found[key]['Path'],
            }
        return result


def register():
    Providers.register(LocalSecretProvider())

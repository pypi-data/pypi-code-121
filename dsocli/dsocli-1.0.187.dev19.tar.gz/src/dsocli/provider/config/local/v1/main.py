import os
from dsocli.logger import Logger
from dsocli.configs import Config, ContextMode
from dsocli.providers import Providers, RemoteConfigProvider
from dsocli.stages import Stages
from dsocli.constants import *
from dsocli.exceptions import DSOException
from dsocli.local_utils import *
from dsocli.settings import *


__default_spec = {
    'path': os.path.join(Config.config_dir, 'config/'),
    'store': 'local.json',
}


def get_default_spec():
    return __default_spec.copy()



class LocalConfigProvider(RemoteConfigProvider):

    def __init__(self):
        super().__init__('config/local/v1')

    @property
    def root_path(self):
        return Config.config_spec('path')


    def get_path_prefix(self):
        return self.root_path



    @property
    def store_name(self):
        return Config.config_spec('store')



    def add(self, key, value):
        Logger.debug(f"Adding local configuration setting '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        response = add_local_parameter(key=key, value=value, store_name=self.store_name, path_prefix=self.get_path_prefix())
        return response



    def list(self, uninherited=False, filter=None):
        Logger.debug(f"Listing local configuration settings: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        settings = load_context_local_parameters(store_name=self.store_name, path_prefix=self.get_path_prefix(), uninherited=uninherited, filter=filter)
        result = []
        for key, details in settings.items():
            item = {
                'Key': key,
            }
            item.update(details)
            result.append(item)

        return result



    def get(self, key, revision=None, uninherited=False, rendered=True):
        if revision:
            Logger.warn(f"Config provider 'local/v1' does not support versioning. Revision request ignored.")
        Logger.debug(f"Getting configuration setting '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        found = locate_parameter_in_context_hierachy(key=key, store_name=self.store_name, path_prefix=self.get_path_prefix(), uninherited=uninherited)
        if not found:
            raise DSOException(f"Configuration setting '{key}' not found in the given context: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        # if len(found) > 1:
        #     raise DSOException(f"Mutiple settings found with the same key '{key}' in the given context.")
        result = {
                'Key': key, 
            }
        result.update(found[key])
        return result



    def history(self, key):
        Logger.warn(f"Config provider 'local/v1' does not support history.")

        Logger.debug(f"Getting local configuration setting '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        found = locate_parameter_in_context_hierachy(key=key, store_name=self.store_name, path_prefix=self.get_path_prefix(), uninherited=False)
        if not found:
            raise DSOException(f"Configuration setting '{key}' not found in the given context: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        result = { "Revisions":
            [{
                'RevisionId': '0',
                'Date': get_file_modified_date(found[key]['Path']),
            }]
        }
        result['Revisions'][0].update(found[key])
        return result


    def delete(self, key):
        Logger.debug(f"Locating config setting '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        ### only configs owned by the config can be deleted, hence uninherited=True
        found = locate_parameter_in_context_hierachy(key=key, store_name=self.store_name, path_prefix=self.get_path_prefix(), uninherited=True)
        if not found:
            raise DSOException(f"Configuration setting '{key}' not found in the given context: namesape={Config.namespace}, application={Config.application}, stage={Config.short_stage}")
        Logger.info(f"Deleting configuration setting '{key}': path={found[key]['Path']}")
        delete_local_parameter(found[key]['Path'], key=key)
        result = {
                'Key': key,
                'Stage': Config.short_stage,
                'Scope': found[key]['Scope'], 
                'Context': found[key]['Context'], 
                'Path': found[key]['Path'],
            }
        return result



def register():
    Providers.register(LocalConfigProvider())

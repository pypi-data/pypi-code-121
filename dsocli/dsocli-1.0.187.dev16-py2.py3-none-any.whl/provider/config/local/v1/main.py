import os
from dsocli.logger import Logger
from dsocli.appconfigs import AppConfigs, ContextMode
from dsocli.providers import Providers
from dsocli.configs import ConfigProvider
from dsocli.stages import Stages
from dsocli.constants import *
from dsocli.exceptions import DSOException
from dsocli.local_utils import *
from dsocli.settings import *


__default_spec = {
    'path': os.path.join(AppConfigs.config_dir, 'config/'),
    # 'namespace': 'default',
    'store': 'local.json',
}


def get_default_spec():
    return __default_spec.copy()



class LocalConfigProvider(ConfigProvider):

    def __init__(self):
        super().__init__('config/local/v1')

    @property
    def root_path(self):
        return AppConfigs.config_spec('path')


    def get_path_prefix(self, service):
        # return self.root_path + os.sep
        return os.path.join(self.root_path, service)

    @property
    def namespace(self):
        return AppConfigs.parameter_spec('namespace')


    @property
    def store_name(self):
        return AppConfigs.parameter_spec('store')



    def set(self, key, value):
        Logger.debug(f"Adding local configuration setting '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        response = add_local_parameter(key=key, value=value, store_name=self.store_name, path_prefix=self.get_path_prefix(service))
        return response



    def list(self, uninherited=False, filter=None):
        self.service = service
        Logger.debug(f"Listing local configuration settings: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        settings = load_context_local_parameters(store_name=self.store_name, path_prefix=self.get_path_prefix(service), uninherited=uninherited, filter=filter)
        result = []
        for key, details in settings.items():
            item = {
                'Key': key,
            }
            item.update(details)
            result.append(item)

        return result



    def get(self, service, key, revision=None, uninherited=False, editable=False):
        self.service = service
        if revision:
            Logger.warn(f"Config provider 'local/v1' does not support versioning. Revision request ignored.")
        Logger.debug(f"Getting configuration setting '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        found = locate_parameter_in_context_hierachy(key=key, store_name=self.store_name, path_prefix=self.get_path_prefix(service), uninherited=uninherited)
        if not found:
            if uninherited:
                raise DSOException(f"Setting '{key}' not found in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
            else:
                raise DSOException(f"Setting '{key}' not found nor inherited in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        # if len(found) > 1:
        #     raise DSOException(f"Mutiple settings found with the same key '{key}' in the given context.")
        result = {
                'Key': key, 
            }
        result.update(found[key])
        return result



    def history(self, service, key):
        self.service = service
        Logger.warn(f"Config provider 'local/v1' does not support versioning.")

        Logger.debug(f"Getting local config setting '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        found = locate_parameter_in_context_hierachy(key=key, store_name=self.store_name, path_prefix=self.get_path_prefix(service), uninherited=False)
        if not found:
            raise DSOException(f"Setting '{key}' not found nor inherited in the given context: stage={Stages.shorten(AppConfigs.short_stage)}")
        result = { "Revisions":
            [{
                'RevisionId': '0',
                'Date': get_file_modified_date(found[key]['Path']),
            }]
        }
        result['Revisions'][0].update(found[key])
        return result


    def unset(self, service, key):
        self.service = service
        Logger.debug(f"Locating config setting '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        ### only configs owned by the config can be deleted, hence uninherited=True
        found = locate_parameter_in_context_hierachy(key=key, store_name=self.store_name, path_prefix=self.get_path_prefix(service), uninherited=True)
        if not found:
            raise DSOException(f"Config setting '{key}' not found in the given context: namesape={AppConfigs.namespace}, application={AppConfigs.application}, stage={AppConfigs.short_stage}")
        Logger.info(f"Deleting config setting '{key}': path={found[key]['Path']}")
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
    Providers.register(LocalConfigProvider())

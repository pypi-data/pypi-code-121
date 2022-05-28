import os
from dsocli.logger import Logger
from dsocli.configs import Config, ContextMode
from dsocli.providers import Providers
from dsocli.parameters import ParameterProvider
from dsocli.constants import *
from dsocli.exceptions import DSOException
from dsocli.shell_utils import *
from dsocli.settings import *


__default_spec = {
    'path': os.path.join(Config.config_dir, 'parameter'),
    'store': 'shell.json',
}


def get_default_spec():
    return __default_spec.copy()



class ShellParameterProvider(ParameterProvider):

    def __init__(self):
        super().__init__('parameter/shell/v1')

    @property
    def root_path(self):
        return Config.parameter_spec('path')


    def get_path_prefix(self):
        return self.root_path

    @property
    def namespace(self):
        return Config.parameter_spec('namespace')


    @property
    def store_name(self):
        return Config.parameter_spec('store')


    def add(self, key, value):
        Logger.debug(f"Adding shell parameter '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        response = add_shell_parameter(key=key, value=value, store_name=self.store_name, path_prefix=self.get_path_prefix())
        return response


    def list(self, uninherited=False, filter=None):
        Logger.debug(f"Listing shell parameters: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        parameters = load_context_shell_parameters(store_name=self.store_name, path_prefix=self.get_path_prefix(), uninherited=uninherited, filter=filter)
        result = []
        for key, details in parameters.items():
            item = {
                'Key': key,
            }
            item.update(details)
            result.append(item)

        return result


    def get(self, key, revision=None, uninherited=False, rendered=True):
        if revision:
            Logger.warn(f"Parameter provider 'shell/v1' does not support versioning. Revision request ignored.")
        Logger.debug(f"Getting shell parameter '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        found = locate_shell_parameter_in_context_hierachy(key=key, store_name=self.store_name, path_prefix=self.get_path_prefix(), uninherited=uninherited, rendered=rendered)
        if not found:
            raise DSOException(f"Parameter '{key}' not found in the given context: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        # if len(found) > 1:
        #     raise DSOException(f"Mutiple parameters found with the same key '{key}' in the given context.")
        result = {
                'Key': key, 
            }
        result.update(found[key])
        return result


    def history(self, key):
        Logger.warn(f"Parameter provider 'shell/v1' does not support history.")

        Logger.debug(f"Getting shell parameter '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        found = locate_shell_parameter_in_context_hierachy(key=key, store_name=self.store_name, path_prefix=self.get_path_prefix(), uninherited=True)
        if not found:
            raise DSOException(f"Parameter '{key}' not found in the given context: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        result = { "Revisions":
            [{
                'RevisionId': '0',
                'Date': get_file_modified_date(found[key]['Path']),
            }]
        }
        result['Revisions'][0].update(found[key])
        return result



    def delete(self, key):
        Logger.debug(f"Locating parameter '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        ### only parameters owned by the config can be deleted, hence uninherited=True
        found = locate_shell_parameter_in_context_hierachy(key=key, store_name=self.store_name, path_prefix=self.get_path_prefix(), uninherited=True)
        if not found:
            raise DSOException(f"Parameter '{key}' not found in the given context: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        Logger.info(f"Deleting parameter: path={found[key]['Path']}")
        delete_shell_parameter(found[key]['Path'], key=key)
        result = {
                'Key': key,
                'Stage': Config.short_stage,
                'Scope': found[key]['Scope'], 
                'Context': found[key]['Context'], 
                'Path': found[key]['Path'],
            }
        return result



def register():
    Providers.register(ShellParameterProvider())

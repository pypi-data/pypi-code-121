import os
from dsocli.logger import Logger
from dsocli.configs import Config
from dsocli.providers import Providers
from dsocli.templates import TemplateProvider
from dsocli.stages import Stages
from dsocli.constants import *
from dsocli.exceptions import DSOException
from dsocli.local_utils import *
from dsocli.settings import *


__default_spec = {
    'path': os.path.join(Config.config_dir, 'templates'),
}


def get_default_spec():
    return __default_spec.copy()


class LocalTemplateProvider(TemplateProvider):


    def __init__(self):
        super().__init__('template/local/v1')


    @property
    def root_dir(self):
        return self.config.template_spec('path')


    def get_path_prefix(self):
        # return self.root_dir + os.sep
        return self.root_dir


    def list(self, config, uninherited=False, include_contents=False, filter=None):
        self.config = config
        Logger.debug(f"Listing local parameters: namespace={config.namespace}, application={config.application}, stage={config.stage}")
        templates = load_context_templates(config=config, path_prefix=self.get_path_prefix(), uninherited=uninherited, include_contents=include_contents, filter=filter)
        result = {'Templates': []}
        for key, details in templates.items():
            item = {'Key': key}
            item.update(details)
            result['Templates'].append(item)
        return result


    def add(self, config, key, contents, render_path=None):
        self.config = config
        # if not Stages.is_default(config.stage) and not ALLOW_STAGE_TEMPLATES:
        #     raise DSOException(f"Templates may not be added to stage scopes, as the feature is currently disabled. It may be enabled by adding 'ALLOW_STAGE_TEMPLATES=yes' to the DSO global settings, or adding environment variable 'DSO_ALLOW_STAGE_TEMPLATES=yes'.")
        Logger.debug(f"Adding local template '{key}': namespace={config.namespace}, application={config.application}, stage={config.stage}")
        response = add_local_template(config=config, key=key, path_prefix=self.get_path_prefix(), contents=contents)
        result = {
                'Key': key,
                'Stage': Stages.shorten(config.stage),
                'Context': response['Context'], 
                'Path': response['Path'],
            }
        return result


    def get(self, config, key, revision=None):
        self.config = config
        if revision:
            Logger.warn(f"Template provider 'local/v1' does not support versioning. Revision request ignored.")
        Logger.debug(f"Getting template '{key}': namespace={config.namespace}, application={config.application}, stage={config.stage}")
        found = locate_template_in_context_hierachy(config=config, key=key, path_prefix=self.get_path_prefix(), include_contents=True)
        if not found:
            raise DSOException(f"Template '{key}' not found nor inherited in the given context: stage={config.short_stage}")
        result = {
                'Key': key, 
            }
        result.update(found[key])
        return result


    def history(self, config, key, include_contents=False):
        self.config = config
        Logger.warn(f"Template provider 'local/v1' does not support versioning.")
        Logger.debug(f"Getting template '{key}': namesape={config.namespace}, application={config.application}, stage={config.stage}")
        found = locate_template_in_context_hierachy(config=config, key=key, path_prefix=self.get_path_prefix(), include_contents=True)
        if not found:
            raise DSOException(f"Template '{key}' not found nor inherited in the given context: stage={config.short_stage}")

        result = { "Revisions":
            [{
                'RevisionId': '0',
            }]
        }
        result['Revisions'][0].update(found[key])
        return result


    def delete(self, config, key):
        self.config = config
        Logger.debug(f"Locating template: namespace={config.namespace}, application={config.application}, stage={config.stage}")
        ### only parameters owned by the context can be deleted, hence uninherited=True
        found = locate_template_in_context_hierachy(config=config, key=key, path_prefix=self.get_path_prefix(), uninherited=True)
        if not found:
            raise DSOException(f"Template '{key}' not found in the given context: stage={Stages.shorten(stage)}")
        Logger.info(f"Deleting template: path={found[key]['Path']}")
        delete_local_template(path=found[key]['Path'])
        result = {
                'Key': key,
                'Stage': config.short_stage,
                'Scope': found[key]['Scope'], 
                'Context': found[key]['Context'], 
                'Path': found[key]['Path'],
            }
        return result



def register():
    Providers.register(LocalTemplateProvider())

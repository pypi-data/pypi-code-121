from dsocli.exceptions import DSOException
from dsocli.logger import Logger
from dsocli.providers import Providers
from dsocli.templates import TemplateProvider
from dsocli.stages import Stages
from dsocli.constants import *
from dsocli.aws_ssm_utils import *
from dsocli.settings import *
from dsocli.configs import Config, ContextMode


__default_spec = {
    'pathPrefix': '/dso/template/',
}

def get_default_spec():
    return __default_spec.copy()


class AwsSsmTemplateProvider(TemplateProvider):


    def __init__(self):
        super().__init__('template/aws/ssm/v1')


    def get_path_prefix(self):
        return Config.template_spec('pathPrefix')


    def list(self, uninherited=False, include_contents=False, filter=None):
        Logger.debug(f"Listing SSM templates: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        templates = load_context_ssm_parameters(parameter_type='StringList', path_prefix=self.get_path_prefix(), uninherited=uninherited, filter=filter)
        result = []
        for key, details in templates.items():
            item = {
                'Key': key,
                'RevisionId': str(details['Version']),
            }
            item.update(details)
            if include_contents: item['Contents'] = item['Value']
            item.pop('Value')
            result.append(item)
        return result


    def add(self, key, contents, render_path=None):
        if len(contents) > 4096:
            raise DSOException(f"This template provider does not support templates larger than 4KB.")
        # if not Stages.is_default(Config.stage) and not ALLOW_STAGE_TEMPLATES:
        #     raise DSOException(f"Templates may not be added to stage scopes, as the feature is currently disabled. It may be enabled by adding 'ALLOW_STAGE_TEMPLATES=yes' to the DSO global settings, or adding environment variable 'DSO_ALLOW_STAGE_TEMPLATES=yes'.")
        Logger.debug(f"Checking SSM template '{key}' overwrites: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        assert_ssm_parameter_no_namespace_overwrites(key=key, path_prefix=self.get_path_prefix())
        Logger.debug(f"Locating SSM template '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        found = locate_ssm_parameter_in_context_hierachy(key=key, path_prefix=self.get_path_prefix(), uninherited=True)
        if found and not found['Type'] == 'StringList':
            raise DSOException(f"Failed to add template '{key}' becasue the key is not available in the given context: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        path = get_ssm_path(context=Config.context, key=key, path_prefix=self.get_path_prefix())
        Logger.debug(f"Adding SSM template: path={path}")
        response = add_ssm_template(path, contents)
        result = {
                'RevisionId': str(response['Version']),
                'Key': key,
                'Stage': Config.short_stage,
                'Scope': Config.context.scope_translation,
                'Context': {
                    'Namespace': Config.namespace,
                    'Application': Config.application,
                    'Stage': Config.stage,
                },
                'Path': path,
            }
        result.update(response)
        return result


    def get(self, key, revision=None):
        Logger.debug(f"Locating SSM template '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        found = locate_ssm_parameter_in_context_hierachy(key=key, path_prefix=self.get_path_prefix(), uninherited=False)
        if not found:
            raise DSOException(f"Template '{key}' not found in the given context: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        else:
            if not found['Type'] == 'StringList':
                raise DSOException(f"Template '{key}' not found in the given context: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        Logger.debug(f"Getting SSM template: path={found['Name']}")
        response = get_ssm_template_history(found['Name'])
        templates = sorted(response['Parameters'], key=lambda x: int(x['Version']), reverse=True)
        if revision is None:
            ### get the latest revision
            result = {
                    'RevisionId': str(templates[0]['Version']),
                    'Date': templates[0]['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key, 
                    'Scope': found['Scope'],
                    'Context': found['Context'],
                    'User': templates[0]['LastModifiedUser'],
                    'Path': found['Name'],
                    'Contents': templates[0]['Value'],
                    }
        else:
            ### get specific revision
            templates = [x for x in templates if str(x['Version']) == revision]
            if not templates:
                raise DSOException(f"Revision '{revision}' not found for template '{key}' in the given context: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
            result = {
                    'RevisionId': str(templates[0]['Version']),
                    'Date': templates[0]['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key, 
                    'Scope': found['Scope'],
                    'Context': found['Context'],
                    'Path': found['Name'],
                    'User': templates[0]['LastModifiedUser'],
                    'Contents': templates[0]['Value'],
                    }

        return result



    def history(self, key, include_contents=False):
        Logger.debug(f"Locating SSM template '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        found = locate_ssm_parameter_in_context_hierachy(key=key, path_prefix=self.get_path_prefix(), uninherited=True)
        if not found:
            raise DSOException(f"Template '{key}' not found in the given context: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        else:
            if not found['Type'] == 'StringList':
                raise DSOException(f"Template '{key}' not found in the given context: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        Logger.debug(f"Getting SSM template: path={found['Name']}")
        response = get_ssm_parameter_history(found['Name'])
        templates = sorted(response['Parameters'], key=lambda x: int(x['Version']), reverse=True)
        if include_contents:
            result = { "Revisions":
                [{
                    'RevisionId': str(template['Version']),
                    'Date': template['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key,
                    # 'Scope': found['Scope'],
                    # 'Context': found['Context'],
                    'User': template['LastModifiedUser'],
                    # 'Path': found['Name'],
                    'Contents': templates[0]['Value'],

                } for template in templates]
            }
        else:
            result = { "Revisions":
                [{
                    'RevisionId': str(template['Version']),
                    'Date': template['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key,
                    # 'Scope': found['Scope'],
                    # 'Context': found['Context'],
                    'User': template['LastModifiedUser'],
                    # 'Path': found['Name'],
                } for template in templates]
            }

        return result



    def delete(self, key):
        Logger.debug(f"Locating SSM template '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        ### only parameters owned by the context can be deleted, hence uninherited=True
        found = locate_ssm_parameter_in_context_hierachy(key=key, path_prefix=self.get_path_prefix(), uninherited=True)
        if not found:
            raise DSOException(f"Template '{key}' not found in the given context: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        else:
            # if len(found) > 1:
            #     Logger.warn(f"More than one template found at '{found['Name']}'. The first one taken, and the rest were discarded.")
            if not found['Type'] == 'StringList':
                raise DSOException(f"Template '{key}' not found in the given context: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        Logger.debug(f"Deleting SSM template: path={found['Name']}")
        delete_ssm_parameter(found['Name'])
        return {
                'Key': key, 
                'Stage': found['Stage'],
                'Scope': found['Scope'],
                'Context': found['Context'],
                'Path': found['Name'],
                }



def register():
    Providers.register(AwsSsmTemplateProvider())

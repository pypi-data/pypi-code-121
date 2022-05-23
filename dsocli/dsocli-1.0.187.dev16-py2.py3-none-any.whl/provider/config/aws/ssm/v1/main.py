import boto3
from dsocli.exceptions import DSOException
from dsocli.logger import Logger
from dsocli.providers import Providers
from dsocli.configs import ConfigProvider
from dsocli.constants import *
from dsocli.aws_ssm_utils import *
from dsocli.appconfigs import AppConfigs, ContextMode


__default_spec = {
    'pathPrefix': '/dso/config/',
}

def get_default_spec():
    return __default_spec.copy()


class AwsSsmConfigProvider(ConfigProvider):

    def __init__(self):
        super().__init__('config/aws/ssm/v1')


    ### adds service name to the artifactory prefix
    def get_path_prefix(self):
        return AppConfigs.config_spec('pathPrefix')


    def list(self, uninherited=False, filter=None):
        Logger.debug(f"Listing SSM configuration settings: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        configuration = load_context_ssm_parameters(parameter_type='String', path_prefix=self.get_path_prefix(), uninherited=uninherited, filter=filter)
        result = []
        for key, details in configuration.items():
            item = {
                'Key': key,
                'RevisionId': str(details['Version']),
            }
            item.update(details)
            result.append(item)

        return result


    def set(self, key, value):
        Logger.debug(f"Checking configuration overwrites '{key}'...")
        assert_ssm_parameter_no_namespace_overwrites(key=key, path_prefix=self.get_path_prefix())
        Logger.debug(f"Locating configuration setting '{key}'...")
        found = locate_ssm_parameter_in_context_hierachy(key=key, path_prefix=self.get_path_prefix(), uninherited=True)
        if found and not found['Type'] == 'String':
            raise DSOException(f"Failed to add configuration setting '{key}' becasue the key is not available in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        path = get_ssm_path(context=AppConfigs.context, key=key, path_prefix=self.get_path_prefix())
        Logger.debug(f"Adding configuration setting: path={path}")
        response = add_ssm_paramater(path, value)
        result = {
                'RevisionId': str(response['Version']),
                'Key': key, 
                'Value': value,
                'Stage': AppConfigs.short_stage,
                'Scope': AppConfigs.context.scope_translation,
                'Origin': {
                    'Namespace': AppConfigs.namespace,
                    'Application': AppConfigs.application,
                    'Stage': AppConfigs.stage,
                },
                'Path': path,
            }
        result.update(response)
        return result



    def get(self, key, revision=None, uninherited=False, rendered=True):
        Logger.debug(f"Locating configuration setting '{key}'...")
        found = locate_ssm_parameter_in_context_hierachy(key=key, path_prefix=self.get_path_prefix())
        if not found:
            raise DSOException(f"Config '{key}' not found nor inherited in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        else:
            if not found['Type'] == 'String':
                raise DSOException(f"Configuration setting '{key}' not found in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        Logger.debug(f"Getting configuration setting from SSM: path={found['Name']}")
        response = get_ssm_parameter_history(found['Name'])
        configuration = sorted(response['Parameters'], key=lambda x: int(x['Version']), reverse=True)
        if revision is None:
            ### get the latest revision
            result = {
                    'RevisionId': str(configuration[0]['Version']),
                    'Date': configuration[0]['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key, 
                    'Value': configuration[0]['Value'],
                    'Scope': found['Scope'],
                    'Origin': found['Origin'],
                    'Path': found['Name'],
                    'User': configuration[0]['LastModifiedUser'],
                    }
                
        else:
            ### get specific revision
            configuration = [x for x in configuration if str(x['Version']) == revision]
            if not configuration:
                raise DSOException(f"Revision '{revision}' not found for parameter '{key}' in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
            result = {
                    'RevisionId':str(configuration[0]['Version']),
                    'Date': configuration[0]['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key, 
                    'Value': configuration[0]['Value'],
                    'Scope': found['Scope'],
                    'Origin': found['Origin'],
                    'Path': found['Name'],
                    'User': configuration[0]['LastModifiedUser'],
                    }

        return result


    def history(self, key, service):
        self.service = service
        Logger.debug(f"Locating configuration setting '{key}' on SSM: service={service}")
        found = locate_ssm_parameter_in_context_hierachy(key=key, path_prefix=self.get_path_prefix(service))
        if not found:
            raise DSOException(f"Config '{key}' not found in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        else:
            if not found['Type'] == 'String':
                raise DSOException(f"Config '{key}' not found in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        Logger.debug(f"Getting configuration from SSM: path={found['Name']}")
        response = get_ssm_parameter_history(found['Name'])
        parameters = sorted(response['Parameters'], key=lambda x: int(x['Version']), reverse=True)
        result = { "Revisions":
            [{
                'RevisionId': str(parameter['Version']),
                'Date': parameter['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                'Key': key,
                'Value': parameter['Value'],
                # 'Scope': found['Scope'],
                # 'Origin': found['Origin'],
                'User': parameter['LastModifiedUser'],
                # 'Path': found['Name'],
            } for parameter in parameters]
        }

        return result



    def unset(self, key):
        Logger.debug(f"Locating configuration setting '{key}'...")
        ### only configuration owned by the context can be deleted, hence uninherited=True
        found = locate_ssm_parameter_in_context_hierachy(key=key, path_prefix=self.get_path_prefix(), uninherited=True)
        if not found:
            raise DSOException(f"Configuration '{key}' not found in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        else:
            # if len(found) > 1:
            #     Logger.warn(f"More than one parameter found at '{found['Name']}'. The first one taken, and the rest were discarded.")
            if not found['Type'] == 'String':
                raise DSOException(f"Configuraton '{key}' not found in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        Logger.debug(f"Deleting configuration from SSM: path={found['Name']}")
        delete_ssm_parameter(found['Name'])
        result = {
                'Key': key,
                'Stage': found['Stage'],
                'Scope': found['Scope'],
                'Origin': found['Origin'],
                'Path': found['Name'],
                }
        return result


def register():
    Providers.register(AwsSsmConfigProvider())

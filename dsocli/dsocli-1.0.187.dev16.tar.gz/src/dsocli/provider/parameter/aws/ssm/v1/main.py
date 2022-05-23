import boto3
from dsocli.exceptions import DSOException
from dsocli.logger import Logger
from dsocli.providers import Providers
from dsocli.parameters import ParameterProvider
from dsocli.constants import *
from dsocli.aws_ssm_utils import *
from dsocli.appconfigs import AppConfigs, ContextMode


__default_spec = {
    'pathPrefix': '/dso/parameter/',
}

def get_default_spec():
    return __default_spec.copy()


class AwsSsmParameterProvider(ParameterProvider):

    def __init__(self):
        super().__init__('parameter/aws/ssm/v1')


    def get_path_prefix(self):
        return AppConfigs.parameter_spec('pathPrefix')


    def list(self, uninherited=False, filter=None):
        Logger.debug(f"Listing SSM parameters: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        parameters = load_context_ssm_parameters(parameter_type='String', path_prefix=self.get_path_prefix(), uninherited=uninherited, filter=filter)
        result = []
        for key, details in parameters.items():
            item = {
                'Key': key,
                'RevisionId': str(details['Version']),
            }
            item.update(details)
            result.append(item)

        return result

    def edit(self, key):
        Logger.debug(f"Editing SSM parameter: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        parameters = load_context_ssm_parameters(parameter_type='String', path_prefix=self.get_path_prefix(), uninherited=True, filter=f"^{key}$")
        if len(parameters) > 1:
            raise DSOException(f"Mutiple parameters found with the same key in the given context.")
        result = {}
        if parameters:
            result['Key'] = list(parameters.keys())[0]
            result.update(list(parameters.values())[0])

        return result

    def get(self, key, revision=None, uninherited=False, rendered=True):
        Logger.debug(f"Locating SSM parameter '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        found = locate_ssm_parameter_in_context_hierachy(key=key, path_prefix=self.get_path_prefix(), uninherited=uninherited)
        if not found:
            raise DSOException(f"Parameter '{key}' not found in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        else:
            if not found['Type'] == 'String':
                raise DSOException(f"Parameter '{key}' not found in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        Logger.debug(f"Getting SSM parameter: path={found['Name']}")
        response = get_ssm_parameter_history(found['Name'])
        parameters = sorted(response['Parameters'], key=lambda x: int(x['Version']), reverse=True)
        if revision is None:
            ### get the latest revision
            result = {
                    'RevisionId': str(parameters[0]['Version']),
                    'Date': parameters[0]['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key, 
                    'Value': parameters[0]['Value'],
                    'Scope': found['Scope'],
                    'Origin': found['Origin'],
                    'Path': found['Name'],
                    'User': parameters[0]['LastModifiedUser'],
                    }
                
        else:
            ### get specific revision
            parameters = [x for x in parameters if str(x['Version']) == revision]
            if not parameters:
                raise DSOException(f"Revision '{revision}' not found for parameter '{key}' in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
            result = {
                    'RevisionId':str(parameters[0]['Version']),
                    'Date': parameters[0]['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key, 
                    'Value': parameters[0]['Value'],
                    'Scope': found['Scope'],
                    'Origin': found['Origin'],
                    'Path': found['Name'],
                    'User': parameters[0]['LastModifiedUser'],
                    }

        return result


    def add(self, key, value):
        Logger.debug(f"Checking SSM parameter overwrites '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        assert_ssm_parameter_no_namespace_overwrites(key=key, path_prefix=self.get_path_prefix())
        Logger.debug(f"Locating SSM parameter '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        found = locate_ssm_parameter_in_context_hierachy(key=key, path_prefix=self.get_path_prefix(), uninherited=True)
        if found and not found['Type'] == 'String':
            raise DSOException(f"Failed to add parameter '{key}' becasue the key is not available in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        path = get_ssm_path(context=AppConfigs.context, key=key, path_prefix=self.get_path_prefix())
        Logger.debug(f"Adding SSM parameter: path={path}")
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





    def history(self, key):
        Logger.debug(f"Locating SSM parameter '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        found = locate_ssm_parameter_in_context_hierachy(key=key, path_prefix=self.get_path_prefix())
        if not found:
            raise DSOException(f"Parameter '{key}' not found in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        else:
            if not found['Type'] == 'String':
                raise DSOException(f"Parameter '{key}' not found in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        Logger.debug(f"Getting SSM parameter: path={found['Name']}")
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



    def delete(self, key):
        Logger.debug(f"Locating SSM parameter '{key}': namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        ### only parameters owned by the context can be deleted, hence uninherited=True
        found = locate_ssm_parameter_in_context_hierachy(key=key, path_prefix=self.get_path_prefix(), uninherited=True)
        if not found:
            raise DSOException(f"Parameter '{key}' not found in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        else:
            # if len(found) > 1:
            #     Logger.warn(f"More than one parameter found at '{found['Name']}'. The first one taken, and the rest were discarded.")
            if not found['Type'] == 'String':
                raise DSOException(f"Parameter '{key}' not found in the given context: namespace={AppConfigs.get_namespace(ContextMode.Target)}, application={AppConfigs.get_application(ContextMode.Target)}, stage={AppConfigs.get_stage(ContextMode.Target)}, scope={AppConfigs.scope}")
        Logger.debug(f"Deleting SSM parameter: path={found['Name']}")
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
    Providers.register(AwsSsmParameterProvider())

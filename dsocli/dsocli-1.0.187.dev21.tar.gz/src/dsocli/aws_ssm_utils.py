import re
import boto3
import logging
from .contexts import Contexts, Context
from .logger import Logger
from dsocli.configs import Config
from dsocli.exceptions import *

logging.getLogger('botocore').setLevel(Logger.mapped_level)
logging.getLogger('boto').setLevel(Logger.mapped_level)
logging.getLogger('boto3').setLevel(Logger.mapped_level)

ssm_resource_type = {
    'String': 'parameter',
    'SecureString': 'secret',
    'StringList': 'template',
}

ssm_null_value = '352e9018-684d-4c4f-a7d2-ceeb9e0fe947'
ssm_empty_value = '3b22cef4-8786-48e9-8521-0a1e45891a3c'


### AWS SSM Parameter store does not allow {{}}
def escape_curly_brackets(contents):
    return contents.replace('{{', r'\{\{').replace('}}', r'\}\}')


def unescape_curly_brackets(contents):
    return contents.replace(r'\{\{', '{{').replace(r'\}\}', '}}')


### AWS SSM Parameter store does not allow empty string or null values
def encode_nulls(value):
    if value is None:
        return ssm_null_value
    elif value == '':
        return ssm_empty_value
    else:
        return value


def decode_nulls(value):
    if value == ssm_null_value:
        return None
    elif value == ssm_empty_value:
        return ''
    else:
        return value



def get_ssm_path(context, key=None, path_prefix=''):
    if path_prefix.endswith('/'): path_prefix = path_prefix[:-1]
    return path_prefix + context.get_path(key)



def load_ssm_path(result, path, parameter_type, used_path_prefix='', decrypt=False, filter=None):
    ssm = boto3.session.Session().client(service_name='ssm')
    p = ssm.get_paginator('get_parameters_by_path')
    paginator = p.paginate(Path=path, Recursive=True, WithDecryption=decrypt, ParameterFilters=[{'Key': 'Type', 'Values': [parameter_type]}]).build_full_result()
    for parameter in paginator['Parameters']:
        key = parameter['Name'][len(path)+1:]
        if filter and not re.match(filter, key): continue
        if key in result:
            Logger.warn("Inherited {0} '{1}' was overridden.".format(ssm_resource_type[parameter_type] , key))
        ctx_path = path[len(used_path_prefix):]
        ctx = Context(*Contexts.parse_path(ctx_path)[0:3])
        details = {
                    # 'Value': unescape_curly_brackets(parameter['Value']) if parameter_type == 'StringList' else decode_nulls(parameter['Value']), 
                    'Value': decode_nulls(unescape_curly_brackets(parameter['Value'])),
                    'Path': parameter['Name'],
                    'Version': parameter['Version'],
                    'Stage': ctx.short_stage,
                    'Scope': ctx.scope_translation,
                    'Context': {
                        'Namespace': ctx.namespace,
                        'Application': ctx.application,
                        'Stage': ctx.stage,
                    },
                    'Date': parameter['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'ARN': parameter['ARN'],
                }
        result[key] = details
    return result



def load_context_ssm_parameters(parameter_type, path_prefix='', decrypt=False, uninherited=False, filter=None):
    ### construct search path in hierachy with no key specified
    paths = Contexts.get_hierachy_paths(context=Config.context, key=None, path_prefix=path_prefix, ignore_stage=Config.stage is None, uninherited=uninherited)
    parameters = {}
    for path in paths:
        Logger.debug(f"Loading SSM parameters: path={path}")
        load_ssm_path(result=parameters, path=path, parameter_type=parameter_type, used_path_prefix=path_prefix, decrypt=decrypt, filter=filter)
    return parameters



def locate_ssm_parameter_in_context_hierachy(key, path_prefix='', uninherited=False):
    result = {}
    paths = Contexts.get_hierachy_paths(context=Config.context, key=key, path_prefix=path_prefix, ignore_stage=Config.stage is None, uninherited=uninherited, reverse=True)
    ssm = boto3.session.Session().client(service_name='ssm')
    for path in paths:
        Logger.debug(f"Describing SSM parameter: path={path}")
        response = ssm.describe_parameters(ParameterFilters=[{'Key':'Name', 'Values':[path]}])
        if len(response['Parameters']) > 0:
            ctx_path = path[len(path_prefix):]
            ctx = Context(*Contexts.parse_path(ctx_path)[0:3])
            result = response['Parameters'][0]
            result['Stage'] = ctx.short_stage
            result['Scope'] = ctx.scope_translation
            result['Context']= {
                'Namespace': ctx.namespace,
                'Application': ctx.application,
                'Stage': ctx.stage,
            }
            break
    return result



def assert_ssm_parameter_no_namespace_overwrites(key, path_prefix=''):
    """
        check if a parameter will overwrite parent or childern parameters (with the same namespaces) in the same context (always uninherited)
        e.g.: 
            parameter a.b.c would overwrite a.b (super namespace)
            parameter a.b would overwrite all a.b.x (sub namespaces)
    """
    ssm = boto3.session.Session().client(service_name='ssm')
    
    ### check children parameters
    path = path_prefix + Config.context.get_path(key)
    response = ssm.describe_parameters(ParameterFilters=[{'Key':'Name', 'Option': 'BeginsWith', 'Values':[f"{path}."]}])
    if len(response['Parameters']) > 0:
        raise DSOException("Parameter key '{0}' is not allowed in the given context becasue it would otherwise overwrite '{0}.{1}' and all other parameters in '{0}.*' namespace if any.".format(key,response['Parameters'][0]['Name'][len(path)+1:]))

    ### check parent parameters
    namespaces = key.split('.')
    for n in range(len(namespaces)-1):
        subKey = '.'.join(namespaces[0:n+1])
        path = get_ssm_path(Config.context, subKey, path_prefix)
        Logger.debug(f"Describing SSM parameter: path={path}")
        # parameters = ssm.describe_parameters(ParameterFilters=[{'Key':'Type', 'Values':['String']},{'Key':'Name', 'Values':[path]}])
        response = ssm.describe_parameters(ParameterFilters=[{'Key':'Name', 'Values':[path]}])
        if len(response['Parameters']) > 0:
            raise DSOException("Parameter key '{0}' is not allowed in the given context becasue it would otherwise overwrite parameter '{1}'.".format(key, subKey))



def add_ssm_paramater(path, value):
    ssm = boto3.session.Session().client(service_name='ssm')
    return ssm.put_parameter(Name=path, Value=escape_curly_brackets(encode_nulls(value)), Type='String', Overwrite=True)



def add_ssm_secret(path, value):
    ssm = boto3.session.Session().client(service_name='ssm')
    return ssm.put_parameter(Name=path, Value=encode_nulls(value), Type='SecureString', Overwrite=True)



def add_ssm_template(path, contents):
    ssm = boto3.session.Session().client(service_name='ssm')
    return ssm.put_parameter(Name=path, Value=escape_curly_brackets(contents), Type='StringList', Overwrite=True)


def do_get_ssm_parameter_history(name, decrypt=False):
    ssm = boto3.session.Session().client(service_name='ssm')
    return ssm.get_parameter_history(Name=name, WithDecryption=decrypt)



def get_ssm_parameter_history(name):
    response = do_get_ssm_parameter_history(name)
    for i in range(0, len(response['Parameters'])):
        response['Parameters'][i]['Value'] = decode_nulls(unescape_curly_brackets(response['Parameters'][i]['Value']))
    return response



def get_ssm_secret_history(name, decrypt=False):
    response = do_get_ssm_parameter_history(name, decrypt)
    if decrypt:
        for i in range(0, len(response['Parameters'])):
            response['Parameters'][i]['Value'] = decode_nulls(response['Parameters'][i]['Value'])
    return response



def get_ssm_template_history(name):
    response = do_get_ssm_parameter_history(name)
    for i in range(0, len(response['Parameters'])):
        response['Parameters'][i]['Value'] = unescape_curly_brackets(response['Parameters'][i]['Value'])
    return response



def delete_ssm_parameter(name):
    ssm = boto3.session.Session().client(service_name='ssm')
    ssm.delete_parameter(Name=name)

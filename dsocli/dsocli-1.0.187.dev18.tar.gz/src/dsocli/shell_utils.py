import os
from .contexts import Context, Contexts
from .logger import Logger
from .stages import Stages
from dsocli.file_utils import *
from dsocli.exceptions import DSOException
from dsocli.dict_utils import *
from dsocli.local_utils import *
from dsocli.configs import Config

def expand_shell_parameters(parameters):
    for param in parameters:
        if not parameters[param]['Value'] is None: ### !important
            parameters[param]['Value'] = os.getenv(parameters[param]['Value'], '')
    return parameters


def locate_shell_parameter_in_context_hierachy(key, store_name, path_prefix='', uninherited=False, rendered=True):
    parameters = locate_parameter_in_context_hierachy(key=key, store_name=store_name, path_prefix=path_prefix, uninherited=uninherited)
    if rendered:
        return expand_shell_parameters(parameters)
    else:
        return parameters

def add_shell_parameter(key, value, store_name, path_prefix=''):
    return add_local_parameter(key=key, value=value, store_name=store_name, path_prefix=path_prefix)

def delete_shell_parameter(path, key):
    return delete_local_parameter(path=path, key=key)

def load_context_shell_parameters(store_name, path_prefix='', uninherited=False, filter=None, raw=False):
    parameters = load_context_local_parameters(store_name=store_name, path_prefix=path_prefix, uninherited=uninherited, filter=filter)
    if raw:
        return parameters
    else:
        return expand_shell_parameters(parameters)



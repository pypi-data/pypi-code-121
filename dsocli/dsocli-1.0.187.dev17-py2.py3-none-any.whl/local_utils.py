import os
import re
from .contexts import Context, Contexts
from .logger import Logger
from .stages import Stages
from dsocli.file_utils import *
from dsocli.exceptions import DSOException
from dsocli.dict_utils import *
from dsocli.configs import Config



def parse_local_path(path):
    return Contexts.parse_path(path.replace(os.sep, '/'))


def get_local_path(context, key=None, path_prefix=''):
    return os.path.join(path_prefix.replace('/', os.sep), context.get_path(key).replace('/', os.sep)[1:])


def get_parameter_store_path(store_name, path_prefix='', create=True):
    path = os.path.join(get_local_path(context=Config.context, key=None, path_prefix=path_prefix), store_name)
    fullPath = os.path.join(Config.working_dir, path)
    if not os.path.exists(fullPath):
        if create:
            os.makedirs(os.path.dirname(fullPath), exist_ok=True)
            open(fullPath, 'w').close()
    return path



def get_context_hierachy_local_paths(context, path_prefix='', ignore_stage=False, uninherited=False, reverse=False):
    result = Contexts.get_hierachy_paths(context=context, path_prefix=path_prefix, ignore_stage=ignore_stage, uninherited=uninherited, reverse=reverse)
    for i, path in enumerate(result):
        result[i] = path.replace('/', os.sep)
    return result


def load_templates_from_path(result, path, path_prefix='', include_contents=False, filter=None):
    for pth, subdirs, files in os.walk(path):
        for name in files:
            filePath = os.path.join(pth, name)
            if is_binary_file(filePath): continue
            ### temlate key is the filename stripped out 'path' from the begining
            key = filePath[len(path)+1:].replace(os.sep, '/')
            if filter and not re.match(filter, key): continue
            if key in result:
                Logger.warn(f"Inherited template '{key}' was overridden.")
            ctx_path = os.path.abspath(filePath)[len(os.path.abspath(Config.working_dir)) + 1 + len(path_prefix):].replace(os.sep, '/')
            ctx = Context(*Contexts.parse_path(ctx_path)[0:3])
            result[key] = {
                'Stage': ctx.short_stage,
                'Scope': ctx.scope_translation,
                'Context': {
                    'Namespace': ctx.namespace,
                    'Application': ctx.application,
                    'Stage': ctx.stage,
                },
                'Path': ctx.path,
                'Date': get_file_modified_date(filePath),
            }
            if include_contents:
                with open(filePath, 'r', encoding='utf-8') as f:
                    result[key]['Contents'] = f.read()

    return result


def load_context_templates(path_prefix='', uninherited=False, include_contents=False, filter=None):
    ### get templates in normal order (top to bottom)
    paths = get_context_hierachy_local_paths(context=Config.context, path_prefix=path_prefix, uninherited=uninherited)
    templates = {}
    for path in paths:
        Logger.debug(f"Loading templates: path={path}")
        load_templates_from_path(result=templates, path=os.path.join(Config.working_dir, path), path_prefix=path_prefix, include_contents=include_contents, filter=filter)

    return templates


def locate_template_in_context_hierachy(key, path_prefix='', include_contents=False, uninherited=False):
    templates = {}
    ### get templates in reverse order (more specific to general)
    paths = get_context_hierachy_local_paths(context=Config.context, path_prefix=path_prefix, uninherited=uninherited, reverse=True)
    for path in paths:
        load_templates_from_path(result=templates, path=os.path.join(Config.working_dir, path), path_prefix=path_prefix, include_contents=include_contents, filter=f"^{key}$")
        if key in templates: break

    return templates


def add_local_template(key, path_prefix, contents):
    path = get_local_path(context=Config.context, key=key, path_prefix=path_prefix)
    Logger.debug(f"Adding local template: path={path}")
    fullPath = os.path.join(Config.working_dir, path)
    os.makedirs(os.path.dirname(fullPath), exist_ok=True)
    with open(fullPath, 'w', encoding='utf-8') as f:
        f.write(contents)
    ctx_path = path[len(path_prefix):].replace(os.sep, '/')
    ctx = Context(*Contexts.parse_path(ctx_path)[0:3])
    result = {
        'Contents': contents,
        'Stage': ctx.short_stage,
        'Scope': ctx.scope_translation,
        'Context': {
            'Namespace': ctx.namespace,
            'Application': ctx.application,
            'Stage': ctx.stage,
        },
        'Path': path,
    }
    return result


def delete_local_template(path):
    ### remove possible starting / before joing path avoiding an absolute path
    path = re.sub(f'^/', '', path)
    fullPath = os.path.join(Config.working_dir, Config.config_dir, 'template', path)
    print(fullPath)
    if os.path.exists(fullPath):
        os.remove(fullPath)


def load_parameter_store(result, path, path_prefix='', filter=None):
    fullPath = os.path.join(Config.working_dir, path)
    if not os.path.exists(fullPath): return result
    parameters = flatten_dict(input=load_file(fullPath))
    for key, value in parameters.items():
        if filter and not re.match(filter, key): continue
        if key in result:
            Logger.warn(f"Inherited parameter '{key}' was overridden.")
        ctx_path = path[len(path_prefix):].replace(os.sep, '/')
        ctx = Context(*Contexts.parse_path(ctx_path)[0:3])
        result[key] = {
            'Value': value,
            'Stage': ctx.short_stage,
            'Scope': ctx.scope_translation,
            'Context': {
                'Namespace': ctx.namespace,
                    'Application': ctx.application,
                'Stage': ctx.stage,
            },
            'Path': path,
        }

    return result


def get_context_hierachy_parameter_stores(context, store_name, path_prefix='', uninherited=False, reverse=False):
    paths = get_context_hierachy_local_paths(context=context, path_prefix=path_prefix, uninherited=uninherited, reverse=reverse)
    stores = []
    for path in paths:
        ctx_path = path[len(path_prefix):].replace(os.sep, '/')
        ctx = Context(*Contexts.parse_path(ctx_path)[0:3])
        stores.append({
            'Stage': ctx.short_stage,
            'Stage': ctx.short_stage,
            'Context': {
                'Namespace': ctx.namespace,
                    'Application': ctx.application,
                'Stage': ctx.stage,
            },
            'Path': os.path.join(path, store_name),
        })
    return stores


def load_context_local_parameters(store_name, path_prefix='', uninherited=False, filter=None):
    ### get stores in normal order (top to bottom)
    stores = get_context_hierachy_parameter_stores(context=Config.context, store_name=store_name, path_prefix=path_prefix, uninherited=uninherited)
    parameters = {}
    for store in stores:
        Logger.debug(f"Loading store: path={store['Path']}")
        load_parameter_store(result=parameters, path=store['Path'], path_prefix=path_prefix, filter=filter)

    return parameters


def locate_parameter_in_context_hierachy(key, store_name, path_prefix='', uninherited=False):
    ### get stores in reverse order (more specific to general)
    stores = get_context_hierachy_parameter_stores(context=Config.context, store_name=store_name, path_prefix=path_prefix, uninherited=uninherited, reverse=True)
    parameters = {}
    for store_name in stores:
        Logger.debug(f"Loading store: path={store_name['Path']}")
        if os.path.exists(store_name['Path']):
            load_parameter_store(result=parameters, path=store_name['Path'], path_prefix=path_prefix, filter=f"^{key}$")
            if key in parameters: break

    return parameters


def add_local_parameter(key, value, store_name, path_prefix=''):
    path = get_parameter_store_path(store_name=store_name, path_prefix=path_prefix)
    Logger.debug(f"Local parameter store: path={path}")
    fullPath = os.path.join(Config.working_dir, path)
    params = load_file(file_path=fullPath)
    set_dict_value(dic=params, keys=key.split('.'), value=value, overwrite_parent=False, overwrite_children=False)
    save_data(data=params, file_path=fullPath)
    ctx_path = path[len(path_prefix):].replace(os.sep, '/')
    ctx = Context(*Contexts.parse_path(ctx_path)[0:3])
    result = {
        'Key': key,
        'Value': value,
        'Stage': Config.short_stage,
        'Scope': Config.context.scope_translation,
        'Context': {
            'Namespace': ctx.namespace,
            'Application': ctx.application,
            'Stage': ctx.stage,
        },
        'Path': path,

    }
    return result


def delete_local_parameter(path, key):
    params = load_file(file_path=path)
    del_dict_item(dic=params, keys=key.split('.'))
    del_dict_empty_item(dic=params, keys=key.split('.')[:-1])
    save_data(data=params, file_path=path)


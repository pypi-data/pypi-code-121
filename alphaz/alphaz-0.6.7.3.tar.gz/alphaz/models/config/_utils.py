import re, os, copy

PAREMETER_PATTERN = '{{%s}}'

def convert_value_for_environment(value: object) -> str:
    if str(value).lower() == 'true': value = '1'
    elif str(value).lower() == 'false': value = '0'
    return str(value)

def set_environment_variables(environs:dict):
    if environs:
        for key, value in environs.items():
            os.environ[key] = convert_value_for_environment(value)

def merge_configuration(configuration, source_configuration,replace=False,path=[],raise_duplicate:bool=False):
    for key2, value2 in source_configuration.items():
        if not key2 in configuration:
            configuration[key2] = value2
        elif replace:
            if type(value2) == dict:
                path.append(key2)
                merge_configuration(configuration[key2],source_configuration[key2],replace=replace,path=path)
            #elif type(value2) == list:
            else:
                configuration[key2] = value2
        elif raise_duplicate:
            raise ValueError(f'Duplicate key {key2} in configuration')


def get_parameters(content):
    title_regex = r'\{\{.*?\}\}'
    founds      = re.findall(title_regex,content)
    return founds

def get_mails_parameters(content):
    title_regex = r'\[\[.*?\]\]'
    founds      = re.findall(title_regex,content)
    return founds


def show(config,level=0):
    for key, cf in config.items():
        val = '' if type(cf) == dict else str(cf)
        print('{} {:30} {}'.format('   '*level,key,val))
        if type(cf) == dict:
            show(cf,level + 1)

def set_configs_paths(config,paths,parameters_values,configurations):
    levels = list(set([len(x) for x in paths]))

    for level in levels:
        for i in range(len(parameters_values)):
            if len(paths[i]) == level:
                set_configurations_path(config, paths[i], parameters_values[i], configurations)

def set_configurations_path(config,path,parameters,parameters_values):
    if len(path) == 1:
        matchs = get_configs_matchs(config[path[0]])
        if len(matchs) != 0 and matchs[0] in parameters_values:
            sub_configuration       = parameters_values[matchs[0]]
            replacement_data        = {x:y for x,y in sub_configuration.data.items() if x not in sub_configuration.tmp}
            config[path[0]]         = replacement_data
        return

    sub_config  = config[path[0]]
    path        = path[1:]

    set_configurations_path(sub_config,path,parameters,parameters_values)
    
def set_paths(config,paths,parameters_values,parameters_value):
    levels = list(set([len(x) for x in paths]))

    for level in levels:
        for i in range(len(parameters_values)):
            if len(paths[i]) == level:
                set_path(config, paths[i], parameters_values[i], parameters_value)

def set_path(config,path,parameters,parameters_values):
    if len(path) == 1:
        value   = config[path[0]]
        for parameter in parameters:
            if parameter in parameters_values:
                parameter_value     = parameters_values[parameter]
                if value == PAREMETER_PATTERN%parameter:
                    value           = parameter_value
                elif PAREMETER_PATTERN%parameter in str(value):
                    value           = value.replace(PAREMETER_PATTERN%parameter,str(parameter_value))
            
        config[path[0]]         = value

        return

    sub_config  = config[path[0]]
    path        = path[1:]

    set_path(sub_config,path,parameters,parameters_values)

def fill_config(configuration,source_configuration):
    for key, value in configuration.items():
        for key2, value2 in source_configuration.items():
            if type(value) != dict and PAREMETER_PATTERN%key2 in str(value):
                value = str(value).replace(PAREMETER_PATTERN%key2,value2)
        configuration[key] = value

def process_configuration(configuration,source_configuration,path=None):
    if path is None:
        fill_config(configuration,source_configuration)

        for key in source_configuration:
            fill_config(configuration,source_configuration[key])

        source  = source_configuration[keys[level]]

        fill_config()

def search_it(nested, target,path=None):
    found, paths = [], []
    if path is None:
        path = []

    if type(nested) == dict:
        for key, value in nested.items():
            next_path   = copy.copy(path)
            next_path.append(key)

            if isinstance(target,list) and len(target) == 1:
                target = target[0]
            
            if isinstance(target,list):
                if key == target[0]:
                    f, p = search_it(value, target[1:],next_path)
                    found.extend(f)
                    paths.extend(p)
            else:
                if key == target:
                    found.append(value)
                    paths.append(path)
            
            if isinstance(value, dict):
                f, p = search_it(value, target,next_path)
                found.extend(f)
                paths.extend(p)
            elif isinstance(value, list):
                i = 0
                for item in value:
                    if isinstance(item, dict):
                        path.append(i)
                        f, p = search_it(item, target, next_path)
                        found.extend(f)
                        paths.extend(p)
                    """else:
                        if key == target:
                            path.append(key)
                            found.append(value)"""
                    i += 1
    """elif type(nested) == list:
        for value in nested:
            if isinstance(item, dict):
                path.append(i)
                f, p = search_it(item, target, next_path)
                found.extend(f)
                paths.extend(p)"""
    return found, paths

def get_configs_matchs(string):
    return re.findall(r"\$config\(([^\$]+)\)",string)

def check_value(value,found,paths,object_type,next_path):
    parameters      = get_parameters(value)

    if object_type == 'parameters':
        results     = [ x.replace('{{','').replace('}}','') for x in parameters]
    else:
        results     = get_configs_matchs(value)

    if len(results) != 0:
        found.append( results)
        paths.append(next_path)

def get_object_from_config(nested,path=None,object_type='parameters'):
    found, paths = [], []
    if path is None:
        path = []

    if isinstance(nested, dict):
        for key, value in nested.items():
            next_path   = copy.copy(path)
            next_path.append(key)

            if isinstance(value, str):
                check_value(value,found,paths,object_type,next_path)
            elif isinstance(value, dict):
                f, p = get_object_from_config(value, next_path,object_type)
                found.extend(f)
                paths.extend(p)
            elif isinstance(value, list):
                f, p = get_object_from_config(value, next_path,object_type)
                found.extend(f)
                paths.extend(p)
    elif isinstance(nested, list):
        for i, value in enumerate(nested):
            next_path   = copy.copy(path)
            next_path.append(i)

            if isinstance(value, str):
                check_value(value,found,paths,object_type,next_path)
            elif isinstance(value, dict):
                f, p = get_object_from_config(value, next_path,object_type)
                found.extend(f)
                paths.extend(p)
            elif isinstance(value, list):
                f, p = get_object_from_config(value, next_path,object_type)
                found.extend(f)
                paths.extend(p)
    return found, paths

def get_parameters_from_config(nested, path=None):
    return get_object_from_config(nested,path=path,object_type='parameters')

def get_configs_from_config(nested, path=None):
    return get_object_from_config(nested,path=path,object_type='configs')

def get_values_for_parameters(config, parameter_name,path=None):
    """Get the values associated to the parameter in the configuration
    
    Arguments:
        config {json dict} -- configuration as a json dict 
        parameter_name {str} -- parameter_name to search
    
    Keyword Arguments:
        path {list} -- the current path in the json dict as a list (default: {None})
    
    Returns:
        tuple -- a tuple of the parameter values and the parameter path
    """
    found, paths = [], []
    if path is None:
        path = []

    for key, value in config.items():
        next_path   = copy.copy(path)
        next_path.append(key)

        if key == parameter_name:
            found.append(value)
            paths.append(path)
        
        if isinstance(value, dict):
            f, p = search_it(value, parameter_name, next_path)
            found.extend(f)
            paths.extend(p)
        elif isinstance(value, list):
            i = 0
            for item in value:
                if isinstance(item, dict):
                    path.append(i)
                    f, p = search_it(item, parameter_name, next_path)
                    found.extend(f)
                    paths.extend(p)
                i += 1
    return found, paths

LIMIT = 100
def set_parameter_value(parameters_value,l):
    if l > 10: 
        print('ERROR: replacement limit exceed for parameter %s'%parameters_value)
        exit()
    l += 1

    replaced    = False
    keys        = list(parameters_value.keys())
    for key, value in parameters_value.items():
        for k in keys:
            if "{{%s}}"%k in str(value) and "{{%s}}"%k != value:
                i = 0
                value       = replace_parameter(k,value,parameters_value[k],i)
                replaced    = True
        parameters_value[key] = value

    if replaced:
        set_parameter_value(parameters_value,l)

def replace_parameter(key,value,replace_value,i):
    if i > LIMIT: 
        print('ERROR: replacement limit exceed for parameter %s'%key)
        exit()
    i += 1

    if isinstance(value,dict):
        replacements = {}
        for k, v in value.items():
            vr = replace_parameter(key,v,replace_value,i)
            if v != vr:
                replacements[k] = vr
        for k, newv in replacements.items():
            value[k] = newv
    elif isinstance(value,list):
        replacements = {}
        i = 0
        for v in value:
            vr = replace_parameter(key,v,replace_value,i)
            if v != vr:
                replacements[i] = vr
            i += 1
        for i, newv in replacements.items():
            value[i] = newv
    else:
        if "{{%s}}"%key == value:
            value   = replace_value
        elif "{{%s}}"%key in str(value):
            value       = value.replace("{{%s}}"%key,replace_value)
    return value


def ensure_path(dict_object,paths=[],value=None):
    if len(paths) == 0: 
        return

    if not paths[0] in dict_object:
        dict_object[paths[0]] = {}

    if len(paths) == 1 and value is not None:
        dict_object[paths[0]] = value
        return

    ensure_path(dict_object[paths[0]],paths[1:],value=value)

def ensure_filepath(name:str,filepath:str,root:str,filename:str):
    name = name.split('/')[-1]
    if filepath is not None:    
        if not filepath[-5:] == '.json':
            filepath    = filepath + '.json'

        filename        = os.path.basename(filepath).split('.')[0]
        if root is None:
            root        = os.path.abspath(filepath).replace('%s.json'%filename,'')
        if name == 'config':
            name        = filename

    if root is None:
        stack           = inspect.stack()
        parentframe     = stack[1]
        module          = inspect.getmodule(parentframe[0])
        filename_frame  = parentframe.filename
        current_path    = os.getcwd()
        root            = current_path
    
    if filename is None:
        filename        = name.lower()

    filepath       = root + os.sep + filename + '.json'
    return name, filepath, root, filename
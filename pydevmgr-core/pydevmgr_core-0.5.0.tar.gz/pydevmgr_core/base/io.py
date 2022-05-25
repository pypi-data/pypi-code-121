import yaml
import os
import re
from pydantic import BaseModel
from typing import Tuple, Optional, List, Dict, Optional, Callable, Any
from ._yaml_loader import PydevmgrLoader

class IOConfig(BaseModel):
    cfgpath : str = 'CFGPATH'
    yaml_ext : Optional[List[str]] = ('.yml', '.yaml')
    YamlLoader = PydevmgrLoader
    
ioconfig = IOConfig()




_re_path_pattern = re.compile( '^([^\\[]+)\\[([^\\]]*)\\]$' )
def parse_file_name(file_name: str):
    """ split a file name into real file and path tuple"""
    g = _re_path_pattern.search(file_name)
    if not g:
        return file_name, None
    else:
        file, path = g[1], g[2]
         
        return file.strip(' '), tuple( p for p in path.strip(' ').split('.') if p)


def load_config(file_name: str, ioconfig: IOConfig = ioconfig) -> Dict:
    """ Load a configuration file into a dictionary
    
    The file name is given, it should be inside one of the path defined by the $CFGPATH 
    environment variable (or the one defined inside ioconfig.cfgpath). 
    
    Alternatively the path can be an absolute '/' path 

    For now only yaml configuration files are supported 
    
    At the end of the file name can be a path to a target value inside the configuration. Path are string separated by
    '.'
    
        e.g.
        
        ::
            
            assert load_config( 'myconfig.yml[a.b.c]' ) == load_config('myconfig.yml')['a']['b']['c']

    Args:
        file_name (str): config file name. Should be inside one of the path defined by the $CFGPATH 
        environment variable. Alternatively the file_name can be an abosolute path
        ioconfig (optional): a :class:`IOConfig`        

    Returns:
        cfg (dict): config dictionary
    """
    file_name, path = parse_file_name( file_name)
    return read_config(find_config(file_name, ioconfig = ioconfig), ioconfig = ioconfig, path=path)


def read_config(file: str, ioconfig: IOConfig =ioconfig, path=None) -> Dict:    
    """ Read the given configuration (yaml) file 
    
    Args:
        file (str): real file path, shall be a yaml file. 
    """
    if not path:
        with open(file) as f:
            return yaml.load(f.read(), Loader=ioconfig.YamlLoader)
    else:
        with open(file) as f:
            d = yaml.load(f.read(), Loader=ioconfig.YamlLoader)
            for p in path:
                if p:
                    try:
                        d = d[p]
                    except KeyError:
                        raise ValueError(f"Cannot resolve path {path!r} inside {file!r}")
            return d


def load_yaml(input: str, ioconfig: IOConfig =ioconfig) -> Any:
    return yaml.load(input, Loader=ioconfig.YamlLoader)

def find_config(file_name, ioconfig: IOConfig =ioconfig):
    """ find a config file and return its absolute path 
    
    Args:
        file_name (str): config file name. Should be inside one of the path defined by the $CFGPATH 
        environment variable. Alternatively the file_name can be an abosolute path
        ioconfig (optional): a :class:`IOConfig`        
    """
    path_list = os.environ.get(ioconfig.cfgpath, '.').split(':')
    for directory in path_list[::-1]:
        path = os.path.join(directory, file_name)
        if os.path.exists(path):
            return  path
    raise ValueError('coud not find config file %r in any of %s'%(file_name, path_list))

# overwrite the PydevmgrLoader.find_config method 
PydevmgrLoader.find_config = staticmethod(find_config)

    
def explore_config(filter: Optional[Callable] =None, ioconfig: IOConfig = ioconfig):
    """ Iterator on all config files found inside directories of the $CFGPATH environment variable 
    
    The iterator returns pairs of (relateve_path, root_directory)   

    Args:
        filter (None, callable, optional): if given it will receive the content for each file
               to filter
        ioconfig (optional): a :class:`IOConfig`

    Example:

    ::

        >>> list(explore_config(  lambda d: d['kind']=='Device' ))

    """
        
    path_list = os.environ.get(ioconfig.cfgpath, '.').split(':')
    found = set()
    
    for root in path_list[::-1]:
        for r, d, files in os.walk(root):
            for file in files:
                body, ext = os.path.splitext(file)
                if ext in ioconfig.yaml_ext:
                    p = os.path.relpath( os.path.join(r,file), root )
                    if not p in found:
                        if filter:
                            if filter(read_config(os.path.join(r,file))):
                                yield  p, root
                        else:
                            yield  p, root                                    
                    found.add(p)



def append_cfgpath( path: str, ioconfig: IOConfig = ioconfig):
    """ Add a new path to the $CFGPATH environment variable 

    Args:
        path (str): new config file directory 
        ioconfig (optional): a :class:`IOConfig` 
    """
    envpath = os.environ.get(ioconfig.cfgpath, '').split(':')
    envpath.append(path)
    os.environ[ioconfig.cfgpath] = ":".join(envpath)




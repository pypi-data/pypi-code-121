import yaml
import os
import pkg_resources
from jinja2 import Template
from pydevmgr_core.base import io as cio

class IOConfig(cio.IOConfig):
    resources : str = 'resources'

ioconfig = IOConfig()

# package name - not module
pkg_name = 'pydevmgr_elt'

def read_map(file, ioconfig=ioconfig):
    with open(file) as f:
        return yaml.load(f.read(), Loader=yaml.CLoader)

def read_config(file, ioconfig=ioconfig):    
    with open(file) as f:
        return yaml.load(f.read(), Loader=yaml.CLoader)

def load_config(file_name, ioconfig=ioconfig):
    return cio.load_config(file_name, ioconfig=ioconfig)
    


def load_map(file_name, ioconfig=ioconfig):
    return read_map(find_config(file_name, ioconfig=ioconfig))

def find_config(file_name, ioconfig=ioconfig):
    return cio.find_config(file_name, ioconfig=ioconfig)
    
def find_map(dev_type, ioconfig=ioconfig):
    """ locate the map file from the pydevmgr installation and return the absolute path 

    
    Args:
        dev_type (str):  Device type as 'Motor' the map file shall be found as mapMotor.yml inside 
        the package resource directories
    """
    resource_list = ['map'+dev_type+".yml", 'map'+dev_type.capitalize()+".yaml"]
    for resource in resource_list:
        if pkg_resources.resource_exists(pkg_name, os.path.join(ioconfig.resources, resource)):  
            break      
    else:
        raise IOError('coud not find map file of device %r from pydevmgr_elt package'%(dev_type))        
    return pkg_resources.resource_filename(pkg_name, os.path.join(ioconfig.resources, resource))



_default_map_cash = {}
def load_default_map(dev_type, ioconfig=ioconfig):
    """ load a map file according to a device type 
    
    The map file is a default one comming from the package
    
    Args: 
        dev_type (str): Device type as 'Motor' the map file shall be found as mapMotor.yml inside 
        the package resource directories (see :func:`find_map`)
    Returns:
       
       map:  A dictionary
       
    Raises:
       
       ValueError: if no default map file exists
    """
    try:
        map =  _default_map_cash[dev_type]
    except KeyError:
        map_file = find_map(dev_type, ioconfig=ioconfig)
        map = read_config(map_file, ioconfig=ioconfig)
        _default_map_cash[dev_type] = map
    return map
        
        
def find_template(dev_type):
    """ locate a template file from the pydevmgr installation and return the absolute path 
    
    templates rendered by jinja2 
    
    Args:
        dev_type (str):  Device type as 'Motor' the template file shall be found as templateMotor.yml inside 
        the package resource directories
    """
    
    resource = 'template'+dev_type.capitalize()+".yml"
    if not pkg_resources.resource_exists(pkg_name, os.path.join('resources',resource)):
        raise IOError('coud not find template file of device %r from pydevmgr_elt package'%(dev_type))        
    return pkg_resources.resource_filename(pkg_name, os.path.join('resources',resource))    

def render_template(dev_type, **kwargs):
    """ render a device template 

    Args:
        dev_type (str):  Device type as 'Motor' the template file shall be found as templateMotor.yml inside 
        the package resource directories
        **kwargs: any key/value used for the template render    
    """
    template_file =  find_template(dev_type)
    with open(template_file) as f:    
        return Template(f.read()).render(**kwargs)
    
def explore_config(what=None, ioconfig=ioconfig):
    """ Iterator on all config files found inside the $CFGPATH environment variable 
    
    Args:
        what (None, str, optional): "Manager" or "Motor", "Lamp", ... any device type
    
    """
    if what is None:
        def filter_func(cfg):
            return True
    elif what == "Manager":
        def filter_func(cfg):
            return 'server_id' in cfg
    else:
        def filter_func(cfg):
            if not len(cfg): return False
            c = next(iter(cfg.values()))
            if not isinstance(c, dict): return False
            try:
                return c['type'] == what
            except KeyError:
                return False
                
    return [(f,r) for f,r in cio.explore_config(filter_func, ioconfig=ioconfig)]
    

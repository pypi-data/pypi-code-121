import sys
from types import ModuleType


def reload_package(root_module):
    """Reload package in interpreter memory.
    
    Useful during development packages and simultaneous testing them at projects.
    
    Refs: 
        https://stackoverflow.com/a/2918951/14748231
    """
    package_name = root_module.__name__

    # get a reference to each loaded module
    loaded_package_modules = dict([
        (key, value) for key, value in sys.modules.items() 
        if key.startswith(package_name) and isinstance(value, ModuleType)])

    # delete references to these loaded modules from sys.modules
    for key in loaded_package_modules:
        del sys.modules[key]

    # load each of the modules again; 
    # make old modules share state with new modules
    for key in loaded_package_modules:
        print('loading %s' % key)
        newmodule = __import__(key)
        oldmodule = loaded_package_modules[key]
        oldmodule.__dict__.clear()
        oldmodule.__dict__.update(newmodule.__dict__)

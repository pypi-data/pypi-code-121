import os, sys, inspect

def get_path_name(path,ext=False):
    name = os.path.basename(path)
    if ext:
        return name
    return '.'.join(name.split('.')[:-1])

def add_previous_to_path(level=0,log=None):
    parentframe     = inspect.stack()[1]
    module          = inspect.getmodule(parentframe[0])
    root            = os.path.abspath(module.__file__).replace('\\','/').replace(module.__file__.replace('\\','/'),'')

    if log: log.debug('Add %s to system path'%root)

    sys.path.append(root)
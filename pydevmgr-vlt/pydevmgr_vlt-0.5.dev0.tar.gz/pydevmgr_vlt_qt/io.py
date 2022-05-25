import os
import pkg_resources
from pydevmgr_core.io import find_config

pkg_name = 'pydevmgr_vlt_qt'

def find_ui(resource):
    try:
        return find_config(resource)
    except ValueError:
        pass 
    
    if not pkg_resources.resource_exists(pkg_name, os.path.join('uis',resource)):
        raise IOError('coud not find ui file %r'%(resource))        
    return pkg_resources.resource_filename(pkg_name, os.path.join('uis',resource))   



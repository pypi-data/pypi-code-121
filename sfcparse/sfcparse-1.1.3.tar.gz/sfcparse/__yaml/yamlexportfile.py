# yamlexportfile
#########################################################################################################
# Imports
from typing import Any as __Any
import yaml as __yaml
from ..error import SfcparseError

# Exception for Module
class _Yamlexportfile: 
    class yamlexportfile(SfcparseError): __module__ = SfcparseError.set_module_name()


#########################################################################################################
# Export yaml file
def yamlexportfile(filename: str, data: __Any) -> None:
    """
    Exports a new file from python type to yaml data.
    
    Enter new filename as str. Pass any general data for output to file
    
    [Example Use]

    yamlexportfile('path/to/filename.yml', data)    

    This is using the PyYAML framework installed as a dependency from pypi. It is only using the
    "safe_dump" method, which only supports standard YAML tags and cannot represent an arbitrary Python object.
    For more information on PyYAML, visit: https://pypi.org/project/PyYAML/
    
    """
    # Export dict data to yaml file
    try:
        with open(filename, 'w') as f:
            __yaml.safe_dump(data, f)
    except __yaml.representer.RepresenterError as __err_msg: raise _Yamlexportfile.yamlexportfile(__err_msg, f'\nFILE:"{filename}" \nDATA:{data}')
    except TypeError as __err_msg: raise _Yamlexportfile.yamlexportfile(__err_msg, f'\nFILE:"{filename}" \nDATA:{data}')
    except ValueError as __err_msg: raise _Yamlexportfile.yamlexportfile(__err_msg, f'\nFILE:"{filename}" \nDATA:{data}')
    except FileNotFoundError as __err_msg: raise _Yamlexportfile.yamlexportfile(__err_msg, f'\nFILE:"{filename}" \nDATA:{data}')

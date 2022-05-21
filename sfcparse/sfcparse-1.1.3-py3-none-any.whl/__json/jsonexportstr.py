# jsonexportstr
#########################################################################################################
# Imports
import json as __json
from ..error import SfcparseError

# Exception for Module
class _Jsonexportstr: 
    class jsonexportstr(SfcparseError): __module__ = SfcparseError.set_module_name()


#########################################################################################################
# Export json str
def jsonexportstr(data: dict, indent_level: int=4) -> str:
    """
    Exports dictionary data to json string

    Returns a str. Assign the output to var

    [Example Use]

    jsonexportstr(dict, [optional] indent_level)

    This is using the native json library shipped with the python standard library. For more
    information on the json library, visit: https://docs.python.org/3/library/json.html
    
    """
    try:
        # Export dict data to json string
        return __json.dumps(data, indent=indent_level)
    except TypeError as __err_msg: raise _Jsonexportstr.jsonexportstr(__err_msg, f'\nDATA:{data} \nINDENT_LEVEL:{indent_level}')
    except ValueError as __err_msg: raise _Jsonexportstr.jsonexportstr(__err_msg, f'\nDATA:{data} \nINDENT_LEVEL:{indent_level}')


# jsonimportstr
#########################################################################################################
# Imports
import json as __json
from ..error import SfcparseError

# Exception for Module
class _Jsonimportstr: 
    class jsonimportstr(SfcparseError): __module__ = SfcparseError.set_module_name()


#########################################################################################################
# Import json string
def jsonimportstr(json_str_data: str) -> dict:
    """
    Imports json data from a string

    Returns a dict. Assign the output to var

    Enter json string as str to import.

    [Example Use]

    jsonimportstr('string with json data')

    This is using the native json library shipped with the python standard library. For more
    information on the json library, visit: https://docs.python.org/3/library/json.html
    """
    # Import json string    
    try:
        return __json.loads(json_str_data)
    except __json.decoder.JSONDecodeError as __err_msg: raise _Jsonimportstr.jsonimportstr(__err_msg, f'\nDATA:"{json_str_data}"')
    except TypeError as __err_msg: raise _Jsonimportstr.jsonimportstr(__err_msg, f'\nDATA:"{json_str_data}"')
    except ValueError as __err_msg: raise _Jsonimportstr.jsonimportstr(__err_msg, f'\nDATA:"{json_str_data}"')


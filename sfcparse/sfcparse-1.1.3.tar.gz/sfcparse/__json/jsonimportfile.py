# jsonimportfile
#########################################################################################################
# Imports
from os import path as __path
import json as __json
from ..error import SfcparseError

# Exception for Module
class _Jsonimportfile: 
    class jsonimportfile(SfcparseError): __module__ = SfcparseError.set_module_name()


#########################################################################################################
# Import json file
def jsonimportfile(filename: str) -> dict:
    """
    Imports json data from a file

    Returns a dict. Assign the output to var

    Enter json file location as str to import.

    [Example Use]

    jsonimportfile('path/to/filename.json')

    This is using the native json library shipped with the python standard library. For more
    information on the json library, visit: https://docs.python.org/3/library/json.html
    """
    # Import json file
    try:
        with open(filename, 'r') as f:
            # Check if file empty. Returns empty dict if empty
            if __path.getsize(filename) == 0:                
                raise SyntaxError(__err_msg)
            return __json.load(f)
    except FileNotFoundError as __err_msg: raise _Jsonimportfile.jsonimportfile(__err_msg, f'\nFILE:"{filename}"')
    except OSError as __err_msg: raise _Jsonimportfile.jsonimportfile(__err_msg, f'\nFILE:"{filename}"')
    except __json.decoder.JSONDecodeError as __err_msg: raise _Jsonimportfile.jsonimportfile(__err_msg, f'\nFILE:"{filename}"')

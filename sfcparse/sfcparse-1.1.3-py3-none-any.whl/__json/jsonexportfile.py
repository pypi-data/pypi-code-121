# jsonexportfile
#########################################################################################################
# Imports
import json as __json
from ..error import SfcparseError

# Exception for Module
class _Jsonexportfile: 
    class jsonexportfile(SfcparseError): __module__ = SfcparseError.set_module_name()


#########################################################################################################
# Export json file
def jsonexportfile(filename: str, data: dict) -> None:
    """
    Exports a new file from a dictionary to json data.
    
    Enter new filename as str. Pass dict data for output to file
    
    [Example Use]

    jsonexportfile('path/to/filename.json', data)    

    This is using the native json library shipped with the python standard library. For more
    information on the json library, visit: https://docs.python.org/3/library/json.html
    
    """
    try:
        # Export dict data to json file
        with open(filename, 'w') as f:
            __json.dump(data, f)
    except TypeError as __err_msg: raise _Jsonexportfile.jsonexportfile(__err_msg, f'\nFILE:"{filename}" \nDATA:{data}')
    except ValueError as __err_msg: raise _Jsonexportfile.jsonexportfile(__err_msg, f'\nFILE:"{filename}" \nDATA:{data}')
    except FileNotFoundError as __err_msg: raise _Jsonexportfile.jsonexportfile(__err_msg, f'\nFILE:"{filename}"')

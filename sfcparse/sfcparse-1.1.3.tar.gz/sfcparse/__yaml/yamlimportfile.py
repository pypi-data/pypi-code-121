# yamlimportfile
#########################################################################################################
# Imports
from os import path as __path
import yaml as __yaml
from ..error import SfcparseError

# Exception for Module
class _Yamlimportfile: 
    class yamlimportfile(SfcparseError): __module__ = SfcparseError.set_module_name()


#########################################################################################################
# Import yaml file
def yamlimportfile(filename: str) -> dict:
    """
    Imports yaml data from a file.

    Returns a dict. Assign the output to var

    Enter yaml file location as str to import.

    [Example Use]

    yamlimportfile('path/to/filename.yml')

    This is using the PyYAML framework installed as a dependency from pypi. It is only using the
    "safe_load" method to protect from untrusted input.
    For more information on PyYAML, visit: https://pypi.org/project/PyYAML/
    """
    # Import yaml file
    try:
        with open(filename, 'r') as f:
            # Check if file empty. Returns empty dict if empty
            if __path.getsize(filename) == 0:                
                return None
            return __yaml.safe_load(f)
    except FileNotFoundError as __err_msg: raise _Yamlimportfile.yamlimportfile(__err_msg, f'\nFILE: "{filename}"')
    except OSError as __err_msg: raise _Yamlimportfile.yamlimportfile(__err_msg, f'\nFILE: "{filename}"')
    except __yaml.scanner.ScannerError as __err_msg: raise _Yamlimportfile.yamlimportfile(__err_msg, f'\nFILE: "{filename}"')
    except ValueError as __err_msg: raise _Yamlimportfile.yamlimportfile(__err_msg, f'\nFILE: "{filename}"')
    except TypeError as __err_msg: raise _Yamlimportfile.yamlimportfile(__err_msg, f'\nFILE: "{filename}"')

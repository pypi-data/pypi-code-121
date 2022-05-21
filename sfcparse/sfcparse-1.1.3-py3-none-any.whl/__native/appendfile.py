# appendfile
#########################################################################################################
# Imports
from typing import Any as __Any
from os import path as __path
from ..error import SfcparseError

# Exception for Module
class _Appendfile: 
    class appendfile(SfcparseError): __module__ = SfcparseError.set_module_name()


#########################################################################################################
# Append Data to File
def appendfile(filename: str, *data: __Any):
    """
    Appends any data to a file.

    Enter existing filename as str, Pass any data type for output to file.

    [Example Use]
    appendfile('filename.test' or 'path/to/filename.test', 'data1', 'data2')
    """

    # Append data to file
    __new_line = '\n'

    # Check if file empty. Throws error if file not found
    try: 
        if __path.getsize(filename) == 0: __new_line = ''
    except FileNotFoundError as __err_msg: raise _Appendfile.appendfile(__err_msg, f'"{filename}"')

    with open(filename, 'a') as f:
        for data_to_write in data:
            f.writelines(f"{__new_line}{data_to_write}")

# importfile
#########################################################################################################
# Imports
from ast import literal_eval as __literal_eval__
from os import path as __path
from ..error import SfcparseError

# Exception for Module
class _Importfile: 
    class importfile(SfcparseError): __module__ = SfcparseError.set_module_name()


#########################################################################################################
# Import py Data from File
class __importfile:
    class file_data:
        def __init__(self, filename: str, attrib_name_dedup: bool):

            # Validate file exists. Open and Import Config File into Class Object then return the object    
            try:
                with open(filename, 'r') as f:
                    f = f.read().splitlines()
            except FileNotFoundError as __err_msg: raise _Importfile.importfile(__err_msg, f'"{filename}"')

            # Syntax Error Message
            __py_syntax_err_msg = "Must have valid Python data types to import, or file is not formatted correctly"
            __name_preexists_err_msg = "Name already preexists. Must give unique attribute names in file"
            
            # Data Build Setup and Switches        
            __is_building_data_sw = False
            __body_build_data_sw = False
            __end_data_build_sw = False
            __build_data = ''

            # Markers
            __start_markers = {'[','{','('}
            __end_markers = {']','}',')'}
            __skip_markers = {'',' ','#','\n'}
            __eof_marker = f[-1]

            # Main File Loop
            for __file_data_line in f:

                # Set Skip Marker
                try: __skip_marker = __file_data_line[0]
                except IndexError: __skip_marker = ''

                # Skip Comments, Blank Lines, and potential New Lines
                if (__is_building_data_sw == False) and (__skip_marker in __skip_markers): continue

                # Set Syntax Check
                try: __syntax_check = __file_data_line.split()[1]
                except IndexError: __syntax_check = ''

                # Basic Syntax Check
                if (__syntax_check == '=') or (__is_building_data_sw):

                    if not __is_building_data_sw:
                        __var_token = __file_data_line.split('=')[0].strip()
                        __value_token = __file_data_line.split('=')[1].strip()
                        __value_token_multi = __file_data_line.split('=')[1].split()[0].strip()
                        __last_token = __file_data_line.split('=')[-1].strip()
                        try: __start_skip_token = __file_data_line.split('=')[1].split()[1][0].strip()
                        except IndexError: __start_skip_token = ''
                        
                    if __is_building_data_sw:
                        try: __end_token = __file_data_line[0]
                        except IndexError: __end_token = ''
                    
                    # START BUILD: Check if value in file line is only Start Marker. Check if Multiline or Single Line
                    if (__value_token_multi in __start_markers) and ((__last_token in __start_markers) or (__start_skip_token[0] in __skip_markers)) and (__is_building_data_sw == False):
                        
                        if (attrib_name_dedup) and (hasattr(self, __var_token)):
                                raise _Importfile.importfile(__name_preexists_err_msg, f'\nFILE: "{filename}" \nATTRIB_NAME: {__var_token}')

                        __build_data = __value_token
                        
                        # Turn ON Data Build Switches
                        __is_building_data_sw = True
                        __body_build_data_sw = True
                        __end_data_build_sw = True
                        continue
                    
                    # END BUILD: Check if line of file is an End Data Build Marker. Import Built Data Type if Valid. Check if EOF in case File Missing End Marker.
                    elif (__end_data_build_sw) and ((__end_token in __end_markers) or (f"{__eof_marker}" == f"{__file_data_line}")):
                        __build_data += f"\n{__file_data_line}"
                        
                        try: setattr(self, __var_token, __literal_eval__(__build_data))
                        except SyntaxError: raise _Importfile.importfile(__py_syntax_err_msg, f'"{filename}"')

                        # Turn OFF Data Build Switches
                        __is_building_data_sw = False
                        __body_build_data_sw = False
                        __end_data_build_sw = False
                        __build_data = ''
                        continue

                    # CONT BUILD: Continue to Build Data
                    elif __body_build_data_sw:
                        __build_data += f"\n{__file_data_line}"
                        
                    # IMPORT SINLGE LINE VALUES: If not multiline, assume single
                    else:
                        try: 
                            if (attrib_name_dedup) and (hasattr(self, __var_token)):
                                raise _Importfile.importfile(__name_preexists_err_msg, f'\nFILE: "{filename}" \nATTRIB_NAME: {__var_token}')
                            
                            setattr(self, __var_token, __literal_eval__(__value_token))
                            
                        except ValueError: raise _Importfile.importfile(__py_syntax_err_msg, f'"{filename}"')
                
                else: raise _Importfile.importfile(__py_syntax_err_msg, f'"{filename}"')


def importfile(filename: str, attrib_name_dedup: bool=True) -> '__importfile.file_data':
    """
    Imports saved python data from any text file.

    Returns a class of attributes. Assign the output to var

    Enter file location as str to import.

    Accepted data types: str, int, float, bool, list, dict, tuple, set, nonetype, bytes

    Returns None if file empty

    [Example Use]
    importfile('filename.data' or 'path/to/filename.data')
    """
    __err_msg_file = 'Invalid data type or nothing specified for filename:'
    __err_msg_attrib = 'Invalid data type or nothing specified for attrib_name_dedup:'
    
    # Error Checks
    if not isinstance(filename, str): raise _Importfile.importfile(__err_msg_file, f'"{filename}"')
    if not isinstance(attrib_name_dedup, bool): raise _Importfile.importfile(__err_msg_attrib, f'"{attrib_name_dedup}"')

    # Check if file empty. Returns None if empty
    try:
        if __path.getsize(filename) == 0:
            return None
    except FileNotFoundError as __err_msg: raise _Importfile.importfile(__err_msg, f'"{filename}"')

    # Return Final Import
    return __importfile.file_data(filename, attrib_name_dedup)

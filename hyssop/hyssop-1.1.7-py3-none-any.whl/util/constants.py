# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: August 27th 2020 12:27:01 pm
'''

Localization_File = 'local.csv'

# base localization code
LocalCode_No_Code = 0                                   # args: (str, str)
LocalCode_Duplicated_Code = 1                           # args: (str, str)
LocalCode_Local_Pack_Parsing_Error = 2                  # args: (str)
LocalCode_Message_Format_Invalid = 3                    # args: (Tuple)

# asynccontextmanager
LocalCode_Not_Async_Gen = 10                            # args: ()
LocalCode_Not_Yield = 11                                # args: ()
LocalCode_Not_Stop = 12                                 # args: ()
LocalCode_Not_Stop_After_Throw = 13                     # args: ()

# callbacks
LocalCode_Not_Valid_Enum = 20                           # args: (Union[Enum, str], Enum)
LocalCode_Not_ASYNC_FUNC = 21                           # args: (Callable)
LocalCode_Invalid_Thread_Safe_Call = 22                 # args: (int, int)

# dynamic class enum
LocalCode_Must_Be_3Str_Tuple = 30                       # args: ()
LocalCode_Must_Be_Class = 31                            # args: (Type)
LocalCode_Must_Be_Function = 32                         # args: (Callable)
LocalCode_Is_Not_Subclass = 33

# hierarchy element
LocalCode_Not_HierarchyElementMeta_Subclass = 40        # args: (str)
LocalCode_No_Parameters = 41                            # args: (type)
LocalCode_Parameters_No_Key = 42                        # args: (type, str)

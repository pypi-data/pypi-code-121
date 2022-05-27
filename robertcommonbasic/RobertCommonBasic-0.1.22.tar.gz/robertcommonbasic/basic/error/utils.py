"""
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!! PLEASE READ BEFORE EDITING THIS PART !!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

This file defines COMMON error codes. COMMON means "not related to any specific module".
If an error is bound to specific module, please define it in the errorcode.py in the folder of that module.

*******************************************
** DO NOT PUT NON-COMMON ERROR CODE HERE **
**                                       **
** DO NOT MAKE THIS FILE TOO BIG         **
*******************************************
"""

from typing import Union

# Success
S_OK = 'S_OK'

# Some issue happens in robert itself, most probably a bug.
E_INTERNAL = 'E_INTERNAL'

# Input data is malformed
E_INPUT_DATA = 'E_INPUT_DATA'

# Input file is malformed or corrupted
E_INPUT_FILE = 'E_INPUT_FILE'

# communication error
E_COMM_ERROR = 'E_COMM_ERROR'


class robertResponse:
    def __init__(self, msg: str='', code: str='1', data: Union[dict, list]={}):
        self.msg = msg
        self.code = code
        self.data = data

class RobertError(Exception):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], dict):
            option = args[0]
        elif len(args) == 2:
            option = dict(code=args[0], msg=args[1])
        else:
            option = kwargs
        if 'code' not in option:
            option['code'] = E_INTERNAL
        if 'msg' not in option:
            option['msg'] = str(option['code'])
        super().__init__(option)

    @property
    def code(self):
        # pylint: disable=unsubscriptable-object
        return self.args[0]['code']

    @property
    def msg(self):
        # pylint: disable=unsubscriptable-object
        return self.args[0]['msg']


class InputDataError(RobertError):
    def __init__(self, msg: str):
        super().__init__(code=E_INPUT_DATA, msg=msg)


class InternalError(RobertError):
    def __init__(self, msg: str):
        super().__init__(code=E_INTERNAL, msg=msg)


class InternalDataError(InternalError):
    def __init__(self, msg: str):
        super().__init__(f"[DATA ERROR] {msg}")


class CommunicationError(RobertError):
    def __init__(self, msg: str):
        super().__init__(code=E_COMM_ERROR, msg=msg)
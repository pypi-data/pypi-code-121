from pydevmgr_ua import UaRpc
from pydevmgr_core import record_class
from .tools import enum_txt, get_txt
from enum import Enum

class RPC_ERROR(int, Enum):
    OK =  0
    NOT_OP =  -1
    NOT_NOTOP_READY =  -2
    NOT_NOTOP_NOTREADY = -3
    LOCAL =  -4
    
    UNREGISTERED = -9999 
    # etc ...
enum_txt( {
    RPC_ERROR.OK:					 'OK',
    RPC_ERROR.NOT_OP:				 'Cannot control motor. Not in OP state.',
    RPC_ERROR.NOT_NOTOP_READY:	     'Call failed. Not in NOTOP_READY.',
    RPC_ERROR.NOT_NOTOP_NOTREADY:	 'Call failed. Not in NOTOP_NOTREADY/ERROR.',
    RPC_ERROR.LOCAL:				 'RPC calls not allowed in Local mode.',
    RPC_ERROR.UNREGISTERED:			 'Unregistered RPC Error',
    # etc 
})

@record_class
class EltRpc(UaRpc):
    class Config(UaRpc.Config):
        type: str = "Elt"
    
    RPC_ERROR = RPC_ERROR
    
    def get_error_txt(self, rpc_error: int) -> str:
        """ get a text description of the rpc_error code 
        
        See the enumerator RPC_ERROR attribute 
        
        Args:
            rpc_error (int): rpc error code  
        """
        return get_txt( self.RPC_ERROR(rpc_error) )
        

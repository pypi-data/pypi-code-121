
from pydevmgr_core import  NodeAlias1, Defaults 
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt

from enum import Enum
Base = EltDevice.Rpcs

R = Base.Rpc # Base Node
RC = R.Config
RD = Defaults[RC] # this typing var says that it is a Rpc object holding default values 


class RPC_ERROR(int, Enum):
    OK =  0
    NOT_OP				= -1			
    NOT_NOTOP_READY		= -2			
    NOT_NOTOP_NOTREADY	= -3	
    STILL_OPENING = -4
    STILL_CLOSING = -5
    LOCAL = -6
    
    UNREGISTERED = -9999
    
enum_txt ({ # copy past on MgetRpcErrorTxt in PLC
        RPC_ERROR.OK:					 'OK',
	    RPC_ERROR.NOT_OP:				 'Cannot control shutter. Not in OP state.',
	    RPC_ERROR.NOT_NOTOP_READY:	     'Call failed. Not in NOTOP_READY.',
	    RPC_ERROR.NOT_NOTOP_NOTREADY:	 'Call failed. Not in NOTOP_NOTREADY/ERROR.',
	    RPC_ERROR.STILL_OPENING:		 'Not allowed to close the shutter while opening.',
	    RPC_ERROR.STILL_CLOSING:		 'Not allowed to open the shutter while closing.',
	    RPC_ERROR.LOCAL:				 'RPC calls not allowed in Local mode.',
        
        RPC_ERROR.UNREGISTERED:          'Unregistered RPC Error',
})



class ShutterRpcs(Base):
    RPC_ERROR = RPC_ERROR

    class Config(Base.Config):
        rpcClose: RD = RC(suffix= 'RPC_Close')
        rpcDisable: RD = RC(suffix= 'RPC_Disable')
        rpcEnable: RD = RC(suffix= 'RPC_Enable')
        rpcInit: RD = RC(suffix= 'RPC_Init')
        rpcOpen: RD = RC(suffix= 'RPC_Open')
        rpcReset: RD = RC(suffix= 'RPC_Reset')
        rpcStop: RD = RC(suffix= 'RPC_Stop')


if __name__ == "__main__":
    s = ShutterRpcs()
    s.rpcClose

from pydevmgr_core import  NodeAlias1, Defaults 
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt

from enum import Enum
Base = EltDevice.Rpcs

R = Base.Rpc # Base Node
RC = R.Config
RD = Defaults[RC] # this typing var says that it is a Rpc object holding default values 



### #############
#
# RPC error
class RPC_ERROR(int, Enum):    
    OK                 =  0     
    NOT_OP             = -1    
    NOT_NOTOP_READY    = -2    
    NOT_NOTOP_NOTREADY = -3    
    SWITCHING_ON       = -4    
    SWITCHING_OFF      = -5    
    COOLING            = -6    
    LOCAL              = -7
    
    UNREGISTERED = -9999
enum_txt ( {
    RPC_ERROR.OK:						 'OK',
	RPC_ERROR.NOT_OP:					 'Cannot control lamp. Not in OP state.',
	RPC_ERROR.NOT_NOTOP_READY:		 'Call failed. Not in NOTOP_READY.',
	RPC_ERROR.NOT_NOTOP_NOTREADY:		 'Call failed. Not in NOTOP_NOTREADY/ERROR.',
	RPC_ERROR.SWITCHING_ON:			 'Lamp OFF failed. Still switching ON.',
	RPC_ERROR.SWITCHING_OFF:			 'Lamp ON failed. Still switching OFF.',
	RPC_ERROR.COOLING:				 'Lamp ON failed. Still cooling down.',
	RPC_ERROR.LOCAL:					 'RPC calls not allowed in Local mode',
    RPC_ERROR.UNREGISTERED:           'Unregistered RPC Error'
})





class LampRpcs(Base):
    RPC_ERROR = RPC_ERROR

    class Config(Base.Config):
        rpcDisable: RD = RC(suffix= 'RPC_Disable')
        rpcEnable: RD = RC(suffix= 'RPC_Enable')
        rpcInit: RD = RC(suffix= 'RPC_Init')
        rpcReset: RD = RC(suffix= 'RPC_Reset')
        rpcStop: RD = RC(suffix= 'RPC_Stop')
        rpcSwitchOff: RD = RC(suffix= 'RPC_Off')
        rpcSwitchOn: RD = RC(suffix= 'RPC_On', arg_parsers=['Float', 'UaUInt32'] )


 



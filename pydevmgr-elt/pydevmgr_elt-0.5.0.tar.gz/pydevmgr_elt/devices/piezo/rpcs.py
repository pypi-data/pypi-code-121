from pydevmgr_core import  NodeAlias1, Defaults 
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt

from enum import Enum
Base = EltDevice.Rpcs

R = Base.Rpc # Base Node
RC = R.Config
RD = Defaults[RC] # this typing var says that it is a Rpc object holding default values 

### ##############
# RPC error
class RPC_ERROR(int, Enum):
    OK			                =  0
    NOT_OP                      = -1
    NOT_NOTOP_READY		        = -2
    NOT_NOTOP_NOTREADY          = -3
    MOVING_USER                 = -5
    MOVING_BIT                  = -6
    LOCAL                       = -7
    
    UNREGISTERED = -9999

# Add text definition to each constants, the definition is then accessible throught .txt attribute 
enum_txt ({
    RPC_ERROR.OK:						 'OK',
    RPC_ERROR.NOT_OP:					 'Cannot control device. Not in OP state.',
    RPC_ERROR.NOT_NOTOP_READY:		     'Call failed. Not in NOTOP_READY.',
    RPC_ERROR.NOT_NOTOP_NOTREADY:		 'Call failed. Not in NOTOP_NOTREADY/ERROR.',
    RPC_ERROR.LOCAL:					 'RPC calls not allowed in Local mode.',
    RPC_ERROR.MOVING_USER:			     'Set user value out of range.',
    RPC_ERROR.MOVING_BIT:				 'Set bit value out of range.',
    
    RPC_ERROR.UNREGISTERED:          'Unregistered RPC Error',
    })



class PiezoRpcs(Base):
    RPC_ERROR = RPC_ERROR

    class Config(Base.Config):
        rpcAuto: RD = RC(suffix= 'RPC_Auto')
        rpcDisable: RD = RC(suffix= 'RPC_Disable')
        rpcEnable: RD = RC(suffix= 'RPC_Enable')
        rpcHome: RD = RC(suffix= 'RPC_Home')
        rpcInit: RD = RC(suffix= 'RPC_Init')
        rpcMoveBits: RD = RC(suffix= 'RPC_MoveBit', arg_parsers=['UaInt16', 'UaInt16', 'UaInt16'] )
        rpcMoveUser: RD = RC(suffix= 'RPC_MoveUser', arg_parsers=['Float', 'Float', 'Float'] )
        rpcPos: RD = RC(suffix= 'RPC_Pos')
        rpcReset: RD = RC(suffix= 'RPC_Reset')
        rpcStop: RD = RC(suffix= 'RPC_Stop')
 



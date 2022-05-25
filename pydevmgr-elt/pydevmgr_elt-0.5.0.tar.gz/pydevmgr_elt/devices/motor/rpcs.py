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
    OK =  0
    NOT_OP =  -1
    NOT_NOTOP_READY =  -2
    NOT_NOTOP_NOTREADY = -3
    LOCAL =  -4
    SW_LIMIT_LOWER = -5
    SW_LIMIT_UPPER = -6
    INIT_WHILE_MOVING = -7
    
    UNREGISTERED = -9999
    
enum_txt ( {
    RPC_ERROR.OK:					 'OK',
    RPC_ERROR.NOT_OP:				 'Cannot control motor. Not in OP state.',
    RPC_ERROR.NOT_NOTOP_READY:	     'Call failed. Not in NOTOP_READY.',
    RPC_ERROR.NOT_NOTOP_NOTREADY:	 'Call failed. Not in NOTOP_NOTREADY/ERROR.',
    RPC_ERROR.LOCAL:				 'RPC calls not allowed in Local mode.',
    RPC_ERROR.SW_LIMIT_LOWER:		 'Move rejected. Target Pos < Lower SW Limit',
    RPC_ERROR.SW_LIMIT_UPPER:		 'Move rejected. Target Pos > Upper SW Limit',
    RPC_ERROR.INIT_WHILE_MOVING:	 'Cannot INIT moving motor. Motor stopped. Retry.',
    
    RPC_ERROR.UNREGISTERED:          'Unregistered RPC Error',
})



class MotorRpcs(Base):
    RPC_ERROR = RPC_ERROR

    class Config(Base.Config):
        rpcDisable: RD = RC(suffix= 'RPC_Disable')
        rpcEnable: RD = RC(suffix= 'RPC_Enable')
        rpcInit: RD = RC(suffix= 'RPC_Init')
        rpcMoveAbs: RD = RC(suffix= 'RPC_MoveAbs', arg_parsers=['Float', 'Float'] )
        rpcMoveRel: RD = RC(suffix= 'RPC_MoveRel', arg_parsers=['Float', 'Float'] )
        rpcMoveVel: RD = RC(suffix= 'RPC_MoveVel', arg_parsers=['Float'] )
        rpcReset: RD = RC(suffix= 'RPC_Reset')
        rpcStop: RD = RC(suffix= 'RPC_Stop')



 



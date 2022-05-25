from pydevmgr_core import  NodeAlias1, Defaults 
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt

from enum import Enum
Base = EltDevice.Interface

R = Base.Rpc # Base Node
RC = R.Config
RD = Defaults[RC] # this typing var says that it is a Rpc object holding default values 


class RPC_ERROR(int, Enum):
    
    UNREGISTERED = -9999
    
enum_txt ({ # copy past on MgetRpcErrorTxt in PLC
          
        RPC_ERROR.UNREGISTERED:          'Unregistered RPC Error',
})



class CcsSimRpcs(Base):
    RPC_ERROR = RPC_ERROR
    
    class Config(Base.Config):
        rpcSetCoordinates:  RD = RC(suffix="RPC_SetCoordinates", arg_parsers=[float, float, float])



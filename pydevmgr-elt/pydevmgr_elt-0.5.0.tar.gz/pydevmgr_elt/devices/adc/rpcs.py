from pydevmgr_core import  NodeAlias1, Defaults 
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt
from pydevmgr_elt.devices.motor import Motor

from enum import Enum
Base = EltDevice.Rpcs

R = Base.Rpc # Base Node
RC = R.Config
RD = Defaults[RC] # this typing var says that it is a Rpc object holding default values 

RPC_ERROR = Motor.Rpcs.RPC_ERROR


class AdcRpcs(Base):
    RPC_ERROR = RPC_ERROR

    class Config(Base.Config):
        rpcDisable:     RD  =  RC(suffix="RPC_Disable")
        rpcEnable:      RD  =  RC(suffix="RPC_Enable")
        rpcReset:       RD  =  RC(suffix="RPC_Reset")
        rpcInit:        RD  =  RC(suffix="RPC_Init")
        rpcMoveAbs:     RD  =  RC(suffix="RPC_MoveAbs",     arg_parsers=["UaInt16",  float,   float])
        rpcMoveRel:     RD  =  RC(suffix="RPC_MoveRel",     arg_parsers=["UaInt16",  float,   float])
        rpcMoveVel:     RD  =  RC(suffix="RPC_MoveVel",     arg_parsers=["UaInt16",  float])
        rpcMoveAngle:   RD  =  RC(suffix="RPC_MoveAngle",   arg_parsers=[float])
        rpcStartTrack:  RD  =  RC(suffix="RPC_StartTrack",  arg_parsers=[float])
        rpcStopTrack:   RD  =  RC(suffix="RPC_StopTrack")
        rpcStop:        RD  =  RC(suffix="RPC_Stop")
        rpcReset:       RD  =  RC(suffix="RPC_Reset")
        rpcInit:        RD  =  RC(suffix="RPC_Init")
            
        


if __name__ == "__main__":
    AdcRpcs()
    print("OK")



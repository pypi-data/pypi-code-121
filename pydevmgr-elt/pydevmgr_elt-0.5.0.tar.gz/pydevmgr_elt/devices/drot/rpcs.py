from pydevmgr_core import  NodeAlias1, Defaults 
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.devices.motor import Motor
from pydevmgr_elt.devices.drot.stat import MODE
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt
from pydevmgr_ua import Int16

from enum import Enum
Base = Motor.Rpcs

R = Base.Rpc # Base Node
RC = R.Config
RD = Defaults[RC] # this typing var says that it is a Rpc object holding default values 

# RPC_ERROR are iddentical then Motor 

def mode_parser(mode):
    if isinstance(mode, str):
        if mode not in ['SKY', 'ELEV']:
            raise ValueError('tracking mode must be one of SKY or ELEV got %r'%mode)
        mode = getattr(MODE, mode)
    return Int16(mode)


class DrotRpcs(Base):

    class Config(Base.Config):
        rpcMoveAngle : RD = RC(suffix="RPC_MoveAngle", arg_parsers=[float])
        rpcStartTrack: RD = RC(suffix="RPC_StartTrack", arg_parsers=[mode_parser, float])
         
        rpcStopTrack: RD = RC(suffix="RPC_StopTrack")



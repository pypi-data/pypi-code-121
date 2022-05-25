from pydevmgr_core import  NodeAlias1, Defaults, NodeVar, record_class, BaseParser
from pydevmgr_vlt.base import VltDevice
from pydevmgr_vlt.devices._tools import _inc
from pydevmgr_ua import Int32

from enum import Enum
Base = VltDevice.Cfg

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 


class VltioDevCfg(Base):
    class Config(Base.Config):
        pass    
    class Data(Base.Data):
        pass           


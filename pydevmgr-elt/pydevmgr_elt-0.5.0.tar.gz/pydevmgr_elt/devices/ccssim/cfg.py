from pydevmgr_core import  NodeAlias1, Defaults, NodeVar
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt

from enum import Enum
Base = EltDevice.Interface

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 



class CcsSimCfg(Base):
    class Config(Base.Config):
        latitude: ND = NC(suffix="cfg.site.latitude")
        longitude: ND = NC(suffix="cfg.site.longitude")
 
    class Data(Base.Data):
        latitude:  NodeVar[float] =  -0.429833092     
        longitude:  NodeVar[float] = 1.228800386    




from pydevmgr_core import   Defaults, NodeVar
from pydevmgr_elt.base import EltDevice

from enum import Enum

Base = EltDevice.Interface

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 




class DoChannels(Base):
    class Config(Base.Config):
        do1:              ND =   NC(suffix="ctrl.arrDO[0].bValue")
        do2:              ND =   NC(suffix="ctrl.arrDO[1].bValue")
        do3:              ND =   NC(suffix="ctrl.arrDO[2].bValue")
        do4:              ND =   NC(suffix="ctrl.arrDO[3].bValue")  
        do5:               ND =  NC(suffix="ctrl.arrDO[4].bValue")
        do6:               ND =  NC(suffix="ctrl.arrDO[5].bValue")
        do7:               ND =  NC(suffix="ctrl.arrDO[6].bValue")
        do8:               ND =  NC(suffix="ctrl.arrDO[7].bValue")
        do9:               ND =  NC(suffix="ctrl.arrDO[8].bValue")
        do10:              ND =  NC(suffix="ctrl.arrDO[9].bValue")
        do11:              ND =  NC(suffix="ctrl.arrDO[10].bValue")
        do12:              ND =  NC(suffix="ctrl.arrDO[11].bValue")
        do13:              ND =  NC(suffix="ctrl.arrDO[12].bValue")
        do14:              ND =  NC(suffix="ctrl.arrDO[13].bValue")
        do15:              ND =  NC(suffix="ctrl.arrDO[14].bValue")
        do16:              ND =  NC(suffix="ctrl.arrDO[15].bValue")
        used : list = []

    @property
    def used_channels(self):
        return [getattr(self, f'do{i}') for i in self.config.used]
 








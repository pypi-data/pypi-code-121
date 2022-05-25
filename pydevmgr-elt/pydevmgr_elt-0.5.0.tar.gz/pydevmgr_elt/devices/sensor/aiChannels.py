
from pydevmgr_core import  NodeAlias1, Defaults, NodeVar
from pydevmgr_elt.base import EltDevice

from enum import Enum

Base = EltDevice.Interface

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 




    
class AiChannels(Base):
    class Config(Base.Config):
        ai1:               ND =  NC(suffix="stat.arrAI[0].lrValueUser")
        ai2:               ND =  NC(suffix="stat.arrAI[1].lrValueUser")
        ai3:               ND =  NC(suffix="stat.arrAI[2].lrValueUser")
        ai4:               ND =  NC(suffix="stat.arrAI[3].lrValueUser")  
        ai5:               ND =  NC(suffix="stat.arrAI[4].lrValueUser")
        ai6:               ND =  NC(suffix="stat.arrAI[5].lrValueUser")
        ai7:               ND =  NC(suffix="stat.arrAI[6].lrValueUser")
        ai8:               ND =  NC(suffix="stat.arrAI[7].lrValueUser")
        ai9:               ND =  NC(suffix="stat.arrAI[8].lrValueUser")
        ai10:              ND =  NC(suffix="stat.arrAI[9].lrValueUser")
        ai11:              ND =  NC(suffix="stat.arrAI[10].lrValueUser")
        ai12:              ND =  NC(suffix="stat.arrAI[11].lrValueUser")
        ai13:              ND =  NC(suffix="stat.arrAI[12].lrValueUser")
        ai14:              ND =  NC(suffix="stat.arrAI[13].lrValueUser")
        ai15:              ND =  NC(suffix="stat.arrAI[14].lrValueUser")
        ai16:              ND =  NC(suffix="stat.arrAI[15].lrValueUser")
        used : list = []

    @property
    def used_channels(self):
        return [getattr(self, f'ai{i}') for i in self.config.used]


    









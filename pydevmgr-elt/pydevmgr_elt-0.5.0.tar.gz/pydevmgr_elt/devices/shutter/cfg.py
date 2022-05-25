from pydevmgr_core import   Defaults, NodeVar
from pydevmgr_elt.base import EltDevice

Base = EltDevice.Cfg

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 



class ShutterCfg(Base):
    class Config(Base.Config):
        ignore_closed: ND = NC(suffix='cfg.bIgnoreClosed' )
        ignore_fault: ND = NC(suffix='cfg.bIgnoreFault' )
        ignore_open: ND = NC(suffix='cfg.bIgnoreOpen' )
        initial_state: ND = NC(suffix='cfg.bInitialState' )
        low_closed: ND = NC(suffix='cfg.bActiveLowClosed' )
        low_fault: ND = NC(suffix='cfg.bActiveLowFault' )
        low_open: ND = NC(suffix='cfg.bActiveLowOpen' )
        low_switch: ND = NC(suffix='cfg.bActiveLowSwitch' )
        timeout: ND = NC(suffix='cfg.nTimeout', parser='UaUInt32')

    
    class Data(Base.Data):
        ignore_closed: NV[bool] = False
        ignore_fault: NV[bool] = False
        ignore_open: NV[bool] = False
        initial_state: NV[bool] = False
        low_closed: NV[bool] = False
        low_fault: NV[bool] = False
        low_open: NV[bool] = False
        low_switch: NV[bool] = False
        timeout: NV[int] = 3000

           


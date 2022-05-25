from pydevmgr_core import  NodeAlias1, Defaults, NodeVar
from pydevmgr_elt.base import EltDevice,  GROUP
from pydevmgr_elt.base.tools import _inc, enum_group, enum_txt

from enum import Enum
Base = EltDevice.Cfg

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 



class LampCfg(Base):
    class Config(Base.Config):
        analog_range: ND = NC(suffix='cfg.nFullRange', parser='UaUInt32')
        analog_threshold: ND = NC(suffix='cfg.nAnalogThreshold', parser='UaInt32')
        cooldown: ND = NC(suffix='cfg.nCooldown', parser='UaUInt32')
        ignore_fault: ND = NC(suffix='cfg.bIgnoreFault' )
        initial_state: ND = NC(suffix='cfg.bInitialState' )
        invert_analog: ND = NC(suffix='cfg.bInvertAnalog' )
        low_fault: ND = NC(suffix='cfg.bActiveLowFault' )
        low_on: ND = NC(suffix='cfg.bActiveLowOn' )
        low_switch: ND = NC(suffix='cfg.bActiveLowSwitch' )
        maxon: ND = NC(suffix='cfg.nMaxOn', parser='UaUInt32')
        timeout: ND = NC(suffix='cfg.nTimeout', parser='UaUInt32')
        warmup: ND = NC(suffix='cfg.nWarmup', parser='UaUInt32')


    
    class Data(Base.Data):
        analog_range: NV[int] = 0
        analog_threshold: NV[int] = 0
        cooldown: NV[int] = 0
        ignore_fault: NV[bool] = False
        initial_state: NV[bool] = False
        invert_analog: NV[bool] = False
        low_fault: NV[bool] = False
        low_on: NV[bool] = False
        low_switch: NV[bool] = False
        maxon: NV[int] = 0
        timeout: NV[int] = 0
        warmup: NV[int] = 0
              


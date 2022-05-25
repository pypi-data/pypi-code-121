from pydevmgr_vlt.base import VltDevice
from pydevmgr_core import Defaults, NodeVar, NodeAlias, NodeAlias1, record_class, BaseParser
from pydevmgr_ua import Int32, Int16
from enum import Enum 
from typing import Optional 
from pydevmgr_vlt.devices.vltmotor.positions import PositionsConfig
from pydevmgr_vlt.devices._tools import _inc 

Base = VltDevice.Ctrl

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 


class MOTOR_COMMAND(int, Enum):
    NONE = _inc(0)
    INITIALISE = _inc()
    SET_POSITION = _inc()
    MOVE_ABSOLUTE = _inc()
    MOVE_RELATIVE = _inc()
    MOVE_VELOCITY = _inc()
    NEW_VELOCITY = _inc()
    NEW_POSITION = _inc()
    CLEAR_NOVRAM = _inc()

@record_class
class MotorCommand(BaseParser):
    class Config(BaseParser.Config):
        type = "MotorCommand"
    @staticmethod
    def parse(value, config):
        if isinstance(value, str):
            value =  getattr(MOTOR_COMMAND, value)
        return Int32(value)


class DIRECTION(int, Enum):
    POSITIVE = _inc(1)
    SHORTEST = _inc()
    NEGATIVE = _inc()
    CURRENT  = _inc()

@record_class
class Direction(BaseParser):
    class Config(BaseParser.Config):
        type = "Direction"
    @staticmethod
    def parse(value, config):
        if isinstance(value, str):
            value =  getattr(DIRECTION, value)
        return Int16(value)





class VltMotorCtrl(Base):
    COMMAND = MOTOR_COMMAND
    DIRECTION = DIRECTION
    
    class Config(Base.Config):
        command:    ND  =  NC(  suffix=  'ctrl.nCommand',     parser=  MotorCommand  )
        direction:  ND  =  NC(  suffix=  'ctrl.nDirection',   parser=  Direction     )
        position:   ND  =  NC(  suffix=  'ctrl.lrPosition',   parser=  'UaDouble'    )
        velocity:   ND  =  NC(  suffix=  'ctrl.lrVelocity',   parser=  'UaDouble'    )
        stop:       ND  =  NC(  suffix=  'ctrl.bStop',        parser=  bool          )
        reset:      ND  =  NC(  suffix=  'ctrl.bResetError',  parser=  bool          )
        disable:    ND  =  NC(  suffix=  'ctrl.bDisable',     parser=  bool          )
        enable:     ND  =  NC(  suffix=  'ctrl.bEnable',      parser=  bool          )
        execute:    ND  =  NC(  suffix=  'ctrl.bExecute',     parser=  bool          )

    class Data(Base.Data):
        pass # empty for ctr TODO: add data for ctrl ? 
   

if __name__=="__main__":
    VltMotorCtrl()

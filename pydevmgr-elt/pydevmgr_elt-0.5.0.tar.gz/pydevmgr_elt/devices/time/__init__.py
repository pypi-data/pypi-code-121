from pydevmgr_elt.devices.time.stat import TimeStat as Stat, MODE
from pydevmgr_elt.devices.time.cfg  import TimeCfg as Cfg
from pydevmgr_elt.devices.time.rpcs import TimeRpcs as Rpcs

from pydevmgr_elt.base import EltDevice
from pydevmgr_core import record_class
from typing import Optional, Union

import datetime

Base = EltDevice


class TimeCtrlConfig(Base.Config.CtrlConfig):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (on top of CtrlConfig)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    latitude  : Optional[float] = -0.429833092 
    longitude : Optional[float] = 1.228800386
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
class TimeConfig(Base.Config):
    CtrlConfig = TimeCtrlConfig
    
    Cfg = Cfg.Config
    Stat = Stat.Config
    Rpcs = Rpcs.Config
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (redefine the ctrl_config)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    type: str = "Time"
    ctrl_config : CtrlConfig= CtrlConfig()
    
    cfg: Cfg = Cfg()
    stat: Stat = Stat()
    rpcs: Rpcs = Rpcs()
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def isodate(d: Union[str,datetime.datetime]):
    """ parse an input datetime or iso string to a string of fomat '2021-04-26-09:23:54.142136' """
    if isinstance(d, datetime.datetime):
        return  d.isoformat().replace("T", "-") 
    return d.replace("T", "-") 





@record_class
class Time(Base):
    """ ELt Standard Time device """
    Config = TimeConfig
    Cfg = Cfg
    Stat = Stat
    Rpcs = Rpcs
    
    MODE = MODE

    class Data(Base.Data):
        Cfg = Cfg.Data
        Stat = Stat.Data
        Rpcs = Rpcs.Data
        
        cfg: Cfg = Cfg()
        stat: Stat = Stat()
        rpcs: Rpcs = Rpcs()
   
    def reset(self) -> Base.Node:
        raise ValueError('Time has no reset capability')

    def enable(self) -> Base.Node:
        raise ValueError('Time has no enable capability')
        
    def disable(self) -> Base.Node:
        raise ValueError('Time has no disable capability')
    
    def init(self) -> Base.Node:
        raise ValueError('Time has no init capability')
    
    def set_mode(self, mode: int) -> None:
        mode = int(self.MODE(mode)) # this will raise error if mode is incorrect 
        self.rpc.rpcSetMode.rcall(mode)
        
    def set_time(self, time: Union[str,datetime.datetime, None]) -> None:
        """ Set time to PLC. If None time will be datetime.now() 
        
        Before setting time the mode is automaticaly switched to simulation 
        """        
        time = isodate(datetime.datetime.now() if time is None else time)
        self.set_mode(self.MODE.LOCAL) # patch to clear any error 
        self.set_mode(self.MODE.SIMULATION)
        # self.cfg.user_time
        self.rpcs.rpcSetTime.rcall(time)        

if __name__ == "__main__":
    Time()
    print("OK")



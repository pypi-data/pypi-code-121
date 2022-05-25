from pydevmgr_elt.devices.shutter.stat import ShutterStat as Stat
from pydevmgr_elt.devices.shutter.cfg  import ShutterCfg as Cfg
from pydevmgr_elt.devices.shutter.rpcs import ShutterRpcs as Rpcs

from pydevmgr_elt.base import EltDevice
from pydevmgr_core import record_class, Defaults
from typing import Optional


Base = EltDevice


class ShutterCtrlConfig(Base.Config.CtrlConfig):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (on top of CtrlConfig)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    low_closed:    Optional[bool] =  False
    low_fault:     Optional[bool] =  False  # If T, signal is active low
    low_open:      Optional[bool] =  False  # If T, signal is active low
    low_switch:    Optional[bool] =  False  # If T, signal is active low
    ignore_closed: Optional[bool] =  False  # If T, ignore the signal
    ignore_fault:  Optional[bool] =  False  # If T, ignore the signal
    ignore_open:   Optional[bool] =  False  # If T, ignore the signal
    initial_state: Optional[bool] =  False
    timeout:       Optional[int]  =  2000
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
class ShutterConfig(Base.Config):
    CtrlConfig = ShutterCtrlConfig
    
    Cfg = Cfg.Config
    Stat = Stat.Config
    Rpcs = Rpcs.Config
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (redefine the ctrl_config)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    type: str = "Shutter"
    ctrl_config : CtrlConfig= CtrlConfig()
    
    cfg: Defaults[Cfg] = Cfg()
    stat: Defaults[Stat] = Stat()
    rpcs: Defaults[Rpcs] = Rpcs()
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




@record_class
class Shutter(Base):
    """ ELt Standard Shutter device """
    Config = ShutterConfig
    Cfg = Cfg
    Stat = Stat
    Rpcs = Rpcs
    
    class Data(Base.Data):
        Cfg = Cfg.Data
        Stat = Stat.Data
        Rpcs = Rpcs.Data
        
        cfg: Cfg = Cfg()
        stat: Stat = Stat()
        rpcs: Rpcs = Rpcs()
    
    def open(self) -> Base.Node:
        """ open the shutter 
        
        Returns:
            is_open:  the :class:`NodeAlias` .stat.is_open to check if the shutter is open
        
        Example:
        
            ::
            
                wait( shutter.open() )
        """
        self.rpcs.rpcOpen.rcall()    
        return self.stat.is_open 
        
    def close(self) -> Base.Node:
        """ close the shutter 
        
        Returns:
            is_closed:  the :class:`NodeAlias` .stat.is_closed to check if the shutter is closed
        
        Example:
        
            ::
            
                wait( shutter.close() )
        """
        self.rpc.rpcClose.rcall()
        return self.stat.is_closed 
        
    def stop(self):
        """ stop any motion """
        self.rpcs.rpcStop.rcall()
if __name__  == "__main__":
    s = Shutter('s')
    s.stat.is_closed


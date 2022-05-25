from pydevmgr_elt.devices.lamp.stat import LampStat as Stat
from pydevmgr_elt.devices.lamp.cfg  import LampCfg as Cfg
from pydevmgr_elt.devices.lamp.rpcs import LampRpcs as Rpcs

from pydevmgr_elt.base import EltDevice
from pydevmgr_core import record_class
from typing import Optional

Base = EltDevice


class LampCtrlConfig(Base.Config.CtrlConfig):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (on top of CtrlConfig)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    low_fault:        bool = False   # If T, signal is active low
    low_on:           bool = False   # If T, signal is active low
    low_switch:       bool = False   # If T, signal is active low
    initial_state:    bool = False
    timeout:          int  = 2000 

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
class LampConfig(Base.Config):
    CtrlConfig = LampCtrlConfig
    
    Cfg = Cfg.Config
    Stat = Stat.Config
    Rpcs = Rpcs.Config
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (redefine the ctrl_config)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    type: str = "Lamp"
    ctrl_config : CtrlConfig= CtrlConfig()
    
    cfg: Cfg = Cfg()
    stat: Stat = Stat()
    rpcs: Rpcs = Rpcs()
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




@record_class
class Lamp(Base):
    """ ELt Standard Lamp device """
    Config = LampConfig
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
    
    def switch_on(self, intensity, time_limit) -> EltDevice.Node:
 
        """ switch on the lamp 
        
        Args:
            intensity (float): in % 
            time_limit (float): number of second the lamp will stay on
        """       
        # intensity - float, onTimeLimit - integer
        
        self.rpcs.rpcSwitchOn.rcall(intensity, time_limit)

        return self.stat.is_on
         
    def switch_off(self) -> EltDevice.Node:
        """ switch off the lamp """        
        self.rpcs.rpcSwitchOff.rcall()
        return self.stat.is_off
    

if __name__ == "__main__":
    Lamp()

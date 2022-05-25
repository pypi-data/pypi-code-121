from pydevmgr_elt.devices.drot.stat import DrotStat as Stat, MODE
from pydevmgr_elt.devices.drot.cfg  import DrotCfg as Cfg
from pydevmgr_elt.devices.drot.rpcs import DrotRpcs as Rpcs

from pydevmgr_elt.base import EltDevice
from pydevmgr_elt.devices.motor import Motor
from pydevmgr_core import record_class
from pydevmgr_core.nodes import Opposite
from typing import Optional


Base = Motor


class DrotCtrlConfig(Base.Config.CtrlConfig):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (on top of CtrlConfig)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pass
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
class DrotConfig(Base.Config):
    CtrlConfig = DrotCtrlConfig
    
    Cfg = Cfg.Config
    Stat = Stat.Config
    Rpcs = Rpcs.Config
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (redefine the ctrl_config)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    type: str = "Drot"
    ctrl_config : CtrlConfig= CtrlConfig()
    
    cfg: Cfg = Cfg()
    stat: Stat = Stat()
    rpcs: Rpcs = Rpcs()
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




@record_class
class Drot(Base):
    """ ELt Standard Drot device """
    Config = DrotConfig
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
   
    def init(self):
        # fix a feature unsude the FB_MA, the RPC_Init return silently zero even if the
        # device is not in the right state
        # TODO remove the patch when this is fixed from ESO side 
        if self.stat.substate.get() != self.SUBSTATE.NOTOP_NOTREADY:
            raise RuntimeError("Should be in NOTOP_NOTREADY state")
        self.rpcs.rpcInit.rcall()
        return self.stat.is_ready   

    def stop_track(self) -> None:
        self.rpcs.rpcStopTrack.rcall()
        return Opposite(node=self.stat.is_tracking)
    
    def start_track(self, mode, angle=0.0) -> Base.Node:
        """ Start drot tracking 
        
        Args:
            mode (int, str): tracking mode. Int constant defined in Drot.MODE.SKY, Drot.MODE.ELEV
                             str 'SKY' or 'ELEV' is also accepted
            angle (float): paSky or paPupil depending of the mode
        
        Returns:
            is_tracking:  the :class:`NodeAlias` .stat.is_tracking to check if the device is in tracking  
        """
        self.rpcs.rpcStartTrack.rcall(mode, angle)
        return self.stat.is_tracking
    
    def move_angle(self, angle=0.0) -> Base.Node:
        """ Move drot to angle in STAT mode 
        
        Args:
            angle (float, optional): target angle default = 0.0 
            
        Returns:
            is_standstill:  the :class:`NodeAlias` .stat.is_standstill to check if the device is 
                            in standstill. (e.i. movement finished)
        
        Example:
        
            ::
            
                wait( drot.move_angle( 34.3 ) )
        """
        self.rpcs.rpcMoveAngle.rcall(angle)
        return self.stat.is_standstill
    
    # Other functions are in Motor     

if __name__ == "__main__":
    Drot()

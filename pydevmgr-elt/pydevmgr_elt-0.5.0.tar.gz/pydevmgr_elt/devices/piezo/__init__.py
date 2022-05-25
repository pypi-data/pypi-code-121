from .stat import PiezoStat as Stat
from .cfg  import PiezoCfg as Cfg
from .rpcs import PiezoRpcs as Rpcs

from pydevmgr_elt.base import EltDevice
from pydevmgr_core import record_class
from typing import Optional


Base = EltDevice


class PiezoCtrlConfig(Base.Config.CtrlConfig):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (on top of CtrlConfig)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pass # Nothing to declare
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
class PiezoConfig(Base.Config):
    CtrlConfig = PiezoCtrlConfig
    
    Cfg = Cfg.Config
    Stat = Stat.Config
    Rpcs = Rpcs.Config
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (redefine the ctrl_config)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    type: str = "Piezo"
    ctrl_config : CtrlConfig= CtrlConfig()
    
    cfg: Cfg = Cfg()
    stat: Stat = Stat()
    rpcs: Rpcs = Rpcs()
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




@record_class
class Piezo(Base):
    """ ELt Standard Piezo device """
    Config = PiezoConfig
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
    
    def auto(self) -> None:
        """ turn on auto mode 
        
        Returns:
           None
        """
        self.rpcs.rpcAuto.rcall()   
    
    def pos(self):
        """ turn to POS mode 
        
        Returns:
           None
        """
        self.rpcs.rpcPos.rcall()
    
    def home(self) -> None:
        """ send  piezos home 
        
        Returns:
           None
        """
        self.rpcs.rpcHome.rcall()
    
    def move_bits(self, pos1=0, pos2=0, pos3=0) -> None:
        """ move piezos to bits position 
        
        Args:
            pos1 (int): piezo 1 position (bits)
            pos2 (int): piezo 2 position (bits) 
            pos3 (int): piezo 3 position (bits)
        """
        # pos1, pos2, pos3 are piezo set positions in bits - integers.
        self.rpcs.rpcMoveBits.rcall(pos1, pos2, pos3)
    
    def move_user(self, pos1=0.0, pos2=0.0, pos3=0.0) -> None:
        """ move piezos to user  position 
        
        Args:
            pos1 (float): piezo 1 position (user)
            pos2 (float): piezo 2 position (user) 
            pos3 (float): piezo 3 position (user)
        """
        # pos1, pos2, pos3 are piezo set positions in UU - float.
        self.rpcs.rpcMoveUser.rcall(pos1, pos2, pos3)
    
    def stop(self) -> None:
        """ stop movement """
        self.rpcs.rpcStop.rcall()



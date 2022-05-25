from pydevmgr_elt.devices.motor.stat import MotorStat as Stat
from pydevmgr_elt.devices.motor.cfg  import MotorCfg as Cfg
from pydevmgr_elt.devices.motor.rpcs import MotorRpcs as Rpcs
from pydevmgr_elt.devices.motor.init_seq import init_sequence_to_cfg, InitialisationConfig
from pydevmgr_elt.devices.motor.positions import PositionsConfig
from pydevmgr_elt.devices.motor.axis_type import AXIS_TYPE

from pydevmgr_elt.base import EltDevice
from pydevmgr_core import record_class, Defaults
from typing import Any, Optional, Dict, Union
from pydantic import validator
Base = EltDevice




class MotorCtrlConfig(Base.Config.CtrlConfig):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (on top of CtrlConfig)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    velocity : float = 0.1 # mendatory because used as default for movement
    min_pos :           Optional[float] = 0.0
    max_pos :           Optional[float] = 0.0 
    axis_type :         Union[None,int,str] = "LINEAR" # LINEAR , CIRCULAR, CIRCULAR_OPTIMISED
    active_low_lstop :  Optional[bool] = False
    active_low_lhw :    Optional[bool] = False
    active_low_ref :    Optional[bool] = True
    active_low_index :  Optional[bool] = False
    active_low_uhw :    Optional[bool] = True
    active_low_ustop :  Optional[bool] = False
    brake :             Optional[bool] = False
    low_brake :         Optional[bool] = False
    low_inpos :         Optional[bool] = False
    backlash :          Optional[float] = 0.0
    tout_init :         Optional[int] = 30000
    tout_move :         Optional[int] = 12000
    tout_switch :       Optional[int] = 10000 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Validator Functions
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    @validator('axis_type')
    def validate_axis_type(cls, ax):
        if isinstance(ax, str):
            try:
                getattr(AXIS_TYPE, ax)
            except AttributeError:
                raise ValueError(f"Unknown axis_type {ax!r}")
        if isinstance(ax, int):            
            # always return a string??
            ax = AXIS_TYPE(ax).name        
        return ax

    
class MotorConfig(Base.Config):
    CtrlConfig = MotorCtrlConfig
    Positions= PositionsConfig
    Initialisation= InitialisationConfig
   
    Cfg = Cfg.Config
    Stat = Stat.Config
    Rpcs = Rpcs.Config
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (redefine the ctrl_config)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    type: str = "Motor"
    ctrl_config :    CtrlConfig = CtrlConfig()
    initialisation : Initialisation= Initialisation()
    positions      : Positions= Positions()
    
    cfg: Cfg = Cfg()
    stat: Stat = Stat()
    rpcs: Rpcs = Rpcs()
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




@record_class
class Motor(Base):
    """ ELt Standard Motor device """
    Config = MotorConfig
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
    
    def get_configuration(self, exclude_unset=True, **kwargs) -> Dict[Base.Node,Any]:
        """  return a node/value pair dictionary ready to be uploaded 
        
        The node/value dictionary represent the device configuration. 
        
        Args:
            **kwargs : name/value pairs pointing to cfg.name node
                      This allow to change configuration on the fly
                      without changing the config file. 
        """
        
        config = self._config 
        
        ctrl_config = config.ctrl_config
        # just update what is in ctrl_config, this should work for motor 
        # one may need to check parse some variable more carefully       
        values = ctrl_config.dict(exclude_none=True, exclude_unset=exclude_unset)
        cfg_dict = { getattr(self.cfg, k):v for k,v in  values.items() }
        cfg_dict[self.is_ignored] = self.config.ignored 
        cfg_dict.update({ getattr(self.cfg,k):v for k,v in  kwargs.items() })
        
        init_cfg = init_sequence_to_cfg(config.initialisation, self.Cfg.INITSEQ)
        cfg_dict.update({ getattr( self.cfg, k):v for k,v in init_cfg.items()})
        
        # transform axis type to number 
        if self.cfg.axis_type in cfg_dict:
            axis_type = cfg_dict[self.cfg.axis_type] 
            cfg_dict[self.cfg.axis_type] =  getattr(self.Cfg.AXIS_TYPE, axis_type) if isinstance(axis_type, str) else axis_type
        ###
        # Set the new config value to the device 
        return cfg_dict
          
    @property
    def posnames(self) -> str:
        """ configured position names in a name:(pos, tol) dictionary """
        return self.config.positions.posnames      
            
    @property
    def velocity(self) -> float:
        return self.config.ctrl_config.velocity
    
     
    def move_abs(self, absPos, vel=None) -> Base.Node:
        """ move motor to an absolute position 
        
        self.move_abs(pos, vel) <-> self.rpc.rpcMoveAbs(pos, vel)
        
        Args:
            absPos (float): absolute position
            vel (float):   target velocity for the movement
            
        """
        vel = self.velocity if vel is None else vel
        self.rpcs.rpcMoveAbs.rcall(absPos, vel)
        return self.stat.is_standstill
        
    def move_name(self, name, vel=None) -> Base.Node:
        """ move motor to a named position 
        
        Args:
           name (str): named position
           vel (float):   target velocity for the movement
        """
        absPos = self.get_pos_target_of_name(name)
        return self.move_abs(absPos, vel)
        
    def move_rel(self, relPos, vel=None) -> Base.Node:
        """ Move motor relative position
        
        Args:
           relPos (float): relative position
           vel (float):   target velocity for the movement
        """
        vel = self.velocity if vel is None else vel
        self.rpcs.rpcMoveRel.rcall(relPos, vel)
        return self.stat.is_standstill
        
    def move_vel(self, vel) -> None:
        """ Move motor in velocity mode 
        
        Args:
           vel (float): target velocity
        """
        self.rpcs.rpcMoveVel.rcall(vel)

    def stop(self) -> None:
        """ Stop the motor """
        self.rpcs.rpcStop.rcall()
    
    def get_pos_target_of_name(self, name: str) -> float:
        """return the configured target position of a given pos name or raise error"""
        # TODO: Fix the get_pos_target_name so it uses the dict 
        try:
            position = getattr(self.config.positions, name)
        except AttributeError:
            raise ValueError('unknown posname %r'%name)
        return position

    def get_name_of_pos(self, pos_actual: float) -> str:
        """ Retrun the name of a position from a position as input or ''
        
        Example:
            m.get_name_of( m.stat.pos_actual.get() )
        """
        positions = self.config.positions    
        tol = positions.tolerance
        
        for pname, pos in positions.positions.items():
            if abs( pos-pos_actual)<tol:
                return pname
        return ''
        
    def is_near(self, pos: float, tol: float, data: Optional[Dict[str,Any]] =None) -> bool:
        """ -> True when abs(pos_actual-pos)<tol """
        apos = self.stat.pos_actual.get(data) 
        return abs(apos-pos)<tol

if __name__ == "__main__":
    Motor()

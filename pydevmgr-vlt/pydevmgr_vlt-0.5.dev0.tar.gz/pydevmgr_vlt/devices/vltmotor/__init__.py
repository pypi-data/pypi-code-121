from pydevmgr_vlt.devices.vltmotor.stat import VltMotorStat as Stat
from pydevmgr_vlt.devices.vltmotor.cfg import VltMotorCfg as Cfg, AXIS_TYPE
from pydevmgr_vlt.devices.vltmotor.ctrl import VltMotorCtrl as Ctrl
from pydevmgr_vlt.devices.vltmotor.init_seq import INITSEQ, InitialisationConfig, init_sequence_to_cfg
from pydevmgr_vlt.devices.vltmotor.positions import  PositionsConfig


from pydevmgr_vlt.base import VltDevice
from pydevmgr_core import upload 
from typing import Optional , Union , Dict, Any
from pydantic import BaseModel, validator

Base = VltDevice



class VltMotorCtrlConfig(BaseModel):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure 
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
    backlash :          Optional[float] = 0.0
    tout_init :         Optional[int] = 30000
    tout_move :         Optional[int] = 12000
    tout_switch :       Optional[int] = 10000
    
    scale_factor : Optional[float] = 1.0
    accel: Optional[float] = 30.0
    decel: Optional[float] = 30.0
    jerk:  Optional[float] = 100.0
    
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


class VltMotorConfig(Base.Config):
    CtrlConfig = VltMotorCtrlConfig
    Positions = PositionsConfig
    Initialisation = InitialisationConfig
    
    Ctrl = Ctrl.Config
    Stat = Stat.Config 
    Cfg = Cfg.Config

    ctrl : Ctrl = Ctrl()
    stat: Stat = Stat()
    cfg: Cfg = Cfg()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    type: str = "VltMotor"
    initialisation : Initialisation= Initialisation()
    positions      : Positions= Positions()
    ctrl_config    : CtrlConfig = CtrlConfig()



class VltMotor(Base):
    Config = VltMotorConfig
    

    Cfg  = Cfg 
    Stat = Stat
    Ctrl = Ctrl
    
    class Data(Base.Data):
        Stat = Stat.Data
        Cfg = Cfg.Data
        Ctrl = Ctrl.Data
        
        stat: Stat = Stat()
        cfg: Cfg = Cfg()
        ctrl: Ctrl = Ctrl()
        

    def get_configuration(self, exclude_unset=True,  **kwargs) -> Dict[VltDevice.Node,Any]:
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
        cfg_dict = {getattr(self.cfg, k):v for k,v in  values.items() }
        cfg_dict[self.is_ignored] = self.config.ignored 
        cfg_dict.update({getattr(self.cfg, k):v for k,v in  kwargs.items() })
        
        init_cfg = init_sequence_to_cfg(config.initialisation, self.Cfg.INITSEQ)
        cfg_dict.update({getattr( self.cfg, k):v for k,v in init_cfg.items()})
        

        AXIS_TYPE = self.Cfg.AXIS_TYPE
        
        # transform axis type to number 
        if self.cfg.axis_type in cfg_dict:
            axis_type = cfg_dict[self.cfg.axis_type] 
            cfg_dict[self.cfg.axis_type] =  getattr(AXIS_TYPE, axis_type) if isinstance(axis_type, str) else axis_type
        ###
        # Set the new config value to the device 
        return cfg_dict      
    
    @property
    def velocity(self) -> float:
        return self.config.ctrl_config.velocity
   

    def check(self):
        """Check if the device is in error. Raise an error in case it is True """
        return self.stat.check.get()

    def stop(self):
        self.ctrl.stop.set(True)
    
    def reset(self):
        self.ctrl.reset.set(True)
        return self.stat.not_initialised
    
    def enable(self):
        self.ctrl.enable.set(True)
        return self.stat.enable_finished
    
    def disable(self):
        self.ctrl.disable.set(True)
        return self.stat.enabled


    def init(self):
        upload({ 
            self.ctrl.execute : True, 
            self.ctrl.command : self.Ctrl.COMMAND.INITIALISE
            })
        return self.stat.initialisation_finished

    def move_abs(self, pos, vel=None):
        
        vel = self.velocity if vel is None else vel
        upload({
            self.ctrl.execute : True, 
            self.ctrl.position: pos, 
            self.ctrl.velocity: vel, 
            self.ctrl.command : self.Ctrl.COMMAND.MOVE_ABSOLUTE
            })
        return self.stat.movement_finished

    def move_rel(self, pos, vel=None):

        vel = self.velocity if vel is None else vel
        upload({
            self.ctrl.execute : True, 
            self.ctrl.position: pos, 
            self.ctrl.velocity: vel, 
            self.ctrl.command : self.Ctrl.COMMAND.MOVE_RELATIVE
            })
        return self.stat.movement_finished  

    def move_vel(self, vel):
        direction = self.Ctrl.DIRECTION.POSITIVE if vel>0 else self.Ctrl.DIRECTION.NEGATIVE
        vel = abs(vel)
        upload({
            self.ctrl.execute : True, 
            self.ctrl.velocity: vel, 
            self.ctrl.direction: direction, 
            self.ctrl.command: self.Ctrl.COMMAND.MOVE_VELOCITY
            })
        return None
    
    def get_pos_target_of_name(self, name: str) -> float:
        """return the configured target position of a given pos name or raise error"""
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

    def move_name(self, name, vel=None) -> VltDevice.Node:
        """ move motor to a named position 
        
        Args:
           name (str): named position
           vel (float):   target velocity for the movement
        """
        absPos = self.get_pos_target_of_name(name)
        return self.move_abs(absPos, vel)
        

    def set_pos(self, pos):
        """ Set the curent position value """
        upload({
            self.ctrl.execute : True, 
            self.ctrl.position: pos, 
            self.ctrl.command : self.Ctrl.COMMAND.SET_POSITION
            })



if __name__=="__main__":
    VltMotor()
    print("OK")

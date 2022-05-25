from PyQt5 import uic
from PyQt5.QtWidgets import QFrame
from .io import find_ui
from pydevmgr_core import NodeVar

from .elt_device_ctrl import EltDeviceCtrl
from pydevmgr_core_qt import record_widget_factory

from enum import IntEnum


# ################################################
class DrotCtrlStatData(EltDeviceCtrl.Data.StatData):
    track_mode_txt: NodeVar[str] = ""     
    pos_actual: NodeVar[float] = 0.0 
    pos_error: NodeVar[float] = 0.0       
    pos_target: NodeVar[float] = 0.0   
    vel_actual: NodeVar[float] = 0.0  
    angle_on_sky: NodeVar[float] = 0.0


class DrotCtrlData(EltDeviceCtrl.Data):
    StatData = DrotCtrlStatData    
    stat: StatData = StatData()

# ################################################

class MOVE_MODE(IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    VELOCITY = 2

class TRACK_MODE(IntEnum):
    SKY = 2
    ELEV = 3
    USER = 4

# ################################################
class DrotCtrlUi(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(find_ui('drot_ctrl_frame.ui'), self)


        
class DrotCtrl(EltDeviceCtrl):
    Data =  DrotCtrlData
    Widget = DrotCtrlUi
                   
    def init_vars(self):
        super().init_vars()
        w = self.widget
        self.outputs.pos_actual = self.outputs.Float(w.pos_actual, fmt="%.3f")
        self.outputs.pos_error  = self.outputs.Float(w.pos_error,  fmt="%.3E")
        self.outputs.pos_target = self.outputs.Float(w.pos_target, fmt="%.3f")
        self.outputs.vel_actual = self.outputs.Float(w.vel_actual, fmt="%.3f")
        self.outputs.angle_on_sky = self.outputs.Float(w.angle_on_sky, fmt="%.3f")
        
        self.outputs.track_mode = self.outputs.Str(w.track_mode_txt)
                
        self.inputs.pos_target = self.inputs.Float(w.input_pos_target, default=0.0)
        self.inputs.velocity = self.inputs.Float(w.input_velocity, default=1.0)
        self.inputs.angle = self.inputs.Float(w.input_angle, default=0.0)
        self.inputs.move_mode = self.inputs.Enum(MOVE_MODE, w.move_mode)
        self.inputs.track_mode = self.inputs.Enum(TRACK_MODE, w.track_mode)
                
    def update(self, data):
        super().update(data)
        
        stat = data.stat 
        
        if self.inputs.move_mode.get() == MOVE_MODE.VELOCITY: # VELOCITY
            self.widget.input_pos_target.setEnabled(False)
        else:
            self.widget.input_pos_target.setEnabled(True)
        
        self.outputs.pos_actual.set(stat.pos_actual)
        self.outputs.pos_error.set(stat.pos_error)
        self.outputs.pos_target.set(stat.pos_target)
        self.outputs.vel_actual.set(stat.vel_actual)
        self.outputs.angle_on_sky.set(stat.angle_on_sky)
        self.outputs.track_mode.set(stat.track_mode_txt)
                
    def setup_ui(self,  drot, data):        
        super().setup_ui(drot, data)
        # init some field to what the state is 
        if drot.is_connected():
            self.inputs.velocity.set_input(drot.cfg.velocity.get())        
                
        
        self.actions.add(
                         drot.stop, 
                         [], feedback=self.feedback
                        ).connect_button(self.widget.stop)
                
        self.actions.add(
                         drot.move_angle, 
                         [ self.inputs.angle.get], 
                         feedback=self.feedback
                        ).connect_button(self.widget.move_angle)
                        
        self.actions.add(
                         drot.start_track,
                         [self.inputs.track_mode.get, self.inputs.angle.get], 
                         feedback=self.feedback
                        ).connect_button(self.widget.start_track)                                     
                    
        self.actions.add(
                          drot.stop_track,                          
                          feedback=self.feedback
                         ).connect_button(self.widget.stop_track)                                      

                
        def move(mode,  pos, vel):
            if mode == MOVE_MODE.ABSOLUTE:
                drot.move_abs( pos, vel)
            elif mode == MOVE_MODE.RELATIVE:
                drot.move_rel( pos, vel)
            elif mode == MOVE_MODE.VELOCITY:
                drot.move_vel( vel)
                
        self.actions.add(
                          move, 
                          [self.inputs.move_mode.get, self.inputs.pos_target.get, self.inputs.velocity.get], 
                          feedback=self.feedback
                        ).connect_button(self.widget.move)         

record_widget_factory("ctrl", "Drot", DrotCtrl)
    
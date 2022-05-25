from PyQt5 import  uic
from PyQt5.QtWidgets import QFrame
from .io import find_ui
from pydevmgr_core import NodeVar
from .elt_device_ctrl import EltDeviceCtrl

from pydevmgr_core_qt import record_widget_factory
from enum import IntEnum

# ################################################
#
#  DATA STRUCTURE 
# 
 # ################################################

class AdcCtrStatData(EltDeviceCtrl.Data.StatData):
    track_mode_txt : NodeVar[str] = ""

class MotorCtrStatData(EltDeviceCtrl.Data.StatData):
    pos_actual: NodeVar[float] = 0.0
    pos_error:  NodeVar[float] = 0.0
    pos_target: NodeVar[float] = 0.0
    vel_actual: NodeVar[float] = 0.0

class MotorCtrData(EltDeviceCtrl.Data):
    StatData =  MotorCtrStatData               
    stat: StatData = StatData()  

class AdcCtrlData(EltDeviceCtrl.Data):
    StatData = AdcCtrStatData
    MotorData = MotorCtrData
    
    stat: StatData = StatData()
    motor1: MotorData = MotorData()
    motor2: MotorData = MotorData()


class MOVE_MODE(IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    VELOCITY = 2
    
class AXES(IntEnum):
    BOTH = 0
    AXIS1 = 1
    AXIS2 = 2


class AdcCtrlUi(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(find_ui('adc_ctrl_frame.ui'), self)

class AdcCtrl(EltDeviceCtrl):
    Data = AdcCtrlData
    Widget = AdcCtrlUi    
      
    def init_vars(self):
        super().init_vars()
        w = self.widget 
        
        self.outputs.motor1_pos_actual = self.outputs.Float(w.motor1_pos_actual, fmt="%.3f")
        self.outputs.motor1_pos_error  = self.outputs.Float(w.motor1_pos_error, fmt="%.3E")
        self.outputs.motor1_pos_target = self.outputs.Float(w.motor1_pos_target, fmt="%.3f")
        self.outputs.motor1_vel_actual = self.outputs.Float(w.motor1_vel_actual, fmt="%.3f")
        
        self.outputs.motor2_pos_actual = self.outputs.Float(w.motor2_pos_actual, fmt="%.3f")
        self.outputs.motor2_pos_error  = self.outputs.Float(w.motor2_pos_error, fmt="%.3E")
        self.outputs.motor2_pos_target = self.outputs.Float(w.motor2_pos_target, fmt="%.3f")
        self.outputs.motor2_vel_actual = self.outputs.Float(w.motor2_vel_actual, fmt="%.3f")
        
        self.outputs.track_mode = self.outputs.Str(w.track_mode_txt)
        
        self.inputs.pos_target = self.inputs.Float(w.input_pos_target, default=0.0)
        self.inputs.velocity = self.inputs.Float(w.input_velocity, default=1.0)
        self.inputs.angle = self.inputs.Float(w.input_angle, default=0.0)
        self.inputs.move_mode = self.inputs.Enum(MOVE_MODE, w.move_mode)
        self.inputs.axis = self.inputs.Enum(AXES, w.input_axis)
        self.inputs.mode = self.inputs.Enum(MOVE_MODE, w.move_mode)
        
    def update(self, data):
        super().update(data)
        
        # disable the input_pos_target if in VELOCITY MODE          
        if self.inputs.move_mode.get() == MOVE_MODE.VELOCITY: #MODEVELOCITY
            self.widget.input_pos_target.setEnabled(False)
        else:
            self.widget.input_pos_target.setEnabled(True)
        
        m1 = data.motor1.stat 
        m2 = data.motor2.stat 
        
        self.outputs.motor1_pos_actual.set(  m1.pos_actual) 
        self.outputs.motor1_pos_error.set(   m1.pos_error )  
        self.outputs.motor1_pos_target.set(  m1.pos_target) 
        self.outputs.motor1_vel_actual.set(  m1.vel_actual) 
        
        self.outputs.motor2_pos_actual.set(  m2.pos_actual) 
        self.outputs.motor2_pos_error.set(   m2.pos_error )  
        self.outputs.motor2_pos_target.set(  m2.pos_target) 
        self.outputs.motor2_vel_actual.set(  m2.vel_actual) 
            
        self.outputs.track_mode.set(data.stat.track_mode_txt)
    
        
    def setup_ui(self, adc, data):
        super().setup_ui(adc, data)
        
        # init some field 
        if adc.is_connected():
            self.inputs.velocity.set_input(adc.motor1.cfg.velocity.get())                        
        
        self.actions.add(
                        adc.stop, feedback=self.feedback
                        ).connect_button(self.widget.stop)
                                
        self.actions.add(
                         adc.start_track, 
                         [self.inputs.angle.get], 
                         feedback=self.feedback
                        ).connect_button(self.widget.start_track)
        
                
        self.actions.add(
                    adc.stop_track, [], feedback=self.feedback
                  ).connect_button(self.widget.stop_track)
                        
        def move(mode, axis, pos, vel):
            if mode == MOVE_MODE.ABSOLUTE:
                adc.move_abs(axis, pos, vel)
            elif mode == MOVE_MODE.RELATIVE:
                adc.move_rel(axis, pos, vel)
            elif mode == MOVE_MODE.VELOCITY:
                adc.move_vel(axis, vel)
        self.actions.add(
                          move, 
                          [self.inputs.mode.get, self.inputs.axis.get,  
                          self.inputs.pos_target.get, self.inputs.velocity.get],
                          feedback = self.feedback
                        ).connect_button(self.widget.move)
        
        self.actions.add(
                         adc.move_angle, 
                         [self.inputs.angle.get], 
                         feedback=self.feedback
                        ).connect_button(self.widget.move_angle)        
        
record_widget_factory("ctrl", "Adc", AdcCtrl)

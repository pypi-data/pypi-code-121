from PyQt5 import uic
from PyQt5.QtWidgets import QFrame
from .io import find_ui
from pydevmgr_core import NodeVar
from .elt_device_ctrl import EltDeviceCtrl
from pydevmgr_core_qt import record_widget_factory


# ################################################
class LampCtrlStatData(EltDeviceCtrl.Data.StatData):
    time_left: NodeVar[float] = 0.0
    intensity: NodeVar[float] = 0.0

class LampCtrlData(EltDeviceCtrl.Data):
    StatData = LampCtrlStatData
    stat: StatData = StatData()
# ################################################


class LampCtrlUi(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(find_ui('lamp_ctrl_frame.ui'), self)    

class LampCtrl(EltDeviceCtrl):
    Widget =  LampCtrlUi
    Data =  LampCtrlData  
    
    def init_vars(self):
        super().init_vars()
        
        self.outputs.time_left = self.outputs.Float( self.widget.time_left, fmt="%.0f")        
        self.outputs.intensity = self.outputs.Float( self.widget.intensity, fmt="%.1f")
        
        self.inputs.intensity = self.inputs.Float(self.widget.input_intensity, default=1.0)
        self.inputs.time = self.inputs.Int(self.widget.input_time, default=10.0)
        
    def update(self, data):
        super().update(data)
                        
        stat = data.stat
        self.outputs.time_left.set( stat.time_left )
        self.outputs.intensity.set( stat.intensity )        
        
    def setup_ui(self, lamp, data):                
        super().setup_ui(lamp, data)
                
        self.actions.add(
             lamp.switch_on, 
             [self.inputs.intensity.get, self.inputs.time.get], 
             feedback=self.feedback
            ).connect_button(self.widget.on)
        
        self.actions.add(
             lamp.switch_off, 
             feedback=self.feedback
            ).connect_button(self.widget.off)        


record_widget_factory("ctrl", "Lamp", LampCtrl)

from PyQt5 import uic
from PyQt5.QtWidgets import QFrame
from .io import find_ui
from pydevmgr_elt import NodeVar

from .elt_device_line import EltDeviceLine
from pydevmgr_core_qt import record_widget_factory


# ################################################
class LampLineStatData(EltDeviceLine.Data.StatData):
    time_left: NodeVar[float] = 0.0
    intensity: NodeVar[float] = 0.0

class LampLineData(EltDeviceLine.Data):
    StatData = LampLineStatData
    
    stat: StatData = StatData()

# ################################################

class LampLineUi(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(find_ui('lamp_line_frame.ui'), self)


class LampLine(EltDeviceLine):    
    Widget = LampLineUi
    Data = LampLineData
    
    def init_vars(self):
        super().init_vars()
        
        self.outputs.time_left = self.outputs.Float( self.widget.time_left, fmt="%.0f")   
        
        self.inputs.intensity = self.inputs.Float(self.widget.input_intensity, default=1.0, fmt="%.1f")
        self.inputs.time = self.inputs.Float(self.widget.input_time, default=10.0, fmt="%.1f")
    
    def update(self, data):
        super().update(data)        
        self.outputs.time_left.set( data.stat.time_left )
        
    
    def list_actions(self, lamp):
        return super().list_actions(lamp)+[
        ("ON",  lamp.switch_on, [self.input_intensity.text, self.input_time.text]),
        ("OFF", lamp.switch_off, [])
        ]
        
    def setup_ui(self,lamp, data):
        """ Link a device to the widget 
        
        downloader (:class:`pydevmgr.Downloader`): a Downloader object 
        lamp (:class:`pydevmgr.Lamp`):  Lamp device
        altname (string, optional): Alternative printed name for the device
        """
        ## disconnect all the button if they where already connected
        super().setup_ui(lamp, data)                
        # put some start values, a pity that there is no way to get the last 
        # entered value
        wa = self.widget.state_action
        reset = lambda : wa.setCurrentIndex(0)
        wa.insertSeparator(wa.count())
        
        wa.addItem("ON")
        self.actions.add( lamp.switch_on,
                         [self.inputs.intensity.get, self.inputs.time.get], 
                         after=reset,
                         feedback=self.feedback
                         ).connect_item(wa, wa.count()-1)
                         
        wa.addItem("OFF")
        self.actions.add( lamp.switch_off, 
                          [ ],                        
                         after=reset, 
                         feedback=self.feedback
                       ).connect_item(wa, wa.count()-1)
                  
record_widget_factory("line", "Lamp", LampLine)        
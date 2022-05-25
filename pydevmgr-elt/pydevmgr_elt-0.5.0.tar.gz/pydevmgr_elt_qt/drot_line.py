from PyQt5 import uic
from PyQt5.QtWidgets import QFrame
from .io import find_ui
from pydevmgr_core import NodeVar

from .elt_device_line import EltDeviceLine
from pydevmgr_core_qt import record_widget_factory
from enum import IntEnum

# ################################################
class DrotLineStatData(EltDeviceLine.Data.StatData):    
    track_mode_txt: NodeVar[str] = ""     
    pos_actual: NodeVar[float] = 0.0 
    angle_on_sky: NodeVar[float] = 0.0
    
class DrotLineData(EltDeviceLine.Data):
    StatData = DrotLineStatData
    
    stat: StatData = StatData()
# ################################################

class TRACK_MODE(IntEnum):
    SKY = 2
    ELEV = 3
    USER = 4

# ################################################



class DrotLineUi(QFrame): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(find_ui('drot_line_frame.ui'), self)
        
        
class DrotLine(EltDeviceLine):  
    Data = DrotLineData
    Widget = DrotLineUi
    
    def init_vars(self):
        super().init_vars()
        w = self.widget
        
        self.outputs.pos_actual = self.outputs.Float(w.pos_actual, fmt="%.3f")
        self.outputs.angle_on_sky = self.outputs.Float(w.angle_on_sky, fmt="%.3f")
        self.outputs.track_mode = self.outputs.Str(w.track_mode_txt)
        
        self.inputs.angle = self.inputs.Float(w.input_angle, default=0.0)
          
    def update(self, data):
        super().update(data)
        stat = data.stat
        
        self.outputs.pos_actual.set(stat.pos_actual)
        self.outputs.angle_on_sky.set(stat.angle_on_sky)
        self.outputs.track_mode.set(stat.track_mode_txt) 
    
    def setup_ui(self,  drot, data):
        """ Link a device to the widget 
        
        downloader (:class:`pydevmgr.Downloader`): a Downloader object 
        drot (:class:`pydevmgr.Drot`):  Drot device
        altname (string, optional): Alternative printed name for the device
        """
        ## disconnect all the button if they where already connected
        super().setup_ui(drot, data)
        wa = self.widget.state_action
        
        wa.insertSeparator(wa.count())
        reset = lambda : wa.setCurrentIndex(0)
        
        wa.addItem("MOVE ANGLE")
        self.actions.add( 
                          drot.move_angle,
                          [self.inputs.angle.get], 
                          after=reset
                         ).connect_item(wa, wa.count()-1)
        
        wa.addItem("TRK ELEV")
        self.actions.add( 
                          drot.start_track,
                          [TRACK_MODE.ELEV, self.inputs.angle.get], 
                          after=reset
                         ).connect_item(wa, wa.count()-1)
                         
        wa.addItem("TRK SKY")
        self.actions.add( 
                          drot.start_track,
                          [TRACK_MODE.SKY, self.inputs.angle.get], 
                          after=reset
                         ).connect_item(wa, wa.count()-1)
                         
        wa.addItem("TRK USER")
        self.actions.add( 
                          drot.start_track,
                          [TRACK_MODE.USER, self.inputs.angle.get], 
                          after=reset
                         ).connect_item(wa, wa.count()-1)
                         
        wa.addItem("STOP TRK")
        self.actions.add( 
                          drot.stop_track,                        
                          after=reset
                        ).connect_item(wa, wa.count()-1)
        
record_widget_factory("line", "Drot", DrotLine)


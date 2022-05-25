from pydantic import BaseModel
from pydevmgr_elt import NodeVar, Time

from PyQt5 import uic
from PyQt5.QtWidgets import QFrame
from pydevmgr_core_qt import record_widget_factory, BaseUiLinker

from .io import find_ui
import datetime 


def now():
    return datetime.datetime.utcnow().isoformat().replace("T", "-") 


class TimeStatData(BaseModel):
        
    time: NodeVar[str] = ""
    mode_txt: NodeVar[str] = ""
    error_msg: NodeVar[str] = ""
    
    
class TimeData(BaseModel):
    StatData = TimeStatData # save StatData class here 
    
    stat: StatData = StatData()    
    name: str = "Time" 
    
        
class TimeCtrlUi(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(find_ui('time_ctrl_frame.ui'), self)
        
class TimeCtrl(BaseUiLinker):
    Widget = TimeCtrlUi
    Data = TimeData
    
    def init_vars(self):
        # these shall get stat data
        self.outputs.time = self.outputs.Str(self.widget.time)
        self.outputs.mode    = self.outputs.Str(self.widget.mode)
        self.outputs.rpc_feedback = self.outputs.Feedback(self.widget.rpc_feedback)
        self.outputs.error    = self.outputs.Str(self.widget.error)
        
        self.inputs.time = self.inputs.Str(self.widget.in_time)
            
    def feedback(self, er, msg=''):
        self.outputs.rpc_feedback.set((er, msg))              
    
    def update(self, data : TimeData) -> None:
        """ update the ui from the data structure """
        super().update(data)
        stat = data.stat
                                        
        #self.outputs.dc_time.set( stat.dc_time  )
         
        self.outputs.time.set( stat.time ) 
        self.outputs.mode.set(  stat.mode_txt )
        self.outputs.error.set( stat.error_msg)
        
        
    def setup_ui(self, device, data):   
        super().setup_ui(device, data)
                                    
        #self.outputs.name.set(data.name or device.key)
        
        
        def now():
            self.widget.in_time.repaint()
            return datetime.datetime.utcnow().isoformat().replace("T", "-") 
            
        def simulate(time):
            #self.set_mode(device.MODE.LOCAL) # to Clear any error ! 
            self.outputs.error.set("") # because this is not cleared on the PLC side 
            self.widget.error.repaint()
            device.set_time(time)
            
        
        self.actions.add(
               simulate,
               [self.inputs.time.get], feedback=self.feedback
               ).connect_button(self.widget.set_simulate)
        self.actions.add(
               device.set_mode,
               [Time.MODE.LOCAL], feedback=self.feedback
               ).connect_button(self.widget.set_local_mode)
        self.actions.add(
               device.set_mode,
               [Time.MODE.UTC], feedback=self.feedback
               ).connect_button(self.widget.set_utc_mode)
        self.actions.add(
                self.inputs.time.set_input, 
                [now], feedback=self.feedback
               ).connect_button(self.widget.set_now)
        
record_widget_factory("ctrl", "Time", TimeCtrl)

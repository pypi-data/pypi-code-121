from pydantic import BaseModel
from pydevmgr_elt import NodeVar, EltDevice

from PyQt5 import uic
from PyQt5.QtWidgets import QFrame
from pydevmgr_core_qt import BaseUiLinker, record_widget_factory
from .io import find_ui

class EltDeviceStatData(BaseModel):
    substate: NodeVar[int] = 0
    substate_txt: NodeVar[str] = ""
    substate_group: NodeVar[int] = "" 

class EltDeviceData(BaseModel):
    StatData = EltDeviceStatData
    
    stat: StatData = StatData()
    is_ignored: NodeVar[bool] = False
    name: str = "" # device name  

class EltDeviceLineUi(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(find_ui('device_line_frame.ui'), self) 

class EltDeviceLine(BaseUiLinker):  
    Widget = EltDeviceLineUi
    Data = EltDeviceData
    def init_vars(self):        
        # these shall get stat data        
        self.outputs.substate = self.outputs.Code(self.widget.substate)
        self.outputs.name = self.outputs.Str(self.widget.name)
        
        self.inputs.ignored = self.inputs.NBool(self.widget.check)
        
    def feedback(self, er, mgs: str=''):     
           
        if er:
            self.widget.state_action.setItemText(0, "!!ERROR!!")
        else:
            self.widget.state_action.setItemText(0, "")    
        
    def update(self, data: EltDeviceData):        
        
        stat = data.stat 
        self.outputs.substate.set( (stat.substate, stat.substate_txt, stat.substate_group) )
        
        if self.inputs.ignored.get() != data.is_ignored:
            self.inputs.ignored.set_input(data.is_ignored)
    
    def setup_ui(self, device: EltDevice, data: EltDeviceData): 
        super().setup_ui(device, data)
        
        # The device name is updated here only 
        self.outputs.name.set( data.name or device.key )
        
        # setup the dorpdown menu list for action     
        wa = self.widget.state_action 
        wa.clear() 
        wa.addItem("") # First item is empty and is always activated after an action 
        action_list = [
         ("INIT",   device.init,   []), 
         ("ENABLE", device.enable, []),
         ("DISABLE",device.disable,[]),
         ("RESET",  device.reset,  []) 
        ]
        # After an command put back the menu to the empty first index
        reset = lambda: wa.setCurrentIndex(0) 
                        
        for i, (name,func,inputs) in  enumerate(action_list, start=wa.count()):
            wa.addItem(name)
            action = self.actions.add(func, inputs, after=reset, feedback=self.feedback)
            action.connect_item(wa, i)
        
                
        w = self.widget.check
        w.setChecked(not device.is_ignored.get())        
                
        self.actions.add(device.is_ignored.set, [self.inputs.ignored.get], feedback=self.feedback).connect_checkbox(w)
        
record_widget_factory("line", "Elt", EltDeviceLine)  

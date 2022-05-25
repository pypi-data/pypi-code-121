from pydevmgr_core import NodeVar, BaseData
from pydevmgr_core_qt import find_ui, BaseUiLinker, get_style, record_widget_factory, Outputs
from pydantic import BaseModel
from .io import find_ui 

from PyQt5 import uic
from PyQt5.QtWidgets import QFrame



class CodeVal_O(Outputs.Base):
    """ widget output for a trio of (code, txt, group) 
    
    e.g. for a substate we get the substate code, its text representation and the group which will 
          be used to color the label. Note that group is a pydevmgr thing only.
    """
    def __init__(self, output, fmt="%s: %s"):
        if isinstance(fmt, str):
            fmt = lambda x,y, fmt=fmt: fmt%(x,y)
        
        if hasattr(output, "setText") and hasattr(output, "setStyleSheet") :                            
            def set_output(ctg): # code, text, group 
                c,t,g = ctg
                output.setText(fmt(c,t))
                output.setStyleSheet(get_style(g))                       
        else:
            raise ValueError("Invalid input output combination")            
        super().__init__(set_output)
Outputs.Code = CodeVal_O 


class EltDeviceStatData(BaseModel):
    state: NodeVar[int] = 0
    state_txt: NodeVar[str] =  ""
    state_group: NodeVar[int] = 0
    
    substate: NodeVar[int] = 0
    substate_txt: NodeVar[str] = ""
    substate_group: NodeVar[int] = "" 
    
    error_code: NodeVar[int] = 0
    error_txt: NodeVar[str] = ""
    error_group: NodeVar[int] = 0
    
class EltDeviceData(BaseData):
    StatData = EltDeviceStatData # save StatData class here 
    
    stat: StatData = StatData()
    is_ignored: NodeVar[bool] = False
    name: str = "" # device name  
                
class EltDeviceCtrlUi(QFrame):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(find_ui('device_ctrl_frame.ui'), self) 

    
class EltDeviceCtrl(BaseUiLinker):
    Widget = EltDeviceCtrlUi
    Data = EltDeviceData
    class Config(BaseUiLinker.Config):
        show_ignore_check_box: bool = True
    
    def init_vars(self):
        # these shall get stat data
        self.outputs.state    = self.outputs.Code(self.widget.state )
        self.outputs.substate = self.outputs.Code(self.widget.substate )
        self.outputs.error    = self.outputs.Code(self.widget.error_txt )
                
        self.outputs.name =  self.outputs.Str(self.widget.name)
        
        self.outputs.rpc_feedback = self.outputs.Feedback(self.widget.rpc_feedback)
        self.inputs.ignored = self.inputs.NBool(self.widget.check)
                    
    def feedback(self, er, msg=''):
        self.outputs.rpc_feedback.set((er, msg))       
        
    def update(self, data : EltDeviceData) -> None:
        """ update the ui from the data structure """
        stat = data.stat
                                
        self.outputs.state.set( (stat.state, stat.state_txt, stat.state_group) )
        self.outputs.substate.set( (stat.substate, stat.substate_txt, stat.substate_group) ) 
        self.outputs.error.set( (stat.error_code, stat.error_txt, stat.error_group) )
        
        if self.config.show_ignore_check_box:
            if self.inputs.ignored.get() != data.is_ignored:             
                self.inputs.ignored.set_input(data.is_ignored)    
                
        
    def setup_ui(self, device, data):   
        super().setup_ui(device, data)
                                    
        self.outputs.name.set(data.name or device.key)
        
                
        self.setup_actions(device, data)
        if self.config.show_ignore_check_box:
            self.setup_ignore_checkbox(device,data)
        else:
            self.widget.check.hide()
            
    def setup_ignore_checkbox(self, device, data):
        w = self.widget.check
        w.setChecked(not device.is_ignored.get())                
        self.actions.add(device.is_ignored.set, [self.inputs.ignored.get]).connect_checkbox(w)
    
    def setup_actions(self, device, data):
        wa = self.widget.state_action
        wa.clear()
        wa.addItem("")
        
        action_list = [
         ("INIT",   device.init,   []), 
         ("ENABLE", device.enable, []),
         ("DISABLE",device.disable,[]),
         ("RESET",  device.reset,  []) 
        ]
        reset = lambda: wa.setCurrentIndex(0)
        
        for i, (name,func,inputs) in  enumerate(action_list, start=wa.count()):
            wa.addItem(name)
            action = self.actions.add(func, inputs, after=reset, feedback=self.feedback)
            action.connect_item(wa, i)
        
record_widget_factory("ctrl", "Elt", EltDeviceCtrl)

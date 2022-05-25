from PyQt5 import  uic
from PyQt5.QtWidgets import QFrame
from .io import find_ui
from .elt_device_ctrl import EltDeviceCtrl
from pydevmgr_core_qt import record_widget_factory



class ShutterCtrlUi(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(find_ui('shutter_ctrl_frame.ui'), self)

class ShutterCtrl(EltDeviceCtrl):
    Widget = ShutterCtrlUi                  
    
    def setup_ui(self, shutter, data):        
        super().setup_ui(shutter, data)
                
        # link the buttons to an action
        self.actions.add(shutter.open, feedback=self.feedback).connect_button(self.widget.open)
        self.actions.add(shutter.close, feedback=self.feedback).connect_button(self.widget.close)        

record_widget_factory("ctrl", "Shutter", ShutterCtrl)
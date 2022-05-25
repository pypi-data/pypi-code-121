from PyQt5 import  uic
from PyQt5.QtWidgets import QFrame

from .io import find_ui
from .elt_device_line import  EltDeviceLine
from pydevmgr_core_qt import record_widget_factory



class ShutterLineUi(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(find_ui('shutter_line_frame.ui'), self)

class ShutterLine(EltDeviceLine):
    Widget = ShutterLineUi
    
    def setup_ui(self, shutter, data):        
        super().setup_ui(shutter, data)
        wa = self.widget.state_action
        # After an command put back the menu to the empty first index
        reset = lambda : wa.setCurrentIndex(0)
        wa.insertSeparator(wa.count())
        
        wa.addItem("OPEN")
        self.actions.add( shutter.open, 
                         after=reset, feedback=self.feedback,
                         ).connect_item(wa, wa.count()-1)
        
        wa.addItem("CLOSE")
        self.actions.add( shutter.close, 
                         after=reset, feedback=self.feedback,
                         ).connect_item(wa, wa.count()-1)
                         
record_widget_factory("line", "Shutter", ShutterLine)
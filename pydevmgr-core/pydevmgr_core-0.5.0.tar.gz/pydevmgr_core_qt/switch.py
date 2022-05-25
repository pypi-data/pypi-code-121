from PyQt5 import  uic
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QComboBox, QWidget
from .base import get_widget_types, BaseUiLinker, get_widget_factory, DEFAULT, LayoutLinker
from pydantic import BaseModel
from typing import Optional, List
from pydevmgr_core import BaseDevice
from .io import find_ui


class SwitchUi(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(find_ui('switch.ui'), self)
        
class SwitchLinker(BaseUiLinker):
    Widget = SwitchUi
    class Config(BaseUiLinker.Config):
        default_widget_type: str = ""
        widget_type_list: Optional[List[str]] = None 


    _linker = None
    layout_linker = None
    
    class Data(BaseModel):
        curent_widget_type:  str = ""
               
    def update(self, data):
        pass
    
    def connect(self, downloader, obj, data = None):
        #if data is None:
        #    data = self.Data()
        self.layout_linker = LayoutLinker(self.widget.device_layout)
        self.layout_linker.connect(downloader)
        #self.setup_ui(obj, data)
        super().connect(downloader, obj, data)
            
    def setup_ui(self, device, data):
        if self.config.widget_type_list is None:
            self.config.widget_type_list =  get_widget_types(device.config.type)
        if not self.config.widget_type_list:
            raise ValueError(f"No Widget found for device of type {device.config.type}")
        if not self.config.default_widget_type:
            self.config.default_widget_type = self.config.widget_type_list[0]
                
        self.widget.style_switch.clear()    
        for wtype in self.config.widget_type_list:
            self.widget.style_switch.addItem(wtype)
        self.widget.style_switch.setCurrentIndex(0)
        
        
        def on_switch_changed(wt):
            # clear the layout
            self.layout_linker.clear()
            self.layout_linker.add_device(device, wt)
            data.curent_widget_type = wt
            
        
        self.actions.add(
            on_switch_changed, 
            [self.widget.style_switch.currentText], 
        ).connect_combo(self.widget.style_switch)
        
        # load with the first widget on the list or default 
        if self.config.default_widget_type and self.config.default_widget_type in self.config.widget_type_list:        
            on_switch_changed(self.config.default_widget_type)
        else:
            on_switch_changed(self.config.widget_type_list[0])
        
            
            
                

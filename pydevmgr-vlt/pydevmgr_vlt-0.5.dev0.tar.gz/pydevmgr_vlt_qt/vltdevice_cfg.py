from pydantic import BaseModel
from PyQt5.QtWidgets import QFrame
from pydevmgr_core_qt import BaseUiLinker, record_widget_factory

        
        
class EltDeviceCfgUi(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # What else ? 
    
        
class EltDeviceData(BaseModel):
    name: str = "" # device name  
            
# place holder for some base setup for config pannels 
# not sure we have any             
class EltDeviceCfg(BaseUiLinker):
    Widget = EltDeviceCfgUi
    Data = EltDeviceData
            
record_widget_factory("cfg", "Elt", EltDeviceCfg) 


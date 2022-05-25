from .base import BaseUiLinker, WidgetControl, WidgetFactory, get_widget_factory
from pydantic import BaseModel, validator
from typing import Iterable, Union, Optional, List, Dict
from .io import find_ui
from pydevmgr_core import _BaseObject, BaseData, BaseDevice



from PyQt5.QtWidgets import QLayout, QBoxLayout, QGridLayout, QVBoxLayout, QWidget, QFrame
from PyQt5 import QtCore
from PyQt5.uic import loadUi
import glob



class ConfigViewSetup(BaseModel):
    """ configuration of one view setup 

    Args:
        layout (str) : name of the layout in the ui used to publish widget (default is 'ly_devices')
        dev_type (iterable, str): Accepted device type names, e.g. ["Motor", "Drot"]
        alt_dev_type (str, None) : If not found look at a widget defined for a `alt_dev_type`
        exclude_device (str, iterable): exclude the device with the given names
        exclude_dev_type (str, iterable): exclude device with the given types
        widget_kind (str): string defining the widget kind (default, 'ctrl')
        alt_layout (iterable, str): Alternative layout name if `layout` is not found
        
        column, row, columnSpan, rowSpan, stretch, alignment : for layout placement. 
                The use depend of the nature of the layout (Grid, HBox, VBox) 
    
    """
    layout: str = "ly_devices" 
    device: Union[str, Iterable] = "*"
    dev_type: Union[str, Iterable]  = "*"
    alt_dev_type: Optional[List[str]] = None

    exclude_device: Union[str, Iterable] = ""
    exclude_dev_type: Union[str, Iterable]  = ""
    
    widget_kind: str = "ctrl"
    alt_layout: Union[str,Iterable] = [] 
    column: int = 0
    row: int = 0
    columnSpan: int = 1
    rowSpan: int = 1
    
    stretch: int = 0
    alignment: int = 0

    class Config:
        extra = 'forbid'
    
    @validator("alt_layout")
    def _liste_me(cls, value):
        return [value] if isinstance(value, str) else value



class ConfigView(BaseUiLinker.Config):
    """ One item that define a layout compose from a ui resource file and a setup 

    The setup is a list of ViewSetup defining one ui layout and what shall be inside. 
    """
    
    alt_dev_type: Optional[List[str]] = None
    setup: List[ConfigViewSetup] = ConfigViewSetup()
    size: Optional[List] = None
    ui_file: Optional[str] = None

    @validator("ui_file")
    def _validate_ui_file(cls, ui_file):
        """ Check if ui_file exists in resources """
        if ui_file is not None:
            try:
                find_ui(ui_file) 
            except IOError as e:
                raise ValueError(e)
        return ui_file
    @validator('setup', always=True)
    def _validate_setup(cls, setup, values):
        alt_dev_type = values.get('alt_dev_type', None)
        for cv in setup:
            if cv.alt_dev_type is None:
                cv.alt_dev_type = alt_dev_type
        return setup


line_setup =  ConfigView(setup = [ConfigViewSetup(widget_kind="line", device="*")])
ctrl_setup =  ConfigView(setup = [ConfigViewSetup(widget_kind="ctrl", device="*")])


class ConfigDevicesWidget(BaseUiLinker.Config):
    """ Configuration for for several views """
    alt_dev_type: Optional[List[str]] = None
    views : Dict[str,ConfigView] = {"line":line_setup, "ctrl":ctrl_setup}
    
    @validator('views', always=True)
    def _validate_views(cls, views, values):
        alt_dev_type = values.get('alt_dev_type', None)
        for cv in views.values():
            if cv.alt_dev_type is None:
                cv.alt_dev_type = alt_dev_type
            for s in cv.setup:
                if s.alt_dev_type is None:
                    s.alt_dev_type = alt_dev_type
        return views



def insert_widget(
     device: BaseDevice, 
     layout: QLayout, 
     config: ConfigViewSetup = ConfigViewSetup(), *,
     
     default_factory: Optional[WidgetFactory] = None,
        ) -> BaseUiLinker:
    """ Insert one device widget inside a QT Layout object 
    
    Args:
        device (BaseDevice): list of devices 
        layout: (QLayout)
        config:  ConfigViewSetup   
    
    Returns:
       linker (BaseUiLinker): A device linker object (not yet connected to device)
       
    """
    factory = get_widget_factory(config.widget_kind, device.config.type,
                                default=default_factory,
                                alt_dev_type=config.alt_dev_type
                                )       
    linker = factory.build()
    
    widget = linker.widget 
    if isinstance(layout, QBoxLayout): 
        layout.addWidget(widget, config.stretch, QtCore.Qt.AlignmentFlag(config.alignment))
    elif isinstance(layout, QGridLayout):
        layout.addWidget(widget, config.row, config.column, config.rowSpan, config.columnSpan)
    else:
        layout.addWidget(widget)  
    return linker 



def _obj_to_match_func(obj):
    if not obj:
        return lambda name: False 
    if isinstance(obj, str):
        return lambda name: glob.fnmatch.fnmatch(name, obj)
    elif hasattr(obj, "__iter__"): 
        return  lambda name: name in obj

def filter_devices(devices, config: ConfigViewSetup = ConfigViewSetup() ):
        c = config
        output_devices = []
        match_device = _obj_to_match_func(c.device)
        match_type   = _obj_to_match_func(c.dev_type)
        
        exclude_match_device = _obj_to_match_func(c.exclude_device)
        exclude_match_type   = _obj_to_match_func(c.exclude_dev_type)
        for device in devices:        
            if exclude_match_device(device.name): continue
            if exclude_match_type(device.config.type): continue
            if match_device(device.name) and match_type(device.config.type):
                output_devices.append(device)  
        return output_devices


def find_layout(ui: QWidget, config:  ConfigViewSetup = ConfigViewSetup() ):
        """ find a layout from a parent ui according to config 
        
        Look for a layout named as .layout properties. If not found look inside 
        the .alt_layout list property. 
        """
        layout = ui.findChild(QLayout, config.layout)
        if layout is None:
            for ly_name in config.alt_layout:
                layout = ui.findChild(QLayout, ly_name)
                if layout: break
            else:
                raise ValueError(f"Cannot find layout with the name {layout!r} or any alternatives")
        return layout
   



class ViewUiLinker(BaseUiLinker):
    """ A widget linker for one single view """
    Config = ConfigView
    _device_linkers  = None       
    
    class Widget(QFrame):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # make a very simple widget with one single layout named ly_devices
            # do not change the layouut_name 
            #layout = QVBoxLayout(objectName="ly_devices") # give a default name for the layout 
            #self.setLayout(layout)
            loadUi(find_ui('simple_devices_frame.ui'), self)

    @classmethod
    def new_widget(self, config):
        if config.ui_file:
            return loadUi(find_ui(config.ui_file))
        else:
            return self.Widget()

    def _link(self, downloader):

        for device, linker in self._device_linkers:
            linker.connect( downloader, device )
        


    def connect(self, downloader, obj_list, data = None):
        if data is None:
            data = self.new_data()
        self.setup_ui( obj_list , data)
        self._link(downloader)
        
        return WidgetControl( self, downloader, obj_list, data )
       
    def disconnect(self):
        super().disconnect()
        if self._device_linkers:
            for _, linker in self._device_linkers:
                linker.disconnect()
    
    def setup_ui(self, obj_list: List[_BaseObject], data: BaseData):
        self.disconnect()
        self.clear()
        
        # pairs of device/linker is recorded they are necessary to connect/disconnect etc ... 
        self._device_linkers = []
        for setup in self.config.setup:
            layout= find_layout( self.widget, setup )
            
            for device in filter_devices(obj_list, setup):
                linker = insert_widget(device, layout, setup)
                self._device_linkers.append( (device, linker ))

    def clear(self):
        if self._device_linkers:
            for d,l in self._device_linkers:
                l.widget.setParent(None)
    
class DevicesWidgetLinker(BaseUiLinker):
    """ A widget linker containing several defined views """
    Config = ConfigDevicesWidget
    
    class Data(BaseModel):
        current_view: str = "line"
    
    class Widget(QWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.container_layout = QVBoxLayout()
            self.setLayout(self.container_layout)
    
    _view_linker = None

    def _link(self, downloader):
        self._view_linker._link(downloader)

    def connect(self, downloader, obj_list, data = None):
        if data is None:
            data = self.new_data()
        self.setup_ui(obj_list, data)
        #self._view_linker.connect(downloader, obj_list)
        self._link(downloader)

        return WidgetControl( self, downloader, obj_list, data )

    def disconnect(self):
        super().disconnect()
        if self._view_linker:
            self._view_linker.disconnect()
    
    def clear(self):
        if self._view_linker:
            self._view_linker.clear()
            self._view_linker.widget.setParent(None)
        
    def setup_ui(self, obj_list: List[_BaseObject], data: BaseData):
        self.disconnect()
        self.clear()
        self._view_linker = None

        view = self.config.views[data.current_view]

        vl = ViewUiLinker(config=view)
        self.widget.container_layout.addWidget(vl.widget)
        vl.setup_ui( obj_list,  vl.new_data() ) 
        self._view_linker = vl

from .widget_io import Inputs, Outputs, InputOutputs
from .io import find_ui
from pydevmgr_core import Downloader, _BaseObject, DataLink, BaseData, RpcError
from typing import Union, Optional, Callable, Iterable
from PyQt5.QtWidgets import QLayout,  QBoxLayout,  QGridLayout , QWidget, QAction, QComboBox, QVBoxLayout, QBoxLayout, QGridLayout
from PyQt5 import uic, QtCore
from pydantic import BaseModel
#QCheckBox, QAction, QPushButton, QComboBox, QLayout,  QWidget, QFrame

class Action:
    """ An action object must be created from a pool of actions of class :class:`Actions` 
    
    Args:
       - parent: :class:`Actions`
       - func (Callable): Command function must take len(inputs) arguments
       - inputs (List): list of static or callable arguments for func
                        if callable it will be called at run time 
                        otherwhise they are static args, sent has is 
       - feedback (Callable) : function of signature f(er, msg) called for feedback. 
                            In case of action this is called only on exception 
        - before (Callable): function without argument called before ``func`` 
        - after (Callable): function without argument called after ``func`` 
    """
    def __init__(self, parent, 
          func: Callable, 
          inputs: list = None, 
          feedback: Callable = None, 
          before: Callable = None, 
          after: Callable = None, 
          okay_msg: str = ""
        ) -> None:        
        inputs = [] if inputs is None else inputs        
        # transform contant to lambdas function
        cleaned_inputs = []
        
        self._disconnection = parent._disconnection
        self._combos = parent._combos
                        
        # everything not callable is treated as a constant 
        # create a dummy function to return this constant
        # better to do it frontend rather then during execution                 
        for input in inputs:
            if not hasattr(input, "__call__"):
                input = lambda __cte__ = input: __cte__
            cleaned_inputs.append(input)
                
        
        if feedback is None:
            def func_call():   
                if before: before()   
                func(*(fi() for fi in cleaned_inputs))
                if after: after()
        else:         
            def func_call():            
                try:
                    if before: before()   
                    func(*(fi() for fi in cleaned_inputs))                    
                except (RpcError,TypeError,ValueError,RuntimeError) as er:
                    feedback(er, str(er))
                else:
                    feedback(0, okay_msg)
                finally:
                    if after: after()
                    
        # overwrite the run method             
        self.run = func_call
            
    def run(self):
        raise NotImplementedError('run')    
    
    def connect_button(self,        
        button: QWidget
      ) -> None:
        """ Connect the action to a button """
        button.clicked.connect(self.run)
        self._disconnection.append( button.clicked.disconnect )
    
    def connect_action(self,        
        action: QAction
      ) -> None:     
        """ Connect the action to a menu action """
        action.triggered.connect(self.run)
        self._disconnection.append( action.triggered.disconnect )
    
    def connect_checkbox(self, 
        checkbox
    ) -> None:
        """ Connect the action to a CheckBox """
        checkbox.stateChanged.connect(self.run)
        self._disconnection.append( checkbox.stateChanged.disconnect ) 
    
    def connect_combo(self, 
       combo: QComboBox, 
    ) -> None:
        """ Connect the action to a combo box """
        def combo_call(idx):
            self.run()
            
        combo.currentIndexChanged.connect(combo_call)
        self._disconnection.append( combo.currentIndexChanged.disconnect ) 
        
    def connect_item(self,         
        combo: QComboBox, 
        item_id: int        
     ) -> None:
        """ Connect the action to a combo box and the item id """
        try:
            f, item2action = self._combos[combo]
        except KeyError:
            self._new_combo(combo)
            f, item2action = self._combos[combo]        
        item2action[item_id] = self
        
    def _new_combo(self, combo):
        if combo in self._combos:
            try:
                combo.currentIndexChanged.disconnect()
            except TypeError:
                pass
                        
        item2action = {}
        def combo_call(i):
            try:
                action = item2action[i]
            except KeyError:
                return 
            action.run()            
        
        self._combos[combo] = (combo_call, item2action)
        combo.currentIndexChanged.connect(combo_call)
        self._disconnection.append(combo.currentIndexChanged.disconnect)

    
class Actions:
    def __init__(self):        
        self._disconnection = []
        self._combos = {}
        
    def add(self, func, inputs=None, feedback=None, before=None, after=None):
        return Action(self, func, inputs, feedback=feedback, before=before, after=after)
        
    def disconnect(self):
        for f in self._disconnection:
            try:
                f()
            except TypeError:
                pass
    

class WidgetControl:
    """ Allows to control a device widget 
    
    A WidgetControl is returned by the method .connect of the linker (:class:`BaseUiLinker`) 
    Is not realy intended to be used outiside of this scope. 
    
    it allows to:
       - update : update a widget with new data if this is not done automatically  
       - disable : the widget is disabled and also the corresponding nodes are free from the downloader
       - enable : re-enable the widget connection 
       - kill : clear any connections between widget and downloader and device so the widget can be destroyed 
    
    enable/disable can be use in the context of a hidden tab for instance.
    
    Args:
    
      Basically they are the linker and all arguments necessary to re-establisher a connection between
      the widget and Downloader and Device
      
        - linker :class:`BaseUiLinker` 
        - downloader  :class:`Downloader`the downloader used by linker to connect widget and device output
        - obj :class:`_BaseObject` device/interface/manager.. used by the linker to connect widget and action methods    
        - data Optional[BaseData]: As created by the linker connection 
   
    Examples:
    
    ::
    
        from pydevmgr_elt import open_device, Downloader
        from pydevmgr_qt import get_widget_factory
        
        downloader = Downloader()
        motor = open_device('resource_path.yml', 'motor1')
        w = get_widget_factory('ctrl', 'Motor').connect(downloader, motor)
        w.disable()
        w.enable()
        
    """
    def __init__(self, 
          linker, 
          downloader: Downloader, 
          device: _BaseObject, 
          data: BaseData 
        ) -> None:
        self.linker  = linker
        self.downloader = downloader
        self.device = device
        
        self.data   = data
         
    @property
    def widget(self):
        return self.linker.widget
    
    def update(self):
        """ Force the widget update now
        
        If self.config.link_update is false the update is not triggered by the downloader. One may want to 
        have more control on when the widget is updated
        """
        self.linker.update(self.data)
    
    def disable(self):
        """ disable the widget and disconnect it to the downloader 
        
        This means that all parameters used inside the widget are freed from the pool of node to 
        download. 
        The connection can be re-established using the ``enable`` method.
        
        disable/enable can be usefull when part of a widget is not used or hidden (for instance in a tab)
        """
        self.linker.disconnect()
        self.linker.widget.setEnabled(False)
        self.linker.widget.repaint()
    
    def enable(self):
        """ re-establish a connection previously cut by disable and enable the widget """
        self.linker.disconnect()
        self.linker.connect(self.downloader, self.device, self.data)
        self.linker.widget.setEnabled(True)
        
    def kill(self):
        """ Kill any connection between widget and downloader, so the widget can be destroyed """
        self.linker.disconnect()
        self.widget.setParent(None)
        self.linker = None
        self.device = None
        self.downloader = None
        self.data = None
    
    def append_in_layout(self, 
           layout: QLayout, 
           stretch: Optional[int] = 0, 
           alignment: Optional[int] = 0, 
           row: Optional[int] = 0, 
           column: Optional[int] = 0, 
           rowSpan: Optional[int] = 1, 
           columnSpan: Optional[int] = 1
        ) -> None:
        """ Place the attached ui widget in control into a QLayout """
        widget = self.widget 
        if isinstance(layout, QBoxLayout): 
            layout.addWidget(widget, stretch, QtCore.Qt.AlignmentFlag(alignment))
        elif isinstance(layout, QGridLayout):
            layout.addWidget(widget, row, column, rowSpan, columnSpan)
        else:
            layout.addWidget(widget)        
    
class BaseUiLinker:
    """ UiLinker takes care of the link between a widget and a downloader and device 
    
    Args:
       widget (optional, :class:`QWidget`) : 
               if not given the default widget is built with the Widget attribute 
                e.i.  MotorCtrl() is equivalent to MotorCtrl(MotorCtrl.Widget()) 
    
    Example:
    
    ::
       
       from pydevmgr_elt import open_device, Downloader
       from pydevmgr_qt import get_widget_factory
       
       downloader = Downloader()
       motor = open_device('resource_path.yml', 'motor1')
       
       motorCtrl = MotorCtrl().connect(downloader, motor)
           
    """        
    Data = BaseModel
    Widget = QWidget    
    class Config(BaseModel):
        link_failure: bool = True
        link_update: bool = True
    
    ## #############################################################
    #  
    #   Engine Methods
    #
    ## #############################################################
    def __init__(self, widget=None, config=None, **kwargs):

        self._config = self.parse_config(config, **kwargs)

        if widget is None:
            widget = self.new_widget(self._config)
        
        self.widget = widget
                
        self.actions = Actions()
        self.inputs = Inputs()
        self.outputs = Outputs()
        self.io = InputOutputs()        
        self.init_vars()        
    
    @property
    def config(self):
        return self._config
    
    @classmethod
    def new_widget(self, config):
        """ Return a new widget for this linker """
        return self.Widget()


    @classmethod
    def parse_config(cls, __config__=None, **kwargs):
        if __config__ is None:
            return cls.Config(**kwargs)
        if isinstance(__config__ , cls.Config):
            return __config__
        if isinstance(__config__, dict):
            return cls.Config( **{**__config__, **kwargs} )
        raise ValueError(f"got an unexpected object for config : {type(__config__)}")

    def _disconnect_widget(self):
        # function to be overwrtiten by link
        pass
    
    def _link(self, 
            downloader_or_connection: Union[Downloader,Downloader.Connection],
            dl: DataLink, 
            data :  BaseData,
         ) -> None:
        """ Link the UI to a downloader 
        
        Each time the downloader will "download" the update will be executed with the 
        freshly updated data.
        
        Args:
            - downloader (:class:`pydevmgr.Downloader`)
            - dl (:class:`pydevmgr.DataLink`)
            - data (:class:`BaseModel`) (shall be the one linked with the dl DataLink)
        """
        self._disconnect_widget() # remove any connection 
        
        link_failure = self.config.link_failure
        link_update = self.config.link_update

        if isinstance(downloader_or_connection, Downloader):  
            connection  = downloader_or_connection.new_connection()
            new_connection = True 
        else:
            connection  = downloader_or_connection
            new_connection = False
        
        # The data is added to the queue of data to be downloaded 
        # y the downloader associated to the connection  
        #dl =  DataLink(obj, data)       
        connection.add_datalink(dl)
        
        if link_update:
            def download_callback(dummy=None):
                self.update(data)
            connection.add_callback(download_callback)
        
        if link_failure:
            connection.add_failure_callback(self.update_failure)
        
        ##
        #  Overwrite the disconnect_widget function 
        if new_connection:
            # we can simply disconnect the connection from the downloader all callback and datalink 
            # will be removed 
            def disconnect_widget():
                connection.disconnect()
        else:       
            # the connection may be used somewhere else so remove only the created 
            # datalinks and callback 
            if link_failure:
                def disconnect_widget():
                    connection.remove_datalink(dl)
                    if link_update:
                        connection.remove_callback(download_callback)
                    connection.remove_failure_callback(self.update_failure)
            else:
                def disconnect_widget():
                    connection.remove_datalink(dl)
                    if link_update:
                        connection.remove_callback(download_callback)
        self._disconnect_widget = disconnect_widget
        
    def connect(self, 
           downloader: Downloader, 
           obj: _BaseObject,
           data = None,       
        ) -> WidgetControl:
        """ Connect the widget to a obj 
        
        Args:
            downloader (:class:`pydevmgr_core.Downloader` or :class:`pydevmgr_core.DownloaderConnection`)
            obj  (:class:`pydevmgr_core._BaseObject`): most probably a  :class:`pydevmgr_core.BaseDevice`
            data (optional, :class:`pydantic.BaseModel`): data structure to be linked. If not given
                  It is created from the class .Data attribute
          
        Returns:
            ctrl: (:class:`WidgetControl`) This object allows to control the link between the widget, 
                the downloader and device. The ctrl is usefull for a parent app whish needs to 
                enable/disable widgets.
        """
        
        if data is None: 
            data = self.new_data()
        # self.disconnect() # Not sure about this, better to keep the disconnection manual 
        #self.setup_ui(obj, data)
        dl = DataLink(obj, data)
        self.setup_ui(obj, data)
        self._link(downloader, dl, data)          
        return WidgetControl(self, downloader, obj, data)
        
    def disconnect(self) -> None:
        """ Free the uilink from downloader connection callbacks 
        After executing, the refresh is stopped and widget actions are removed 
        """
        self._disconnect_widget()        
        self.disconnect_events()
    
    def new_data(self, **kwargs):
        return self.Data(**kwargs)
    
    def disconnect_events(self):
        # disconnect all button or other action associiated to a device 
        # which has been connected by setup              
        self.actions.disconnect()
    
    def update_failure(self, er):
        if er:
            self.widget.setEnabled(False) 
        else:
            self.widget.setEnabled(True)       
        
    def __del__(self):
        try:
            self.disconnect()
        except Exception as e:
            pass        

    ## #############################################################
    #
    #    Methods To be implemented 
    #
    ## #############################################################
    
    def init_vars(self):
        """ init all widget input and output handlers """
        pass
    
    def setup_ui(self, obj: _BaseObject, data: BaseData) -> None:
        """ setup the UI for a input device and associated data 
        
        setup change the static data and the actions associated to buttons, dropdown, etc ...
        """        
        # Disconnect all buttons, dropdoown, etc from previous connected events
        self.disconnect_events()
        # to be implemented 
        
        
    def update(self, data: BaseData) -> None:
        """ update the ui to new data 
        
        Args:
           data (class:`pydantic.BaseModel`): Data Model as returned by .new_data() method            
        """
        pass

    def feedback(self, er, msg=''):
        pass
 



class LayoutLinker:
    _wctrl_loockup = None
    Layout = QVBoxLayout
    _downloader = None
    def __init__(self, layout: Optional[str] = None):
        if layout is None:
            layout = self.Layout()
        
        self.layout = layout
        self._wctrl_loockup = {}
        
    def connect(self, downloader):
        """ Connect the LayoutLinker to a downloader """
        self._downloader = downloader
    
    def disconnect(self):
        """ disconnect from downloader and disconnect all linker children """
        self._downloader = None
        for l in self._wctrl_loockup.values():
            l.disable()
        
    def clear(self):
        """ Clear all widget and disconnect them """
        for i in reversed(range(self.layout.count())): 
            w = self.layout.itemAt(i).widget()
            w.setParent(None)            
            if w in self._wctrl_loockup:
                l = self._wctrl_loockup.pop(w)
                l.disable()
                
    def add_device(self, 
            device : _BaseObject, 
            widget_kind: str , 
            data: BaseData =None, 
            default_factory: Optional['WidgetFactory'] = None, 
            stretch: Optional[int] = 0, 
            alignment: Optional[int] = 0, 
            row: Optional[int] = 0, 
            column: Optional[int] = 0, 
            rowSpan: Optional[int] = 1, 
            columnSpan: Optional[int] = 1
            ):
        if self._downloader is None:
            raise ValueError("LayoutLinker is not connected")
        
        factory = get_widget_factory(widget_kind, device.config.type, default=default_factory)      
        linker = factory.build()
        ctrl = linker.connect(self._downloader, device, data=data)
        self._wctrl_loockup[ctrl.widget] = ctrl
        ctrl.append_in_layout(self.layout, stretch = stretch, alignment=alignment, row=row, 
                              column=column, rowSpan=rowSpan, columnSpan=columnSpan
                            )
                        
        
    
class WidgetFactory:
    """ A factory for widget and widget linker 
    
    A WdigetFactory is reutrned by :func:`get_widget_factory`
    
    Args:
        - widget_type (str) :  e.g. 'line', 'ctrl', 'cfg'
        - dev_type (str) : device type, e.g. 'Motor', 'Lamp', 'Adc', ...
        - LinkerClass (BaseUiLinker): Class of the linker. The linker is building the relation between
                                    a widget and the device. 
        - WidgetClass (QWidget, optional): if not given take the default defined in LinkerClass
        - DataClass (BaseModel, optional): the class to build the data structure. If not given take 
                                           one defined in LinkerClass 
    """
    def __init__(self, 
            widget_type: str, 
            dev_type: str, 
            LinkerClass: BaseUiLinker, 
            WidgetClass: Optional[QWidget] =None, 
            DataClass: Optional[BaseData] =None
          )-> None:
        self._widget_type = widget_type
        self._dev_type = dev_type 
        
        self.LinkerClass = LinkerClass
        if WidgetClass is None:
            WidgetClass = LinkerClass.Widget
        self.WidgetClass = WidgetClass
        if DataClass is None:
            self.DataClass = LinkerClass.Data
                
    def build_and_connect(self, 
          downloader: Downloader, 
          device: _BaseObject, 
          data: BaseData = None, 
          widget: Optional[QWidget] =None
        )-> WidgetControl:
        if widget is None:
            widget = self.WidgetClass()
        if data is None:
            data = self.DataClass()
            
        return self.Linker(widget).connect(downloader, device, data=data)
        
    def build(self,  widget: Optional[QWidget] =None) -> BaseUiLinker:
        if widget is None:
            widget = self.WidgetClass()
        return self.LinkerClass(widget)


_widget_factories = {}
def record_widget_factory(
       widget_type: str, 
       dev_type: Union[None, str,Iterable],
       LinkerClass: BaseUiLinker
     ) -> None:
    """ Record a widget linker defined by its type name and a device type 
    
    Args:
       - widget_type : string defining the widget (e.g. 'line', 'ctrl', 'cfg', ...)
       - dev_type : A list or a string for which the Linker apply. If None the Linker can handle any type 
       - LinkerClass: The Linker Class (derived from :class:`BaseUiLinker`)
    """
    
    global _widget_factories
    if not isinstance(dev_type, str) and hasattr(dev_type, '__iter__'):
        for dt in dev_type:    
            _widget_factories[(widget_type, dt)] =  WidgetFactory(widget_type, dt, LinkerClass)
    else:        
        _widget_factories[(widget_type, dev_type)] =  WidgetFactory(widget_type, dev_type, LinkerClass)

def get_widget_types(dev_type: str):
    """ Return a list of available widget str types for a given device name """
    return [wt for wt, dt in _widget_factories if dt==dev_type]
    
def get_widget_factory(
       widget_type: str, 
       dev_type: Union[None, str], 
       default: Optional[WidgetFactory] = None, 
       alt_dev_type: Optional[Iterable] = None
     ) -> WidgetFactory:
    """ Return a widget linker factory to build a widget for a given widget type and device type 
    
    Args:
    
       - widget_type (str) : string defining the widget (e.g. 'line', 'ctrl', 'cfg', ...)
       - dev_type (str): The device type 
       - default (optional, WidgetFactory): If given and the Factory is not found it is returned else
                an error is raised.
        - alt_dev_type (iterable, optional): Alternative type list if the widget is not found with dev_type 
    Example:
        
        > get_widget_factory('ctr', 'Motor').build().connect(downloader, motor1)
        
    """ 
    # it may be that this is defined for all device type
    try:
        return  _widget_factories[(widget_type, None)]
    except KeyError:
        pass

    try:
        return  _widget_factories[(widget_type, dev_type)]
    except KeyError:
        pass

    if alt_dev_type:
        for tpe in alt_dev_type:
            try:
                return  _widget_factories[(widget_type, tpe)]
            except KeyError:
                pass

    
    if default:
        return default

    raise ValueError(f"Widget Factory with type {widget_type} and device type {dev_type} cannot be found, set `alt_dev_type` or `default`")


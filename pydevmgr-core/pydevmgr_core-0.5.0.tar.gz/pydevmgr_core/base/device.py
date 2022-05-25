from .base import (_BaseObject, _BaseProperty, BaseData, open_object, 
                        ChildrenCapability, ChildrenCapabilityConfig
                        )
from .class_recorder import  KINDS,  record_class
from .node import BaseNode 
from .interface import BaseInterface
from .rpc import BaseRpc
from enum import Enum 


from typing import  Optional, Any 


# used to force kind to be a device
class DEVICEKIND(str, Enum):
    DEVICE = KINDS.DEVICE.value





class BaseDeviceConfig(_BaseObject.Config, ChildrenCapabilityConfig):
    kind: DEVICEKIND = DEVICEKIND.DEVICE
    type: str = "Base"
    
    
    def cfgdict(self, exclude=set()):
        all_exclude = {*{}, *exclude}
        d = super().cfgdict(exclude=all_exclude)       
        return d
    
  
    
def open_device(cfgfile, path=None, prefix="", key=None, default_type=None, **kwargs):
    """ Open a device from a configuration file 

        
        Args:
            cfgfile: relative path to one of the $CFGPATH or absolute path to the yaml config file 
            key: Key of the created Manager 
            path (str, int, optional): 'a.b.c' will loock to cfg['a']['b']['c'] in the file. If int it will loock to the Nth
                                        element in the file
            prefix (str, optional): additional prefix added to the name or key

        Output:
            device (BaseDevice subclass) :tanciated Device class     
    """
    kwargs.setdefault("kind", KINDS.DEVICE)

    return open_object(cfgfile, path=path, prefix=prefix, key=key, default_type=default_type, **kwargs) 




class DeviceProperty(_BaseProperty):    
    fbuild = None    
    
    def builder(self, func):
        """ Decorator for the interface builder """
        self.fbuild = func
        return self
     
   
    def __call__(self, func):
        """ The call is used has fbuild decorator 
        
        this allows to do
        
        ::
            
            class MyManager(BaseManager):
                @MyDevice.prop('motor2')
                def motor2(self, motor):
                    # do somethig
                    
        """
        self.fbuild = func
        return self
    
    def _finalise(self, parent, device):
        # overwrite the fget, fset function to the node if defined         
        if self.fbuild:
            self.fbuild(parent, device)  




@record_class
class BaseDevice(_BaseObject, ChildrenCapability):
    Property = DeviceProperty
    Config = BaseDeviceConfig
    Interface = BaseInterface
    Data = BaseData
    Node = BaseNode
    Rpc = BaseRpc    
    
    def __init__(self, 
           key: Optional[str] = None, 
           config: Optional[Config] = None,
           **kwargs
        ) -> None:        
        
        super().__init__(key, config=config, **kwargs)  
        if self._localdata is None:
            self._localdata = {}
    
    def __enter__(self):
        try:
            self.disconnect()
        except (ValueError, RuntimeError):
            pass 
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False # if exception it will be raised 
    
    @classmethod
    def parse_config(cls, config, **kwargs):
        if isinstance(config, dict):
            kwargs = {**config, **kwargs}
            config = None
        return super().parse_config( config, **kwargs)
        
    @classmethod
    def new_com(cls, config: Config, com: Optional[Any] = None) -> Any:
        """ Create a new communication object for the device 
            
        Args:
           config: Config object of the Device Class to build a new com 
           com : optional, A parent com object used to build a new com if applicable  
           
        Return:
           com (Any): Any suitable communication object  
        """
        return com 
    
                        
    def connect(self):
        """ Connect device to client """
        raise NotImplementedError('connect method not implemented') 
    
    def disconnect(self):
        """ Disconnect device from client """
        raise NotImplementedError('disconnect method not implemented')    
    
    def is_connected(self):
        """ True if device connected """
        raise NotImplementedError('is_connected method not implemented') 
    
    def rebuild(self):
        """ rebuild will disconnect the device and create a new com """
        self.disconnect()
        self.clear()
        self._com = self.new_com(self._config)
    
        


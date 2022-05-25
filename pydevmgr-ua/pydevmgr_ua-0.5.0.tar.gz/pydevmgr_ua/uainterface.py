from pydevmgr_core import BaseNode, BaseInterface, record_class, ksplit
from .uacom import opcua, UaCom, _UaCom, parse_com
from .uanode import UaNode
from .uarpc import UaRpc
from pydantic import BaseModel, AnyUrl
from typing import Optional, Any, Union, List, Type, Dict

class UaInterfaceConfig(BaseInterface.Config, extra="allow"):
    Node = UaNode.Config
    Rpc = UaRpc.Config

    type: str = "Ua"
    prefix: str = "" # prefix added to com.prefix 
     
@record_class    
class UaInterface(BaseInterface):
    """ Interface containing :class:`pydevmgr_ua.UaNode` or :class:`pydevmgr_ua.UaRpcNode` objects
    
    Each :class:`pydevmgr_ua.UaNode` will inerit from the Ua Client communication and will have the
       UA prefix of the interface  
    
    Note, the .com attribute is a (sub)UaCom object built from the com class argument 
        
    The UA prefix can be defined in the interface config or in the com object or in both:
    
    
    e.g. on the example bellow the 3 UaInterface instances will have the same prefix
    
    :: 
       
       from pydevmgr_ua import UaCom, UaInterface
       i1 = UaInterface(prefix="MAIN.stat" ,  com=UaCom(prefix="") )
       i2 = UaInterface(prefix="stat" ,  com=UaCom(prefix="MAIN") )
       i3 = UaInterface(prefix="" ,  com=UaCom(prefix="MAIN.stat") )
       
       assert i1.com.prefix == i2.com.prefix
       assert i2.com.prefix == i3.com.prefix
    
    
    Args:
        
        key (str): a unique key defining the interface. This is generally the same key as the host 
                  :class:`Device`. e.g. mgr.motor1.key ==  mgr.motor1.stat.key == mgr.motor1.cfg.key
        config (optional, :class:`pydevmgr_ua.UaInterface.Config`): configuration of the interface 
        com (optional, :class:`UaCom`, :class:`opcua.Client`, dict, str): 
            - if str create a :class:`UaCom` from the str address 
            - if :class:`opcua.Client` wrap it in a :class:`UaCom`
            - if :class:`UaCom` use it
        \*\*kwargs: If configuration is  None they are used to build the config otherwise they are ignored 
    
            
    """
           
    Config = UaInterfaceConfig
    Com = UaCom
    Node = UaNode
    Rpc = UaRpc
    
    def __init__(self, 
          key: Optional[str] = None,           
          config: Optional[Config] = None, *,
          com: Union[UaCom, opcua.Client, str] = None, 
          **kwargs
        ) -> None:
        
        super().__init__(key, config=config, **kwargs)        
        com = parse_com(com, None)
          
        # assume it is a _UaCom object or similar 
        # not checking the type because I am the feeling it can be usefull for simulator at some points 
        self._com = com.subcom(self._config.prefix)
    
    @classmethod
    def new_args(cls, parent, name, config):
        d = super().new_args(parent, name, config)
        d.update(com=parent.com)
        return d        

    @property
    def com(self):
        return self._com
            


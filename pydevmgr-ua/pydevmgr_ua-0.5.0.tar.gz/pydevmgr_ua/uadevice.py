from pydevmgr_core import BaseDevice, record_class
from .uacom import UaCom, parse_com
from .config import uaconfig
from .uainterface import UaInterface
from .uanode import UaNode
from .uarpc import UaRpc
from typing import  Optional, Any
from pydantic import AnyUrl, Field

@record_class
class UaDevice(BaseDevice):
    Node = UaNode
    Rpc = UaRpc
    Interface = UaInterface
    
    
    class Config(BaseDevice.Config, extra="allow"):
        Node = UaNode.Config
        Interface = UaInterface.Config
        Rpc = UaRpc.Config

        type: str = "Ua"
        # AnyUrl  will valid the address to an url 
        # the url is first replaced on-the-fly if defined in host_mapping 
        address     : AnyUrl         = Field(default_factory=lambda : uaconfig.default_address) 
        prefix      : str            = ""
        namespace   : int            = Field(default_factory=lambda : uaconfig.namespace)
    
    _com = None                
    def __init__(self, 
           key: Optional[str] = None, 
           config: Optional[Config] = None,
           com: Optional[UaCom] = None,             
           **kwargs
        ) -> None:     
        super().__init__(key, config=config, **kwargs)
        self._com = self.new_com(self.config, com)

     

    @classmethod
    def new_com(cls, config: Config, com: Optional[UaCom] = None) -> UaCom:  
        """ Create a new communication object for the device 
            
        Args:
           config: Config object of the Device Class to build a new com 
           com : optional, A parent com object used to build a new com if applicable  
           
        Return:
           com (Any): Any suitable communication object  
        """

        if com is None:       
            return UaCom(address=config.address, namespace=config.namespace).subcom(config.prefix)
        if isinstance(com, dict):
            com = UaCom(**com)
        elif isinstance(com, UaCom.Config):
            com = UaCom(config=com)
        ## Warning config is changed to the com address and namespace 
        config.address = com.address 
        config.namespace = com.namespace           
        return com.subcom(config.prefix)
    
    @property
    def com(self):
        return self._com

    @classmethod
    def new_args(cls, parent, name, config):
        d = super().new_args(parent, name,  config)
        if isinstance( parent, (UaDevice, UaInterface) ):
            d.update(com=parent.com)
        return d


    def connect(self):
        """ Connect to the OPC-UA client """
        self._com.connect()
        
    def disconnect(self):
        """ Connect from the  OPC-UA client """
        self._com.disconnect()
    
    def is_connected(self):
        return self._com.is_connected()
    
    @property
    def uaprefix(self):
        return self._com.prefix

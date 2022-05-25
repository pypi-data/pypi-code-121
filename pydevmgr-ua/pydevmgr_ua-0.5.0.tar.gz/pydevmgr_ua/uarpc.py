from pydevmgr_core import BaseRpc, ksplit, kjoin, record_class
from .uacom import UaCom, _UaCom,  UAReadCollector, UAWriteCollector, parse_com
from .uabase import _UaComCapabilities

import opcua
from opcua import ua
from typing import Callable, Optional, Any, Union
from pydantic import AnyUrl, BaseModel, validator

class UaRpcConfig(BaseRpc.Config):
    type: str = 'Ua'
    suffix: Optional[str] = None # Suffix for the node name added to the com.prefix
    # these 
    com: Optional[UaCom.Config] = None
    
@record_class        
class UaRpc(BaseRpc, _UaComCapabilities):
    """ Object representing a value rpc node in opc-ua server """
    Config = UaRpcConfig
    Com = UaCom
    
    def __init__(self,  
          key: Optional[str] = None,            
          config: Optional[UaRpcConfig] = None, *,
          
          com: Union[dict, UaCom, opcua.Client] = None, 
          **kwargs
        ) -> None:
        super().__init__(key, config=config, **kwargs)   
        com = parse_com(com, self._config.com)
        # suffix define node and method name 
        node_name, method_name = ksplit( self._config.suffix )
        self._com = com.rpccom(node_name, method_name)
    
    @property
    def sid(self) -> Any:
        return self._com.sid
    
    @property
    def uanodeid(self) -> ua.NodeId:
        return self._com.nodeid

    def get_error_txt(self, rpc_error: int) -> str:
        """ get a text description of the rpc_error code 
        
        See the enumerator RPC_ERROR attribute 
        
        Args:
            rpc_error (int): rpc error code  
        """
        return 'unknown error'
    
    def fcall(self, *args) -> int:
        """ call method on serser, the arguments has been parsed before """        
        return self._com.call_method(*args)
    
    @classmethod
    def new_args(cls, parent, name, config):
        d = super().new_args(parent, name, config)
        d.update(com=parent.com)
        return d
           
    @property
    def com(self):
        return self._com
            
    def connect(self) -> None:
        """ Establish the client connection to OPC-UA server """
        self._com.connect()
        
    def disconnect(self) -> None:
        """ disconnect the OPC-UA client 
        
        This will only work if the Interface own the OPC-UA client (e.i. if the client was built at init)
        """
        self._com.disconnect()
    
    def is_connected(self) -> bool:
        """ Return True if the current device is connected to OPC-UA """
        return self._com.is_connected()               


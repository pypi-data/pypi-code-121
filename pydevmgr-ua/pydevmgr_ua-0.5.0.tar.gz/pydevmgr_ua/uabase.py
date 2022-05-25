from .uacom import UaCom, _UaCom
from pydantic import BaseModel
import opcua
from typing import Union, Optional
class _UaComCapabilities:
    # define classmethod to parse a UA communication
    @classmethod
    def parse_com(cls, 
        com: Optional[Union[UaCom,opcua.Client,str]], 
        config: BaseModel
      ) -> Union[UaCom,_UaCom]:
        if com is None:
            com = UaCom(config=config.com)            
        elif isinstance(com, (dict, BaseModel)):
            com = UaCom(config=com)
        elif isinstance(com, opcua.Client):
            com = _UaCom(ua_client=com) 
        elif isinstance(com, str):
            com = UaCom(address=com)     
        return com
    
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
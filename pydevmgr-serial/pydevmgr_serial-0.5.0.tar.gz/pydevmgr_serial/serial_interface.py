from typing import Optional 
from pydevmgr_core import BaseInterface
import serial as sr

    
class SerialInterface(BaseInterface):
    def __init__(self, 
           key: Optional[str], 
           config: Optional[BaseInterface.Config] = None, 
           com: Optional[sr.Serial] = None, 
           **kwargs
        ) -> None:
        # parse the config and com object                    
        super().__init__(key, config=config, **kwargs) 
        self._com = com 

    @property
    def com(self):
        return self._com 
    
    
    @classmethod
    def new_args(cls, parent, name, config):
        d = super().new_args(parent, name, config)
        d.update(com=parent.com)
        return d



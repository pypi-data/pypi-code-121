from typing import Optional
from pydevmgr_core import BaseNode

class BaseSerialNode(BaseNode):
    def __init__(self, key=None, config=None, com=None, **kwargs): 
        # parse the config and com object 
            
        super().__init__(key, config=config, **kwargs)
        self._com = com 


    @classmethod
    def new_args(cls, parent, name, config):
        d = super().new_args(parent, name, config)
        d.update(com=parent.com)
        return d

    @property
    def com(self):
        return self._com 
    
    @property
    def sid(self):
        # the port is the sid  
        return self._com.port
     
    def fget(self):
        raise NotImplementedError('fget')
        
    def fset(self, value):
        raise NotImplementedError('fset')
        

from pydevmgr_ua import UaInterface
from pydevmgr_core import record_class, ksplit, get_class

from typing import Dict, Any, Optional
from .tools import fjoin 
from .eltnode import EltNode
from .eltrpc import EltRpc
from . import io
from pydantic import root_validator


@record_class
class EltInterface(UaInterface):

    Node = EltNode
    Rpc = EltRpc
    class Config(UaInterface.Config, extra="allow"):
        Node = EltNode.Config
        Rpc = EltRpc.Config
        
        type: str = "Elt"
                
    def __init__(self, *args, fits_key: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self.fits_key = fits_key
    
    @classmethod
    def new_args(cls, parent, name, config):
        d = super().new_args(parent, name, config)
        d.update(fits_key = parent.fits_key)
        return d
         
    def get_nodes(self, node_names  = None):
        raise DeprecationWarning('get_nodes is deprecated use the .find method instead')
    
    @property
    def all_nodes(self) -> list:    
        raise DeprecationWarning('.all_nodes is deprecated use the .find method instead')
    
    @property
    def all_native_nodes(self) -> list:
        """ deprecated  use the .nodes attribute instead """
        raise DeprecationWarning('.all_native_nodes is deprecated use the .find method instead')
        
     

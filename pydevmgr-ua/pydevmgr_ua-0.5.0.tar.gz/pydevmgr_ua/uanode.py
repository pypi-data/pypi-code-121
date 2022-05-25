from pydevmgr_core import BaseNode, ksplit, kjoin, record_class
from .uacom import UaCom, _UaCom,  UAReadCollector, UAWriteCollector, parse_com
from .uabase import _UaComCapabilities

import opcua
from opcua import ua
from typing import Callable, Optional, Any, Union
from pydantic import AnyUrl, BaseModel, validator

class UaNodeConfig(BaseNode.Config):
    type: str = 'Ua'
    suffix: Optional[str] = None # Suffix for the node name added to the com.prefix
    # these 
    attribute: ua.AttributeIds = ua.AttributeIds.Value
    
    @validator("attribute", pre=True)
    def _validate_attribute(cls, value):
        if isinstance(value, str):
            return getattr(ua.AttributeIds, value)
        return value 
    
@record_class        
class UaNode(BaseNode, _UaComCapabilities):
    """ Object representing a value node in opc-ua server

    This is an interface representing one single value (node) in an OPC-UA server. 
    
    Args:
    
        key (str, optional): The string key representing the node in its context. If none a unique 
                   string key is build.
        config (optional, :class:`pydevmgr_ua.UaNode.Config`, dict): Config for the node
            includes: 
                - suffix (str): the node suffix in the OPC-UA server
                - attribute (uaAttributeIds) 
        
        For other arguments please see :class:`pydevmgr_core.BaseNode` documentation
                
    .. note::
            
                Several parser to ua Variant are defined in pydevmgr_ua and can be set with the `parser` argument: 
                
                - Int16, INT    (INT is an alias as TwinCat defines it)
                - Int32, DINT
                - Int64, LINT
                - UInt16, UINT
                - UInt32, UDINT
                - UInt64, ULINT
                - Float, REAL
                - Double, LREAL
                
                can also be created by VariantParser('Int16')                
                
    Example:
    
    In the example bellow it is assumed that the OPC UA server as a nodesid "ns=4;s=MAIN.Tamp001" node
    defined.
    
    ::
    
        >>> from pydevmgr_ua import UaNode, UaCom
        >>> com = UaCom(address=="opc.tcp://localhost:4840", namespace=4, prefix="MAIN")
        >>> temp = UaNode("temperature" , com=com, suffix="Temp001")
        >>> temp.get()
        
    Alternatively the com can be created on-the-fly
    
    :: 
    
        temp_config = {
            'com': {'address', "opc.tcp://localhost:4840", namespace=4, prefix="MAIN"}
            'suffix': 'Temp001'
        }
        temp = UaCom(config=temp_config)     
    
    One can build a UaInterface for several node 
    
    ::
    
        from pydevmgr_ua import UaInterface, UaNode
        from pydevmgr_core.nodes import Formula1
        
        class MyInterface(UaInterface):            
            temp_volt = UaNode.prop(suffix="Temp001")
            humidity = UaNode.prop(suffix="Humidity001")
            
            temp_kelvin = Formula1.prop(node="temp_volt", formula="230 + 1.234 * t", varname="t")
        
        sensors = MyInterface(com={'address', "opc.tcp://localhost:4840", namespace=4, prefix="MAIN"})
        
                                    
    """
    Config = UaNodeConfig
    Com = UaCom
    
    def __init__(self,  
          key: Optional[str] = None,            
          config: Optional[UaNodeConfig] = None, *,
          
          com: Union[dict, UaCom, opcua.Client] = None, 
          **kwargs
        ) -> None:
        super().__init__(key, config=config, **kwargs)        
        com = parse_com(com, None)
        self._com = com.nodecom(self._config.suffix)
    
    @property
    def sid(self) -> Any:
        return self._com.sid
    
    @property
    def uanodeid(self) -> ua.NodeId:
        return self._com.nodeid
    
    @classmethod
    def new_args(cls, parent, name, config):
        d = super().new_args(parent, name, config)
        d.update(com=parent.com)
        return d
    
    @property
    def com(self):
        return self._com
            
    def read_collector(self) -> UAReadCollector:
        """ Return a :class:`UAReadCollector` object to queue nodes for reading """
        return self._com.read_collector()
    
    def write_collector(self) -> UAWriteCollector:
        """ Return a :class:`UAWriteCollector` object to queue nodes and values for writing """
        return self._com.write_collector()
    
    def fget(self) -> Any:
        """ get the value from server """
        return self._com.get_attribute(self.config.attribute)
    
    def fset(self, value: Any) -> None:
        """ set the value on server 
        
        Args:
            value (any): if :attr:`~UaNode.parser` is defined it is used to parse the value
                can be str, float, int, or :class:`ua.Variant` or  :class:`ua.DataValue` 
        """
        a = self.config.attribute
        datavalue = self._parse_value_for_ua(value) # is the node as a parser it as already been parsed 
        self._com.set_attribute(a, datavalue)
            
    def _parse_value_for_ua(self, value: Any) -> None:        
        #if self._parser:
        #    value = self._parser(value)
        return self._com.parse_value(value)
        

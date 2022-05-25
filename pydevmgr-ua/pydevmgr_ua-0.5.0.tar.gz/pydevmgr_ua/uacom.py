import opcua
from opcua import ua
from typing import Optional, Any, Dict, Union
from pydevmgr_core import reconfig, BaseParser, record_class
from .config import uaconfig
from pydantic import BaseModel, AnyUrl, Field, Extra
from enum import Enum


def _ua_server_sid(client):
    """ Used in node to get a unique id per server 
    
    When for instance using download or upload method the coms are grouped 
    by server ID to allow one single call per server. 
    """
    u = client.server_url
    return (u.hostname, u.port) 

def kjoin(*names) -> str:        
    return ".".join(a for a in names if a)

######
#  Some special Vars with no or ambigous native python equivalent 

def Int16(value:int) -> ua.Variant:
    return ua.Variant(int(value), ua.VariantType.Int16) 
INT = Int16

def Int32(value: int) -> ua.Variant:
    return ua.Variant(int(value), ua.VariantType.Int32)
DINT = Int32

def Int64(value: int) -> ua.Variant:
    return ua.Variant(int(value), ua.VariantType.Int64)  
LINT = Int64

def UInt16(value: int) -> ua.Variant:
    return ua.Variant(int(value), ua.VariantType.UInt16) 
UINT = UInt16

def UInt32(value: int) -> ua.Variant:
    return ua.Variant(int(value), ua.VariantType.UInt32)
UDINT = UInt32

def UInt64(value: int) -> ua.Variant:
    return ua.Variant(int(value), ua.VariantType.UInt64)        
ULINT = UInt64

def Float(value: float) -> ua.Variant:
    return ua.Variant(float(value), ua.VariantType.Float)
REAL = Float

def Double(value: float) -> ua.Variant:
    return ua.Variant(float(value), ua.VariantType.Double)
LREAL = Double



class VARIANTS(str, Enum):
    """ Enumerator for Variant Parser """
    Int16 = "Int16"
    INT = "Int16"
    Int32 = "Int32"
    DINT = "Int32"
    Int64 = "Int64"
    LINT = "Int64"
    
    UInt16 = "UInt16"
    UINT = "UInt16"
    UInt32 = "UInt32"
    UDINT = "UInt32"
    UInt64 = "UInt64"
    ULINT = "UInt64"
    
    Float = "Float"
    REAL = "Float"
    Double = "Double"
    LREAL = "Double"

   
def _record_variants():   
    for t in ua.VariantType:
        if "Int" in t.name:
            def parse(value, config, vtype=t):
                return ua.Variant(int(value), vtype)
        elif "Float" in t.name or "Double" in t.name:
            def parse(value, config, vtype=t):
                return ua.Variant(float(value), vtype)
        else:        
            def parse(value, config, vtype=t):
                return ua.Variant(value, vtype)
        class Config(BaseParser.Config):
            type: str = 'Ua'+t.name
            
        cls = type( 'Ua'+t.name, (BaseParser,), {'parse':staticmethod(parse), 'Config':Config})
        record_class(cls)
        record_class(cls, type=t.name+"Variant")
        globals()[t.name] = cls()
        globals()['Ua'+t.name] = cls
        
        
_record_variants()

# record a new variant parser, it will transform any input to the right output variant 
@record_class    
class VariantParser(BaseParser):
    """ Parser for UA variant 
    
    Exemple::
    
       >>> from pydevmgr_elt import VariantParser, VARIANTS
       >>> parser = VariantParser(variant=VARIANTS.Int16)
       >>> parser(4.5)
       Variant(val:4.5,type:VariantType.Int16)
    
    """
    VARIANTS = VARIANTS
    
    class Config(BaseParser.Config):
        type: str = "Variant2"
        variant: VARIANTS = VARIANTS.Double 
    @staticmethod
    def parse(value, config):
        return ua.Variant(value, getattr(ua.VariantType, config.variant))   
        
##
# Read and write collectors for OPC-UA 

class UAReadCollector:
    """ A Collector to read the value of multiple opc-ua nodes in one roundtrip 
    
    Args:
        uaclient (:class:`opcua.Client`)
    """
    def __init__(self, uaclient: opcua.Client) -> None:
        params =  ua.ReadParameters()
        params.uaclient = uaclient
        self._keys = list()
        self._params = params
                
    def add(self, node) -> None:
        """ Add a UaNode to the queue 
        
        Args:
            node (:class:`pydevmgr.UaNode`): node to add in the key. 
                Note this is a pydevmgr UaNode and not an opcua.Node
        """
        rv = ua.ReadValueId()
        rv.NodeId = node.uanodeid
        #rv.AttributeId = ua.AttributeIds.Value
        rv.AttributeId = node.config.attribute
        self._params.NodesToRead.append(rv)
        self._keys.append(node)
    
    def read(self, data: dict) -> None:
        """ read all data from server and feed result in the input dictionary """
        result = self._params.uaclient.read(self._params)
        for key,r in zip(self._keys, result):
            r.StatusCode.check()
            data[key] =  r.Value.Value 

class UAWriteCollector:
    """ A Collector to write the value of multiple opc-ua nodes in one roundtrip 
    
    Args:
        uaclient (:class:`opcua.Client`)
    """
    def __init__(self, uaclient: opcua.Client) -> None:
        params =  ua.WriteParameters()
        params.NodesToWrite = []        
        params.uaclient = uaclient
        self._params = params
        
        
    def add(self, node, value: Any) -> None:   
        """ Add a node and its attached value to the queue 
        
        Args:
            node (:class:`pydevmgr.UaNode`): node to add in the key. 
                Note this is a pydevmgr UaNode and not an opcua.Node
            value (any): value to be writen 
        
        """ 
        wv = ua.WriteValue()
        wv.NodeId = node.uanodeid
        wv.AttributeId = ua.AttributeIds.Value
        wv.AttributeId = node.config.attribute 
        self._params.NodesToWrite.append(wv)
        wv.Value = node._parse_value_for_ua(value)
    
    def write(self) -> None:
        """ Write all values to server """
        params = self._params
        result = params.uaclient.write(params)
        for r in result: 
            r.check()


class _UaComNode:
    def __init__(self, ua_client, node,  namespace: int = uaconfig.namespace, sid: Optional[Any] = None):
        self._ua_client = ua_client
        ua_id = "ns={};s={}".format(namespace, node)    
        
        self._ua_client = ua_client
        self._ua_node = ua_client.get_node(ua_id)
        
        self._sid = sid
        self._ua_variant_type = None
    
    @property
    def sid(self) -> Any:
        """ Unique server identification. shall be any hashable object """        
        if self._sid:
            return self._sid            
        # in case UaComNode has not be created by UaCom , the sid was missing 
        # so we need to create one from the client=server information
        # The only way I found is this one if their is a connection
        if self._ua_node.server._uasocket:
            if self._ua_node.server._uasocket._socket.socket.fileno()>0:
                self._sid = self._ua_node.server._uasocket._socket.socket.getpeername()
                return self._sid
        # unconnected sid, should not really mater what the output is (except None reserved for aliases)
        return 999        

    @property
    def nodeid(self) -> ua.NodeId:
        return self._ua_node.nodeid
    
    def get_value(self) -> Any:
        """ get the node value from server """
        return  self._ua_node.get_value()
    
    def get_attribute(self, a):
        result = self._ua_node.get_attribute(a)
        return result.Value.Value
    
    def set_attribute(self, a, value):
        if a == ua.AttributeIds.Value:
            return self._ua_node.set_value(value)
        else:
            return self._ua_node.set_attribute(a, value)
    
    def set_value(self, datavalue: ua.DataValue) -> None:
        """ set the node value to server 
        
        Args:
            data value (:class:`ua.DataValue`): DataValue as returned by the method :meth:`UaComNode.parse_value`
        """
        self._ua_node.set_attribute(ua.AttributeIds.Value, datavalue)
    
    def parse_value(self, value: Any) -> ua.DataValue:
        """ parse a value to a  :class:`ua.DataValue` 
        
        Args:
            value (int, float, str, :class:`ua.Variant`,  :class:`ua.DataValue`)
                note if int, to remove ambiguity between int64, int32, the real variant is asked to 
                the server the first time than cashed. This should rarely append as UA type will be  
                parsed through the :class:`pydevmgr.UaNode`.
                
        """
        if isinstance(value, (int,)):
            # remove embiguity between int64 and int32, int16
            # we need to ask the variant_type on the server
            if self._ua_variant_type is None:
                self._ua_variant_type = self._ua_node.get_data_type_as_variant_type()
            datavalue = ua.DataValue(ua.Variant(value, self._ua_variant_type))
        elif isinstance(value, ua.DataValue):
            datavalue = value
        elif isinstance(value, ua.Variant):
            datavalue = ua.DataValue(value)
        else:
            datavalue = ua.DataValue(value)
        return datavalue 
                
    def call_method(self, methodid, *args) -> int:
        """ Call a method of the node 
        
        see :meth:`opcua.Node.call_method`    
        """        
        return self._ua_node.call_method(methodid, *args)
        
    def read_collector(self) -> UAReadCollector:
        """ Return a :class:`UAReadCollector` to collect nodes for reading node values on the server """
        return UAReadCollector(self._ua_node.server)
        
    def write_collector(self) -> UAWriteCollector:
        """ Return a :class:`UAWriteCollector` to collect nodes for writing node values on the server """
        return UAWriteCollector(self._ua_node.server)
    
    def connect(self):        
        self._ua_client.connect()
    
    def disconnect(self):  
        self._ua_client.disconnect()      
        #raise ValueError("Cannot disconnect: does not own the connection")
    
    @property
    def namespace(self):
        return self._namespace
    
            
class UaComNode(_UaComNode):
    """ A class com interface for opcua.Node 
    
    Function used in the context of pydevmgr are re-defined here. 
    
    
    Args:
        address (str, Optional): use to build a ua_client if this last one is None
        node: (str): node path this will be formated to a normal OPC-UA NodeId   
        namespace (int, optional): OPC-UA node namespace default is 4
        ua_client (:class:`opcua.Client`): use as is, if not None address will be ignored
        sid (Any, optional): Any hashable object which will be used to iddentify the "server"
                             a default one is built if None
        
          
    """
    #def __init__(self, ua_node: opcua.Node, sid: Optional[Any] = None) -> None:
    class Config(BaseModel):
        address: AnyUrl =  Field(default_factory=lambda : uaconfig.default_address)
        namespace: int =   Field(default_factory=lambda : uaconfig.namespace)
        node_name: str = ''
        class Config:
            extra = Extra.forbid
            
    def __init__(self, config: Config = None, **kwargs):
        config = reconfig(self.Config, config, kwargs)
        if config.address is None: 
            raise ValueError('address is None')            
        ua_client = opcua.Client(str(config.address))
        super().__init__(ua_client, config.node_name, namespace = config.namespace)
        self._config = config
    
    @property
    def config(self):
        return self._config
    
    def reset(self):
        ua_client = opcua.Client(str(self.config.address))
        super().__init__(ua_client, self.config.node_name, namespace = self.config.namespace)
    
    def connect(self):        
        self._ua_client.connect()
    
    def disconnect(self):        
        self._ua_client.disconnect()


class _UaComRpcNode(_UaComNode):
    def __init__(self, ua_client: opcua.Client,  
        node: str = '',
        method: str = '',
        namespace: int = uaconfig.namespace,
        sid: Optional[Any] = None   
        ):
        super().__init__(ua_client, node, namespace, sid=sid)         
        method_id = "{}:{}".format(namespace, method)  
        self._method_id = method_id
    
    def call_method(self, *args) -> int:
        """ Call a method of the node 
        
        see :meth:`opcua.Node.call_method`    
        """       
        return self._ua_node.call_method(self._method_id, *args)
    
class UaComRpcNode(_UaComRpcNode):
    """ A class interface for opcua.Node 
    
    Function used in the context of pydevmgr are re-defined here. 
        
    Args:
        us_node (:class:`opcua.Node`)
        sid (optional, any): hashable object (most likely str). Defines an unique server id.
    """
    #def __init__(self, ua_node: opcua.Node, sid: Optional[Any] = None) -> None:
    class Config(BaseModel):
        address: AnyUrl =  Field(default_factory=lambda : uaconfig.default_address)
        namespace: int =   Field(default_factory=lambda : uaconfig.namespace)
        node_name: str = ''
        method_name: str = ''
        class Config:
            extra = Extra.forbid        
    
    def __init__(self, config: Optional[Config] = None, **kwargs):        
        config = reconfig(self.Config, config, kwargs)
                    
        ua_client = opcua.Client( config.address)
        super().__init__(ua_client, 
            config.node_name, 
            config.method_name, 
           namespace = config.namespace
        )
        self._config = config
    
    @property
    def config(self):
        return self._config
        
    def disconnect(self):        
        self._ua_client.disconnect()    
        
class _UaCom:
    
    def __init__(self, ua_client: opcua.Client, prefix: str, namespace: int = uaconfig.namespace, sid: Optional[int] = None):
        self._ua_client = ua_client
        self._prefix = prefix 
        self._namespace = namespace
        self._sid = None
    
    @property
    def sid(self) -> tuple:        
        if not self._sid:
            u = self._ua_client.server_url
            self._sid = (u.hostname, u.port)
        return self._sid
    
    @property
    def prefix(self):
        return self._prefix    
    
    @property
    def namespace(self):
        return self._namespace
    
    def subcom(self, suffix,  namespace=None, dev_type=None):
        """ return a new UaCom object according to a new suffix 
        
        Args:
           suffix (str): the suffix is added to the object prefix to build a new prefix for the 
                         returned object
                        
                        ::
                        
                           UaCom(prefix="A").subcom("B").config.prefix == 'A.B'
            
            namespace (optional, int): if given change the namespace for the created com  
        """
        namespace = self._namespace if namespace is None else namespace
        return _UaCom(self._ua_client, kjoin(self._prefix, suffix), namespace=namespace, sid=self._sid)
    
    def nodecom(self, suffix, namespace=None):
        """ Return a :class:`_UaComNode` object dedicated for node communication 
        
        Args:
            suffix (str): node suffix added to com prefix 
            namespace (optional, int): if given change the namespace for the created node com  
            
        """
        namespace = self._namespace if namespace is None else namespace        
        return _UaComNode(        
          self._ua_client, 
          kjoin(self._prefix, suffix),
          namespace=namespace,
          sid= self.sid  
        )
    
    def rpccom(self, suffix: str, method: str, namespace=None):
        """ Return a :class:`_UaComRpcNode` object dedicated for rpc communication 
        
        Args:
            suffix (str): node suffix added to com prefix 
            method (str): RPC method name
            namespace (optional, int): if given change the namespace for the created rpc node com  

        """
        namespace = self._namespace if namespace is None else namespace        
        
        return _UaComRpcNode(
             self._ua_client, 
             kjoin(self._prefix, suffix),
             method,
             namespace=namespace,
             sid= self.sid 
            )

    def read_collector(self) -> UAReadCollector:
        """ Return a :class:`UAReadCollector` to collect nodes for reading node values on the server """
        return UAReadCollector(self._ua_client.uaclient)

    def write_collector(self) -> UAWriteCollector:
        """ Return a :class:`UAWriteCollector` to collect nodes for writing node values on the server """
        return UAWriteCollector(self._ua_client.uaclient)   
    
    def connect(self):
        return self._ua_client.connect()
    
    def disconnect(self):
        try:
            return self._ua_client.disconnect()
        except AttributeError:
            pass
        #raise ValueError("Cannot disconnect: not the owner of the UA client")    

    def is_connected(self) -> bool:
        """ True if the com is connected to the server """
        if self._ua_client.uaclient and self._ua_client.uaclient._uasocket:
            t = self._ua_client.uaclient._uasocket._thread
            return t and t.is_alive()
        return False
    
    @property
    def address(self):
        return self._ua_client.server_url.geturl()
    
class UaCom(_UaCom):
    """ This is a wrapper arround the :class:`opcua.Client`
    
    All objects,  :class:`pydevmgr.UaDevice`, :class:`pydevmgr.UaInterface`, ... will use 
    an :class:`UaCom` instance to communicate to OPCUA.
    :class:`pydevmgr.UaNode`  and :class:`pydevmgr.UaRpc` will use a :class:`UaComNode` instance.
    
    The idea is that one can replace this object by anything else to cover special needs. 
    E.g. to make a simulator for instance
    The simulator should define the same method as in UaCom and UaComNode 
    
    Args:
        address (optional, str): needed if `ua_client` is None
             server url address as e.g. "opc.tcp://192.168.1.11:4840"
        ua_client (optional, :class:`opcua.Client`): needed if address is None
            is this Client instead of creating one from the address 
         
        dev_type (str, optional): Not used but here to allow future simulation
    
    """    
    class Config(BaseModel):
        """ Config parameters for a UaCom object """
        namespace: int  = Field(default_factory=lambda : uaconfig.namespace)
        address: AnyUrl = Field(default_factory=lambda : uaconfig.default_address)
        prefix: str = ""
        class Config:
            extra = Extra.forbid 
        
    def __init__(self, 
          config: Optional[Config] = None,
          **kwargs
        ):
        
        config = reconfig(self.Config, config, kwargs)
        
        try:
            address = uaconfig.host_mapping[str(config.address)]
        except KeyError:
            address = str(config.address)
        
        ua_client = opcua.Client(address)
        super().__init__(ua_client, config.prefix, namespace=config.namespace)
        self._config = config
    
    @property
    def config(self):
        return self._config

    def reset(self):
        if self.is_connected():
            raise ValueError("Please disconnect before doing reset to kill thread background processes")
        self._ua_client.disconnect() # disconnect anyway to make sure everything is freed    
        config = self._config
        ua_client = opcua.Client(str(config.address))
        super().__init__(ua_client, config.prefix, config.prefix, namespace=config.namespace)    
        
    def disconnect(self):
        """ attempt to disconnect client """
        try:
            return self._ua_client.disconnect()
        except AttributeError:
            pass
           
    
def parse_com(com: Optional[Union[UaCom,opcua.Client,str]],
             config: BaseModel
        ) -> Union[UaCom,_UaCom]:
        if com is None:
            com = UaCom(config=config)            
        elif isinstance(com, (dict, BaseModel)):
            com = UaCom(config=com)
        elif isinstance(com, opcua.Client):
            com = _UaCom(com, '') 
        elif isinstance(com, str):
            com = UaCom(address=com)     
        return com

 



       

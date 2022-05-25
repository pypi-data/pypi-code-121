from .node import BaseNode, NodesReader, NodesWriter
from .base import kjoin, _BaseObject, new_key, path 
from typing import Union, List, Optional, Any, Dict, Callable
from pydantic import create_model, validator
from inspect import signature , _empty


class NodeAliasConfig(BaseNode.Config):
    type: str = "Alias"
    nodes: Optional[Union[List[Union[str, tuple]], str]] = None
    
 
class NodeAlias1Config(BaseNode.Config):
    type: str = "Alias1"
    node: Optional[Union[str,tuple]] = None
    


class NodeAliasProperty(BaseNode.Property):
    # redefine the node alias property to explicitly add the nodes argument
    def __init__(self, cls, constructor, name, nodes, *args, **kwargs):
        super().__init__( cls, constructor, name, *args, **kwargs)
        self._nodes = nodes
    
    def new(self, parent):
        config = self.get_config(parent)
        if self._name is None:
            name = new_key(config)
        else:
            name = self._name    
        obj = self._constructor(parent, name, self._nodes, *self._args, config=config, **self._kwargs)            
        self._finalise(parent, obj)
        return name, obj 



class BaseNodeAlias(BaseNode):
    _n_nodes_required = None
    _nodes_is_scalar = False
    def __init__(self, 
          key: Optional[str] = None, 
          nodes: Union[List[BaseNode], BaseNode] = None,
          config: Optional[BaseNode.Config] = None,
          **kwargs
         ):
         
        super().__init__(key, config=config, **kwargs)
        if nodes is None:
            nodes = []
        
        elif isinstance(nodes, BaseNode):
            nodes = [nodes]
            self._nodes_is_scalar = True
        if self._n_nodes_required is not None:
            if len(nodes)!=self._n_nodes_required:
                raise ValueError(f"{type(self)} needs {self._n_nodes_required} got {len(nodes)}")
        self._nodes = nodes
    
    @property
    def sid(self):
        """ sid of aliases must return None """ 
        return None
    
    @property
    def nodes(self):
        return self._nodes
    
    @classmethod
    def new(cls, parent, name, config=None, **kwargs):
        """ a base constructor for a NodeAlias within a parent context  
        
        The requirement for the parent :
            - a .key attribute 
            - attribute of the given name in the list shall return a node
        """
        config = cls.parse_config(config, **kwargs)
                                       
        nodes  = cls.new_target_nodes(parent, config) 
        
        return cls(kjoin(parent.key, name), nodes, config=config, localdata=parent.localdata)

    def get(self, data: Optional[Dict] =None) -> Any:
        """ get the node alias value from server or from data dictionary if given """
        if data is None:
            _n_data = {}
            NodesReader(self._nodes).read(_n_data)
            values = [_n_data[n] for n in self._nodes]
            #values = [n.get() for n in self._nodes]
        else:
            values = [data[n] for n in self._nodes]
        return self.fget(*values)
    
    def set(self, value: Any, data: Optional[Dict] =None) -> None:
        """ set the node alias value to server or to data dictionary if given """
        values = self.fset(value)
        if len(values)!=len(self._nodes):
            raise RuntimeError(f"fset method returned {len(values)} values while {len(self._nodes)} is on the node alias") 
        if data is None:
            NodesWriter(dict(zip(self._nodes, values))).write()                        
            #for n,v in zip(self._nodes, values):
            #    n.set(v)
        else:
            for n,v in zip(self._nodes, values):
                data[n] = v        
    
    def fget(self, *args) -> Any:
        # Process all input value (taken from Nodes) and return a computed value 
        return args 
    
    def fset(self, value) -> Any:
        # Process one argument and return new values for the aliased Nodes 
        raise NotImplementedError('fset')    



            
class NodeAlias(BaseNodeAlias):
    """ NodeAlias mimic a real client Node. 
        
    The NodeAlias object does a little bit of computation to return a value with its `get()` method and 
    thanks to required input nodes.
     
    The NodeAlias cannot be use as such without implementing a `fget` method. This can be done by 
    implementing the fget method on an inerated class or with the `nodealias` decorator. 
    
    NodeAlias is an abstraction layer, it does not do anything complex but allows uniformity among ways to retrieve values. 
    
    NodeAlias object can be easely created with the @nodealias() decorator
    
    ..note::
    
        :class:`pydevmgr_core.NodeAlias` can accept one or several input node from the unique ``nodes`` argument. 
        To remove any embiguity NodeAlias1 is iddentical but use only one node as input from the ``node`` argument.  
            


    Args:
        key (str): Key of the node
        nodes (list, class:`BaseNode`): list of nodes necessary for the alias node. When the 
                     node alias is used in a :class:`pydevmgr_core.Downloader` object, the Downloader will automaticaly fetch 
                     those required nodes from server (or other node aliases).
                     
    Example: 
    
    Using a dummy node as imput (for illustration purpose).
    
    

    ::
        
        from pydevmgr_core.nodes import Value 
        from pydevmgr_core import NodeAlias
        position = Value('position', value=10.3)
        
        is_in_position = NodeAlias( nodes=[position])
        is_in_position.fget =  lambda pos: abs(pos-4.56)<0.1
        is_in_position.get()
        # False
        
    
    Using the nodealias decorator

    ::

        from pydevmgr_core.nodes import Value 
        from pydevmgr_core import NodeAlias
        position = Value('position', value=10.3)
        
        @nodealias('is_in_position')
        def is_in_position(pos):
            return abs(pos-4.56)<0.1
 
    Derive the NodeAlias Class and add target position and precision  in configuration

    ::
 

        from pydevmgr_core.nodes import Value 
        from pydevmgr_core import NodeAlias
        position = Value('position', value=10.3)

        
        class InPosition(NodeAlias):
            class Config(NodeAlias.Config):
                target_position: float = 0.0 
                precision : float = 1.0 
            
            def fget(self, position):
                return abs( position - self.config.target_position) < self.config.precision 
        
        is_in_position = InPosition('is_in_position', nodes=[position],  target_position=4.56, precision=0.1)
        
        is_in_position.get()
        # False
        position.set(4.59)
        is_in_position.get()
        # True 
            
    NodeAlias can accept several nodes as input: 
    
    ::

        from pydevmgr_core.nodes import Value 
        from pydevmgr_core import NodeAlias
        
        class InsideCircle(NodeAlias):
            class Config(NodeAlias.Config):
                x: float = 0.0 
                y: float = 0.0
                radius: float = 1.0 
            
            def fget(self, x, y):
                return  ( (x-self.config.x)**2 + (y-self.config.y)**2 ) < self.config.radius**2
                
        position_x = Value('position_x', value=2.3)
        position_y = Value('position_y', value=1.4)
        is_in_target = InsideCircle( 'is_in_target', nodes=[position_x, position_y], x=2.0, y=1.0, radius=0.5 )
        is_in_target.get()
        # True


       
    .. seealso::  
        :func:`nodealias`
        :class:`NodeAlias1`            

    """
    Config = NodeAliasConfig
    Property = NodeAliasProperty
    
    
    
    @classmethod
    def prop(cls, name: Optional[str] = None, nodes=None, **kwargs):
        nodes = [] if nodes is None else nodes
        #config = cls.Config.parse_obj(kwargs)  
        config = cls.parse_config(kwargs)
        return cls.Property(cls, cls.new, name, nodes, config=config)
                
    @classmethod
    def new(cls, parent, name, nodes=None, config=None, **kwargs):
        """ a base constructor for a NodeAlias within a parent context  
        
        The requirement for the parent :
            - a .key attribute 
            - attribute of the given name in the list shall return a node
        """
        config = cls.parse_config(config, **kwargs)
        if nodes is None:
            if config.nodes is None:
                nodes = []
            else:
                nodes = config.nodes
        # nodes = config.nodes                
        # handle the nodes now
        #if nodes is None:
        #    raise ValueError("The Node alias does not have origin node defined, e.i. config.nodes = None")
        if isinstance(nodes, str):
            nodes = [nodes]
        elif hasattr(nodes, "__call__"):
            nodes = nodes(parent)
                                
        parsed_nodes  = [ cls._parse_node(parent, n, config) for n in path(nodes) ]
        
        return cls(kjoin(parent.key, name), parsed_nodes, config=config, localdata=parent.localdata)
    
    @classmethod
    def _parse_node(cls, parent: _BaseObject, in_node: Union[tuple,str,BaseNode], config: Config) -> 'NodeAlias':
        if isinstance(in_node, BaseNode):
            return in_node
        
        
        if isinstance(in_node, str):
            try:
                node = getattr(parent, in_node)
            except AttributeError:
                raise ValueError(f"The node named {in_node!r} does not exists in parent {parent}")
            else: 
                if not isinstance(node, BaseNode):
                    raise ValueError(f"Attribute {in_node!r} of parent is not node got a {node}")
                return node      
        
        if isinstance(in_node, tuple):
            cparent = parent
            for sn in in_node[:-1]:
                cparent = getattr(cparent, sn)
            
            name  = in_node[-1]
            try:
                node = getattr(cparent, name)
            except AttributeError:
                 raise ValueError(f"Attribute {name!r} does not exists in  parent {cparent}")
            else:
                if not isinstance(node, BaseNode):
                    raise ValueError(f"Attribute {in_node!r} of parent is not a node got a {type(node)}")
                return node

        
        raise ValueError('node shall be a parent attribute name, a tuple or a BaseNode got a {}'.format(type(in_node)))         
        
    def fget(self, *args) -> Any:
        """ Process all input value (taken from Nodes) and return a computed value """
        raise NotImplementedError("fget")

class BaseNodeAlias1(BaseNode):
    """ BaseNodeAlias1 base classed  
    
    The ``_new_source_node(cls, parent, config)`` class method shall be implemented to this base node in order to 
    retrieve the source node from the context of a parent object. 

    Example:

    ::

        from pydevmgr_core import BaseInterface, BaseNodeAlias1
        from pydevmgr_core.nodes import Value 
        
        class AiNode(BaseNodeAlias1, ai_number=(int,0)):
            @classmethod
            def _new_source_node(cls, parent, config):
                return getattr(parent, f"ai_{config.ai_number}")

        VC = Value.Config 
        class MyInterface(BaseInterface):
            class Config(BaseInterface.Config):
                ai_0: VC = VC(value=1.0)
                ai_1: VC = VC(value=2.0)
                ai_3: VC = VC(value=3.0)
                # etc ... 
                
                temperature : AiNode.Config = AiNode.Config(ai_number=1)

        my_interface = MyInterface()
        my_interface.temperature.get()
        # -> 2.0
                
    """
    # This class does not implement the engine to get the source node from a parent object 
    # one has to implement the _new_source_node(cls, parent, config) class method 
    
    def __init__(self, 
          key: Optional[str] = None, 
          node: Optional[BaseNode] = None,
          config: Optional[BaseNode.Config] = None, 
          localdata: Optional[dict] = None, 
          **kwargs
         ):        
        super().__init__(key, config=config, localdata=localdata, **kwargs)    
        if node is None:            
            raise ValueError("the node pointer is empty, alias node cannot work without")    
                    
        self._node = node
    
    @property
    def sid(self):
        """ sid of aliases must return None """ 
        return None
    
    @property
    def node(self):
        return self._node
    
    # nodes property is mendatory for the NodeReader 
    @property
    def nodes(self):
        return [self._node]
    
    
    @classmethod
    def new(cls, parent, name, config=None, **kwargs):
        """ a base constructor for a NodeAlias within a parent context  
        
        The requirement for the parent :
            - a .key attribute 
            - attribute of the given name in the list shall return a node
        """
        config = cls.parse_config(config, **kwargs)
                             
        parsed_node  = cls._new_source_node(parent, config)    
        
        return cls(kjoin(parent.key, name), parsed_node, config=config, localdata=parent.localdata)
    
    @classmethod
    def _new_source_node(cls, parent, config):
        raise NotImplementedError('new_target_node')
    
    
    
    def get(self, data: Optional[Dict] =None) -> Any:
        """ get the node alias value from server or from data dictionary if given """
        if data is None:
            _n_data = {}
            NodesReader([self._node]).read(_n_data)
            value = _n_data[self._node]
        else:
            value = data[self._node]
        return self.fget(value)    
        
    def set(self, value: Any, data: Optional[Dict] =None) -> None:
        """ set the node alias value to server or to data dictionary if given """
        value = self.fset(value)
        if data is None:
            NodesWriter({self._node:value}).write()                        
        else:
            data[self._node] = value
    
    def fget(self,value) -> Any:
        """ Process the input retrieved value and return a new computed on """
        return value
    
    def fset(self, value) -> Any:
        """ Process the value intended to be set """
        return value



class NodeAlias1(BaseNodeAlias1):
    """ A Node Alias accepting one source node 
    
    By default this NodeAlias will return the source node. 
    One have to implement the fget and fset methods to custom behavior. 

    Example:
    
    ::
        
        from pydevmgr_core import NodeAlias1
        from pydevmgr_core.nodes import Value
             
        class Scaler(NodeAlias1, scale=(float, 1.0)):
            def fget(self, value):
                return value* self.config.scale
            def fset(self, value):
                return value/self.config.scale 
    
        raw = Value('raw_value', value=10.2)
        scaled = Scaler('scaled_value', node = raw, scale=10)
        scaled.get()
        # -> 102
        scaled.set( 134)
        raw.get()
        # -> 13.4

    """
    Config = NodeAlias1Config
    Property = NodeAliasProperty
    
       
       
    @classmethod
    def prop(cls, 
          name: Optional[str] = None, 
          node: Union[BaseNode,str] = None,  
          **kwargs
        ) -> NodeAliasProperty:
        # config = cls.Config.parse_obj(kwargs)
        config = cls.parse_config(kwargs)
        return cls.Property(cls, cls.new, name, node, config=config)
    
    @classmethod
    def new(cls, parent, name, node=None,  config=None, **kwargs):
        """ a base constructor for a NodeAlias within a parent context  
        
        The requirement for the parent :
            - a .key attribute 
            - attribute of the given name in the list shall return a node
        """
        config = cls.parse_config(config, **kwargs)
        if node is None:            
            node = config.node 
        if node is None:
            raise ValueError("node origin pointer is not defined")                             
        parsed_node  = NodeAlias._parse_node(parent, path(node), config)    
        
        return cls(kjoin(parent.key, name), parsed_node, config=config, localdata=parent.localdata)
    

def nodealias(key: Optional[str] =None, nodes: Optional[list] = None):
    """ This is a node alias decorator 
    
    This allow to quickly embed any function in a node without having to subclass the Alias Node
    
    The build node will be readonly, for a more complex behavior please subclass a NodeAlias
    
    Args:
        key (str): string key of the node
        nodes (lst): list of nodes 
        
    Returns:
       func_setter: a decorator for the fget method  
       
    Example:
    
    A simulator of value:
    
    ::
        from pydevmgr_core import node, nodealias 
        
        # To be replaced by real stuff of course
        @node('temperature')
        def temperature():
            return np.random.random()*3 + 20
        @node('motor_pos')
        def motor_pos():
            return np.random.random()*100
        
        # the nodealias focus is computed from temperature and motor position 
        @nodealias('focus', [temperature, motor_pos]):
        def focus(temp, pos):
            return pos+ 0.45*temp + 23.
            
    In the example above when doing `focus.get()` it will automaticaly fetch the `temperature` and
    `motor_pos` nodes.  
        
    """
    node = NodeAlias(key,nodes)
    def set_fget(func):
        node.fget = func
        if hasattr(func, "__func__"):
            node.__doc__= func.__func__.__doc__
        else:
            node.__doc__ = func.__doc__
        return node
    return set_fget



def nodealias1(key: Optional[str] = None, node: Optional[BaseNode] = None) -> Callable:
    """ This is a node alias decorator 
    
    This allow to quickly embed any function in a node without having to subclass the Alias Node
    This is the counterpart of :func:`nodealias` except that it explicitely accept only one node
    as input instead of severals
    
    The build node will be readonly, for a more complex behavior please subclass a NodeAlias
    
    Args:
        key (str, optional): string key of the node
        node (:class:`BaseNode`): input node. This is not optional and shall be defined 
                                  It is however after key for historical reason 
        
    Returns:
       func_setter: a decorator for the fget method  
       
    Example:
    
    A simulator of value:
    
    ::
        
        from pydevmgr_core import nodealias1, node 
        import numpy as np 
        
        @node('temperature_volt')
        def temperature_volt():
            return np.random.random()*3 + 20
        
        @nodealias1('temperature_celcius', temperature_volt):
        def temperature_celcius(temp_volt):
            return temp_volt*12.3 + 2.3
            
    """
    node = NodeAlias1(key,node)
    def set_fget(func):
        node.fget = func
        if hasattr(func, "__func__"):
            node.__doc__= func.__func__.__doc__
        else:
            node.__doc__ = func.__doc__
        return node
    return set_fget

def to_nodealias_class(_func_: Callable =None, *, type: Optional[str] = None):
    if _func_ is None:
        def node_func_decorator(func):
            return _nodealias_func(func, type)
        return node_func_decorator
    else:
        return _nodealias_func(_func_, type)
    
    
def _nodealias_func(func, type_):
    if not hasattr(func, "__call__"):
        raise ValueError(f"{func} is not callable")
    
    try:    
        s = signature(func)
    except ValueError: # assume it is a builtin class with one argument 
        conf_args = {}
        obj_args = []
        
    else:
        
        conf_args = {}
        obj_args = []
        poasarg = 0
        for a,p in s.parameters.items():
            if p.default == _empty:
                if a in ['com', 'localdata', 'key', 'nodes']:
                    if poasarg:
                        raise ValueError("Pos arguments must be after or one of 'com', 'localdata' or 'key'")
                    obj_args.append(a)
                else:
                    poasarg += 1        
            else:                
                if p.annotation == _empty:
                    conf_args[a] = p.default 
                else:
                    conf_args[a] = (p.annotation,p.default)
                    
    extras = {}
    if type_ is None:        
        if  "type" in conf_args:
            type_  = conf_args['type']            
        else:
            type_ = func.__name__
            extras['type'] = type_
    else:
        extras['type'] = type_
        
          
                
    Config = create_model(type_+"Config", **extras, **conf_args, __base__=NodeAlias.Config)
        
    if conf_args or obj_args: 
        conf_args_set = set(conf_args)        
                
        if obj_args:        
            def fget_method(self, *args):
                c = self.config
                return func(*[getattr(self,__a__) for __a__ in obj_args], *args, **{a:getattr(c,a) for a in conf_args_set})
        else:
            def fget_method(self, *args): 
                c = self.config           
                return func(*args, **{a:getattr(c,a) for a in conf_args_set})        
            
    else:
        def fget_method(self, *args):
            return func(*args)
    try:
        doc = func.__doc__
    except AttributeError:
        doc = None
                   
    return type(type_+"NodeAlias", 
                (NodeAlias,), 
                {'Config':Config, 'fget': fget_method, '__doc__':doc, '_n_nodes_required': poasarg}
               )
    



    


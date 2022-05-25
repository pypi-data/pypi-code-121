from .class_recorder import  KINDS
from .base import (_BaseObject, _BaseProperty)
                           

from typing import Dict, List, Callable, Union , Optional, Type
from pydantic import create_model
from .parser_engine import parser, AnyParserConfig
from inspect import signature , _empty
from enum import Enum 
import weakref



# used to force kind to be a rpc 
class RPCKIND(str, Enum):
    RPC = KINDS.RPC.value


class BaseRpcConfig(_BaseObject.Config):
    kind: RPCKIND = RPCKIND.RPC
    type: str = ""
    
    arg_parsers: Optional[List[Union[AnyParserConfig, List[Union[str, Callable]], str, Callable]]] = []
    kwarg_parsers: Optional[Dict[str,Union[AnyParserConfig, List[Union[str, Callable]], str, Callable]]] = {}
   


class BaseCallCollector:
    """ The Read Collector shall collect all nodes having the same sid and read them in one call
    
    - __init__ : should not take any argument 
    - add : take one argument, the Node. Should add node in the read queue 
    - read : takes a dictionary as arguement, read the nodes and feed the data according to node keys 
    
    The BaseReadCollector is just a dummy implementation where nodes are red one after the other     
    """
    def __init__(self):
        self._rpcs = []
    
    def add(self, rpc, args, kwargs):
        self._rpcs.append((rpc, args, kwargs))
        
    def call(self):        
        for rpc, args, kwargs in self._rpcs:
            rpc.rcall(*args, **kwargs)
                
class RpcError(RuntimeError):
    """ Raised when an rpc method is returning somethingelse than 0

        See rcall method of RpcNode
    """
    rpc_error = 0

class RpcProperty(_BaseProperty):    
    fcall = None
    
    def caller(self, func):
        """ decoraotr to define the fcall function """
        self.fcall = func
        return self # must return self
    
 
    def _finalise(self, parent, rpc):
        if self.fcall:
            parent_wr = weakref.ref(parent)
            def fcall(*args, **kwargs):
                return self.fcall(parent_wr(), *args, **kwargs)
            rpc.fcall = fcall
    
    def __call__(self, func):
        """ The call is used has fcall decorator """
        self.fcall = func
        return self



class BaseRpc(_BaseObject):
    
    Config = BaseRpcConfig
    Property = RpcProperty
    
    _arg_parsers = None
    _kwarg_parsers = None
    def __init__(self, 
           key: Optional[str] = None, 
           config: Optional[Config] =None, 
           **kwargs
        ) -> None:  
        super().__init__(key, config=config, **kwargs)
        
        if self.config.arg_parsers:
            _arg_parsers = []
            for i,p in enumerate(self.config.arg_parsers):                
                _arg_parsers.append(parser(p)) 
                self.config.arg_parsers[i] = _arg_parsers[i].config
            self._arg_parsers = _arg_parsers
        if self.config.kwarg_parsers:
            _kwarg_parsers = {}
            for k,p in self.config.kwarg_parsers.items():
                _kwarg_parsers[k] = parser(p)
                self.config.kwarg_parsers[k] = _kwarg_parsers[k].config    
            self._kwarg_parsers  = _kwarg_parsers


    @property
    def sid(self):
        """ default id server is 0 
        
        The sid property shall be adujsted is the CallCollector
        """
        return 0
    
    
    def get_error_txt(self, rpc_error):
        """ Return Error text from an rpc_error code """
        return "Not Registered Error"
    
    def call_collector(self):
        """ Return a collector for method call """
        return BaseCallCollector()
    
    def parse_args(self, args, kwargs):
        """ Modify in place a list of args and kwargs thans to the defined arg_parsers and kwarg_parsers """
        if self._arg_parsers:
            for i,(p,a) in enumerate(zip(self._arg_parsers, args)):
                args[i] = p(a) 
        if self._kwarg_parsers:
            for k,a in kwargs.items():
                try:
                    p = self._kwarg_parsers[k]
                except KeyError:
                    pass
                else:
                    kwargs[k] = p(a)
                
    def call(self, *args, **kwargs):
        """ Call the method and return what return the server 
        
        this will mostly return an integer which shall be 0 if success
        
        .. seealso::
        
           :func:`BaseRpc.rcall` method
          
        """
        args = list(args)
        self.parse_args(args, kwargs)
        return self.fcall(*args, **kwargs)
    
    def rcall(self, *args, **kwargs):
        """ Call the Rpc Method but raised an exception in case of an error code is returned """
        e = self.get_error(self.call(*args, **kwargs))
        if e:
            raise e
    
    def get_error(self, rpc_return):
        if rpc_return:
            e = RpcError("RPC ({}): {}".format(rpc_return, self.get_error_txt(rpc_return)))
            e.rpc_error = rpc_return
            return e
    
    def fcall(self, *args, **kwargs):
        raise NotImplementedError('fcall')
        

def rpcproperty(name, *args, **kwargs):
    """ A decorator for a quick rpc creation 
    
    This shall be implemented in a parent interface or any class 
    
    Args:
        cls (class, optional): default is :class:`BaseRpc` used to build the rpc  
        **kwargs: All other arguments necessary for the node construction
    """
    return BaseRpc.prop(name, *args, **kwargs)


def to_rpc_class(_func_: Callable = None, *, type: Optional[str] = None) -> Type[BaseRpc]:
    """ Create a Rpc Class from a function 
    
    This is a conveniant function to quickly create a Rpc Class. 
    As this is a lazy and durty implementation they are some naming convention to respect for the 
    function arguments. 
    The function can have the signature : 
    
    - `f(arg1, arg2, ..., key1=val1, key2=val2, ...)`
    
    Eventualy before the args 1 to 3 positional arguments can be named key, com and localdata 
    
    - `f(key, arg1, arg2, ..., key1=val1, key2=val2, ...)`
    - `f(key, com, arg1, arg2, ..., key1=val1, key2=val2, ...)`
    - `f(com, localdata, key, arg1, arg2, ..., key1=val1, key2=val2, ...)`
    - etc ...
    
    At call, com, localdata and key will be replaced by the corresponding Rpc instance attribute other
    positional argument are parsed to the function. 
    The keyowrd become parameters of the Config class 
    
    The to_rpc_class can be used as decorator or function 
    
    Example:
    
        >>> from pydevmgr_core import to_rpc_class
        >>> @to_rpc_class
        >>> def Echo(key, value, end: str = "\n"):
        >>>     print( key, "is called with value", value,  end=end)
      
        >>> Echo.Config()    
        EchoConfig(kind=<KINDS.RPC: 'Rpc'>, type='Echo', arg_parsers=None, kwarg_parsers=None, arg_parsers_config=[], kwarg_parsers_config={}, com=None, end='\n')
        
        >>> echo = Echo('echo!!', end="||\n")
        >>> echo.call(100)
        echo!! is called with value 100||
        >>> echo.config.end = "*********\n"
        >>> echo.call(100)
        echo!! is called with value 100*********
    
    The above class creation is equivalent of doing
    
    ::
    
       class Echo(BaseRpc):
            class Config(BaseRpc.Config):
                end: str = "\n"
            def fcall(self, value):
                print( self.key, "is called with value", value,  end=self.config.end)
    
    The penalty of the durty class creation is not so big: 1.5 to 2 times slower for the call 
    process only. Probably that what is inside the function will dominate the execution time anyway  
    """
    if _func_ is None:
        def rpc_func_decorator(func):
            return _rpc_func(func, type)
        return rpc_func_decorator
    else:
        return _rpc_func(_func_, type)
    
def _rpc_func(func, type_):
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
        poasarg = False
        for a,p in s.parameters.items():
            if p.default == _empty:
                if a in ['com', 'localdata', 'key']:
                    if poasarg:
                        raise ValueError("Pos arguments must be after or one of 'com', 'localdata' or 'key'")
                    obj_args.append(a)
                else:
                    poasarg = True        
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
        
    Config = create_model(type_+"Config", **extras, **conf_args, __base__=BaseRpc.Config)
        
    if conf_args or obj_args: 
        conf_args_set = set(conf_args)        
        
        if obj_args:        
            def fcall_method(self, *args):
                c = self.config
                return func(*[getattr(self,__a__) for __a__ in obj_args], *args, **{a:getattr(c,a) for a in conf_args_set})
        else:
            def fcall_method(self, *args):   
                c = self.config         
                return func(*args, **{a:getattr(c,a) for a in conf_args_set})        
            
    else:
        def fcall_method(self, *args):
            return func(*args)
    try:
        doc = func.__doc__
    except AttributeError:
        doc = None           
    return type(type_+"Rpc", (BaseRpc,), {'Config':Config, 'fcall': fcall_method, '__doc__':doc})
    




        

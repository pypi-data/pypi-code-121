from enum import Enum
from typing import Union, List, Optional, Type, Callable
class KINDS(str, Enum):
    PARSER = "Parser"
    NODE = "Node"
    RPC = "Rpc"
    DEVICE = "Device"
    INTERFACE = "Interface"
    MANAGER = "Manager"


class Parsers:
    pass
class Nodes:
    pass
class Rpcs:
    pass
class Devices:
    pass
class Interfaces:
    pass
class Managers:
    pass


object_loockup = {}
def get_class(kind: KINDS, type_: str, default=None) -> Type:
    try:
        return object_loockup[(kind, type_)]
    except KeyError:
        if default is None:
            raise ValueError(f"Unknown {kind!r} of type {type_!r}")
        else:
            return default

def record_class(
         _cls_: Type =None, *, 
         overwrite: Optional[bool] = False, 
         type: Optional[str] =None, 
         kind: Optional[Union[KINDS,str]] =None
     ) -> Callable:
    """ record a new class by its kind and type 
    
    This can be used as decorator or function 
    """   
    if _cls_ is None:
        def obj_decorator(cls) -> Type:
            return record_class(cls, overwrite=overwrite, type=type, kind=kind)
        return obj_decorator
    else:
        cls = _cls_
    try:
        C = cls.Config
    except AttributeError:
        raise ValueError("Recorded class must have a Config class defined as attribute")
    
    if kind is None:        
        try:
            kind_field = C.__fields__['kind']    
        except (KeyError, AttributeError):
            raise ValueError("Config is missing 'kind' attribute or is not a BaseModel")
        else:
            kind = kind_field.default  
    
             
    if type is None:
        try:
            type_field = C.__fields__['type']    
        except (KeyError, AttributeError):
            raise ValueError("Config is missing 'type' attribute")
        else:
            type = type_field.default
            
    _record_class_as(kind_field.default, type, cls, overwrite=overwrite)
    return cls

def _record_class_as(kind, type, cls, overwrite=False):
    if not hasattr(cls, "Config"):
        raise ValueError("recorded class must have a Config attribute")
    try:
        recorded_cls = object_loockup[(kind, type)]
    except KeyError:
        pass
    else:
        if cls is recorded_cls:
            return
        if not overwrite:
            raise ValueError(f"{kind} {type} object is already recorded, use overwrite keyword to replace")
    
    object_loockup[(kind, type)] = cls

    if kind == KINDS.PARSER:
        setattr(Parsers, type, cls)
    elif kind == KINDS.NODE:
        setattr(Nodes, type, cls)
    elif kind == KINDS.RPC:
        setattr(Rpcs, type, cls)
    elif kind == KINDS.INTERFACE:
        setattr(Interfaces, type, cls)    
    elif kind == KINDS.DEVICE:
        setattr(Devices, type, cls)
    elif kind == KINDS.MANAGER:
        setattr(Managers, type, cls)
    

def list_classes(kind: Optional[KINDS] = None)-> Union[List[tuple],List[str]]:
    """ list all class names recorded class accessible with :func:`get_class` 
    
    Args:
        kind (str, KINDS, optional) :  If None the returned list is a list of (kind,type) tuple 
                                      Otherwise it musb a valid KINDS and the return list is a list 
                                      of type name 
    Return:
        classe_names (list):  list of tuple if kind=None or list of str if kind is given 
    """
    if kind is None:
        return list(object_loockup)
    else:
        return [t for k,t in object_loockup if k==kind]
            

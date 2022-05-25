from pydantic import BaseModel, ValidationError, Field
from pydantic.fields import ModelField
from .download import download, BaseDataLink, reset
from .upload import upload
from .node import BaseNode
from .model_var import NodeVar, NodeVar_R, NodeVar_W, NodeVar_RW, StaticVar
from .base import BaseData, path as to_path 

from typing import  Any, Iterable, Dict, List, Type

class C:
    ATTR = 'attr'
    ITEM = 'item'
    NODE = 'node'
    PATH = 'path'

class MatchError(ValueError):
    ...

def _extract_static(obj, name, field):        
    if C.ATTR in field.field_info.extra:
        if field.field_info.extra.get(C.ITEM, None) is not None:
            raise ValueError(f'{C.ATTR!r} and {C.ITEM!r} cannot be both set, choose one.')                    
        
        attribute = field.field_info.extra[C.ATTR]
        if attribute:
            try:
                val = getattr(obj, attribute)
            except AttributeError:
                raise MatchError(f'{attribute!r} is not an attribute of {obj.__class__.__name__!r}')
        else:
            val = obj
    
    elif C.ITEM in field.field_info.extra:             
        item = field.field_info.extra[C.ITEM]
        try:
            val = obj[item]
        except KeyError:
            raise MatchError(f'{item!r} is not an item of {obj.__class__.__name__!r}')
    else:
        try:
            val = getattr(obj, name)
        except AttributeError:
            raise MatchError(f'{name!r} is not an attribute of {obj.__class__.__name__!r}')        
    
    return val
        
def _extract_node(obj, name, field):
    """ called when a NodeVar is detected in datamodel """
    
    if C.NODE in field.field_info.extra:
        
        node = field.field_info.extra[C.NODE]
        node = to_path(node)    
        if field.field_info.extra.get(C.ATTR, None) is not None:
            raise MatchError(f'node={C.NODE!r} and attr={C.ATTR!r} cannot be both set, choose one.')
        
        if field.field_info.extra.get(C.PATH, None) is not None:
            raise MatchError(f'node={C.NODE!r} and path={C.PATH!r} cannot be both set, choose one.')
        
        if field.field_info.extra.get(C.ITEM, None) is not None:
            raise MatchError(f'node={C.NODE!r} and item={C.ITEM!r} cannot be both set, choose one.')
                                        
        if isinstance(node, BaseNode.Property):
            _, node = node.new(obj)
        elif isinstance(node, str):
            try:
                attr = node
                node = getattr(obj, attr)
            except AttributeError:
                raise MatchError(f'{attr!r} is not a node in {obj.__class__.__name__!r}')
        elif hasattr(node, "__iter__"):
            
            attr = node
            cobj = obj
            path = tuple(attr)
            for a in path[:-1]:
                cobj = getattr(cobj, a)
            try:
                node = getattr(cobj, path[-1])
            except AttributeError:
                raise MatchError(f'{path[-1]!r} is not a node in {obj.__class__.__name__!r} with path {path}')        
        elif not isinstance(node, BaseNode):
            raise MatchError(f'node set in the field is not a node')
    
    elif C.ATTR in field.field_info.extra:
        if field.field_info.extra.get(C.ITEM, None) is not None:
            raise MatchError(f'attr={C.ATTR!r} and item={C.ITEM!r} cannot be both set, choose one.')
        if field.field_info.extra.get(C.PATH, None) is not None:
            raise MatchError(f'attr={C.ATTR!r} and path={C.PATH!r} cannot be both set, choose one.') 
            
        attr = field.field_info.extra[C.ATTR]  
        if attr:            
            try:
                node = getattr(obj, attr)
            except AttributeError:
                raise MatchError(f'{attr!r} is not a node in {obj.__class__.__name__!r}')
        else:
            node = obj        
            
    elif C.PATH in field.field_info.extra:
        if field.field_info.extra.get(C.ITEM, None) is not None:
            raise MatchError(f'path={C.PATH!r} and item={C.ITEM!r} cannot be both set, choose one.')
             
        path = field.field_info.extra[C.PATH]
        path = to_path(path)    
        if path:
            
            if isinstance(path, str):
                path = path.split('.')                
            elif not hasattr(path, "__iter__"):
                raise MatchError(f"expecting string or iterable for path parameter got {path!r}")
                
            cobj = obj
            path = tuple(path)
            try:
                for a in path[:-1]:
                    cobj = getattr(cobj, a)
                node = getattr(cobj, path[-1])
            except AttributeError:
                raise MatchError(f'{path!r} is not a valid in {obj.__class__.__name__!r} with path {path}')                                    
        else:
            node = obj
             
        if not isinstance(node, BaseNode):
            raise MatchError(f'node attribute  {attr!r} is not a node in {obj.__class__.__name__!r}')
    
    elif C.ITEM in field.field_info.extra:
         
        item = field.field_info.extra[C.ITEM]
        try:
            node = obj[item]
        except (KeyError, TypeError):
            raise MatchError(f'{item!r} is not an item in {obj.__class__.__name__!r}')
                             
        if not isinstance(node, BaseNode):
            raise MatchError(f'node item {item!r} is not a node in {obj.__class__.__name__!r}')    
                                            
    else:
        attr = name
        try:
            node = getattr(obj, attr)
        except AttributeError as e:
            raise MatchError(f'{attr!r} is not a node in {obj.__class__.__name__!r}')         
        if not isinstance(node, BaseNode):
            raise MatchError(f'node attribute {attr!r} is not a node in {obj.__class__.__name__!r}')
         
    return node                                
    
class DataLink(BaseDataLink):
    """ Link an object containing nodes, to a :class:`pydantic.BaseModel` 
    
    Args:
        input (Any):  Any object with attributes, expecting that the input contains some 
                      :class:`BaseNode` attributes in its hierarchy
                         
        model (:class:`pydantic.BaseModel`): a data model. Is expecting that the data model structure 
            contains :class:`NodeVar` type hint signature.
            
    Example: 
    
        In the following, it is assumed that the motor1 object has a .stat attribute and the .stat
        object have nodes as `pos_actual`, `vel_actual`, etc ... 
        
        ::
        
            from pydevmgr_core import NodeVar, DataLink
            from pydevmgr_core.nodes import UtcTime
            from pydantic import BaseModel, Field
            
            class MotorStatData(BaseModel):
                # the following nodes will be retrieve from the input object, the name here is the 
                # the attribute of the input object                
                pos_actual:  NodeVar[float] = 0.0  
                vel_actual:  NodeVar[float] = 0.0  
                
                
                
                # also the input object attribute pointing to a node can be changed 
                # with the no de keyword in Field (from pydantic import Field)
                pos: NodeVar[float] = Field(0.0, node='pos_actual')
                vel: NodeVar[float] = Field(0.0, node='vel_actual')
                 
                
            class MotorData(BaseModel):    
                num  : int =1 # other data which are not node related                
                
                # Add the stat Data Model 
                stat : MotorStatData = MotorStatData()
                
                # This node is standalone, not linked to input object, 
                # it must be specified in Field with the node keyword 
                utc:         NodeVar[str]   = Field('1950-01-01T00:00:00.00000', node=UtcTime('utc'))
                
                
            >>> data = MotorData()
            >>> data.stat.pos
            0.0
            >>> link = DataLink( motor1, data )
            >>> link.download() # download node values inside data from tins.motor1
            >>> data.stat.pos
            4.566   
            >>> data.utc
            '2020-12-17T10:05:15.831726'
            
        :class:`DataLink` can be added to a :class:`Downloader`, at init or with the :meth:`Dwonloader.add_datalink` method
        
        ::
        
            from pydevmgr_core import Downloader
            
            >>> downloader = Downloader(link)
            >>> downloader.download()
            
            # Or
            
            >>> connection = downloader.new_connection()
            >>> connection.add_datalink(link)                        
            
    """
    def __init__(self, 
          input : Any, 
          model : BaseModel, 
          strick_match : bool = True 
        ) -> None:
        
        self._rnode_fields = {}
        self._wnode_fields = {}
        if isinstance(input, BaseNode):
            try:
                model.value 
            except AttributeError:
                raise ValueError("To link a Node, the data model must have the 'value' attribute")
            self._collect_single_node(model, input)
            self._rnode_fields[input] = [('value', model)]
            self._wnode_fields[input] = [('value', model)]
            
        else:
            self._collect_nodes(model, input, strick_match)
        self._input = input 
        self._model = model
    
    @property
    def model(self)-> BaseModel:
        return self._model    
    
    @property
    def input(self)-> Any:
        return self._input
    
    @property
    def rnodes(self)-> Iterable:
        return self._rnode_fields
    
    @property
    def wnodes(self)-> Iterable:
        return self._wnode_fields
    
    def _collect_single_node(self, model, input_obj):
        for name, field in model.__fields__.items():
            if not isinstance(field.type_, type):
                continue            
            if issubclass(field.type_, StaticVar):
                val = _extract_static(input_obj, name, field)
                setattr(model, name, val) 
            elif issubclass(field.type_, (NodeVar_R,NodeVar,NodeVar_W, NodeVar_RW)):
                raise ValueError("Linking a single node. Data model should not contain NodeVar fields")
    
    def _collect_nodes(self, model, input_obj, strick_match):
        for name, field in model.__fields__.items():
            if not isinstance(field.type_, type):
                continue        
            if issubclass(field.type_, StaticVar):
                try:
                    val = _extract_static(input_obj, name, field)
                except MatchError as e:
                    if strick_match: raise e
                else:    
                    setattr(model, name, val)
                    
            elif issubclass(field.type_, (NodeVar_R,)):
                try:
                    node = _extract_node(input_obj, name, field)               
                except MatchError as e:
                    if strick_match: raise e
                else:
                    self._rnode_fields.setdefault(node, []).append((name, model))
            
            elif issubclass(field.type_, (NodeVar, NodeVar_RW)):
                try:
                    node = _extract_node(input_obj, name, field)               
                except MatchError as e:
                    if strick_match: raise e
                else:
                    
                    self._rnode_fields.setdefault(node, []).append((name, model))
                    self._wnode_fields.setdefault(node, []).append((name, model))
                       
            elif issubclass(field.type_, (NodeVar_W, )):
                try:
                    node = _extract_node(input_obj, name, field)
                except MatchError as e:
                    if strick_match: raise e
                else:                  
                    self._wnode_fields.setdefault(node, []).append((name, model))   
                
            elif issubclass(field.type_, BaseModel):
                # chidren is ignored if path is broken
                sub_model = getattr(model, name)
                if not isinstance(sub_model, BaseModel):                
                    continue
                
                                                    
                try:
                    sub_obj = _extract_static(input_obj, name, field)
                except MatchError as e:
                    # if BaseData force the existance of the path 
                    if strick_match and issubclass(field.type_, BaseData):
                        raise e
                else:                    
                    self._collect_nodes( sub_model, sub_obj, strick_match)
    
    def download_from_nodes(self, nodevals: Dict[BaseNode,Any]) -> None:
        """ Update the data from a dictionary of node/value pair 
        
        If a node in the dictionary is currently not part of the data model link it is ignored silently 
        """
        for node, val in nodevals.items():
            try:
                lst = self._rnode_fields[node]
            except KeyError:
                pass
            else:
                for attr, obj in lst:
                    setattr(obj, attr, val)
                    
    def _download_from(self, data: dict) -> None:
        for node, lst in self._rnode_fields.items():
            for attr, obj in lst:
                setattr(obj, attr, data[node])
                
    def download(self) -> None:
        """ download Nodes from servers and update the data """
        data = {}
        download( self._rnode_fields, data )
        self._download_from(data)
    
    def reset(self):
        """ All linked nodes with a reset method will be reseted """   
        reset(self._rnode_fields)
        reset(self._wnode_fields)         
                
    def _upload_to(self, todata: dict) -> None:
        for node, lst in self._wnode_fields.items():    
            for attr, obj in lst:
                val = getattr(obj, attr)
                if isinstance(val, BaseNode):
                    continue
                # the last in the list will be set
                # which may not in a hierarchical order 
                # any way several same w-node should be avoided
                todata[node] = val  
                        
    def upload(self) -> None:
        """ upload data value (the one linked to a node) to the server """
        todata = {}
        self._upload_to(todata)
        upload(todata) 

def model_subset(
       class_name: str, 
       Model: Type[BaseModel], 
       fields: List[str], 
       BaseClasses: tuple =(BaseModel,)
    ) -> Type[BaseModel]:
    """ From a pydantic model class create a new model class with a subset of fields 
    
    Args:
        class_name (str): name of the create class model 
        Model (BaseModel): Model root 
        fields (List[str]): list of Model field names 
        BaseClasses (optional, tuple): base classes of the new class default is (BaseModel,)
    """
    annotations = {}
    new_fields = {}
    for field_name in fields:
        field = Model.__fields__[field_name]
        fi = field.field_info
        kwargs = dict(            
            description = fi.description, 
            ge=fi.ge, 
            gt=fi.gt, 
            le=fi.le, 
            lt=fi.lt,
            max_items=fi.max_items, 
            max_length=fi.max_length, 
            min_items=fi.min_items, 
            min_length=fi.min_length, 
            multiple_of=fi.multiple_of, 
            title=fi.title,         
        )
        kwargs.update(fi.extra)
                
        new_field = Field(fi.default, **kwargs)
        annotations[field.name] = field.type_ 
        new_fields[field.name] = new_field
        
    new_class = type(class_name, BaseClasses, new_fields)  
    new_class.__annotations__ = annotations
    return new_class

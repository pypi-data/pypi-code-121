from typing import Any, Optional, Type, Callable, Union, Iterable, List, Generic, TypeVar
from pydantic import BaseModel , create_model, Extra, validator, ValidationError

from pydantic.fields import ModelField
from inspect import signature , _ParameterKind, _empty, isbuiltin
from .class_recorder import get_class, KINDS, record_class
from .base import reconfig
import math
from enum import Enum 

from .io import load_config
parser_loockup = {}

def get_parser_class(type_):
    return get_class(KINDS.PARSER, type_)

class AnyParserConfig(BaseModel):
    """ A base model for any kind of parser """
    type: Union[List[Union[str, Callable]], str, Callable] = ""
    class Config:
        extra = Extra.allow

# Config for online built parser
class ParserConfig(BaseModel):
    kind: KINDS = KINDS.PARSER
    type: str = ""
    class Config:
        validate_assignment = True
        extra = "forbid"
        
# Config for parser classes 
class ParserElementConfig(BaseModel):    
    kind: KINDS = KINDS.PARSER
    type: str = ""
    class Config:
        validate_assignment = True
        extra = "forbid"
        
class BaseParser:       
    """ Callable Parser class """      
    Config = ParserElementConfig
    
    def __init_subclass__(cls, **kwargs) -> None:
        if kwargs:
            cls.Config = create_model(  cls.__name__+"Config",  __base__=cls.Config, **kwargs)
   
    def __init__(self, 
           config: Optional[ParserElementConfig] = None, 
           **kwargs
        ) -> None:
        self.config = reconfig(self.Config, config, kwargs)
    
    @staticmethod
    def parse(value, config: Optional[ParserElementConfig]) -> Any:
        return value 
    
    def __call__(self, value: Any) -> Any:        
        return self.parse(value, self.config)


class _BuiltParser:
    Config = ParserConfig
    __parsers__ = [] # yes this is the list and it is defined in the class 
    
    def __init_subclass__(cls, **kwargs) -> None:
        if kwargs:
            cls.Config = create_model(  cls.__name__+"Config",  __base__=cls.Config, **kwargs)

    def __init__(self, config=None, **kwargs):
        self.config = reconfig(self.Config, config, kwargs)
    
    @classmethod
    def parse(cls, value, config):
        for parser in cls.__parsers__:
            value = parser(value, config)
        return value
    
    def __call__(self, value):
        return self.parse(value, self.config)        

    
def to_parser_class(_func_: Callable =None, *, type: Optional[str] = None) -> Type[BaseParser]:
    if _func_ is None:
        def parser_func_decorator(func):
            return _parser_func(func, type)
        return parser_func_decorator
    else:
        return _parser_func(_func_, type)


def _parser_func(func, type_):            
    if not hasattr(func, "__call__"):
        raise ValueError(f"{func} is not callable")
        
    try:    
        s = signature(func)
    except ValueError: # assume it is a builtin class with one argument 
        conf_args = {}
    else:
        posarg = False
        conf_args = {}
        for a,p in s.parameters.items():
            if not posarg: 
                if p.kind!=_ParameterKind.POSITIONAL_OR_KEYWORD:
                    if p.default != _empty:
                        raise ValueError("first function argument should not have default") 
                posarg = True
            else:
                if p.default == _empty:
                    raise ValueError("Only one positional argument accepted")
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
        
    Config = create_model(type_+"Config", **extras, **conf_args, __base__=BaseParser.Config)
    
    
    if conf_args: 
        conf_args_set = set(conf_args)        
        def parser_func_method(arg, config):
            return func(arg, **{a:getattr(config,a) for a in conf_args_set})
    else:
        def parser_func_method(arg, config):
            return func(arg)
            
    return type(type_+"Parser", (BaseParser,), {'Config':Config, 'parse': staticmethod(parser_func_method)})
    

def func_parser_parse(func):
    def f_parse(value, config):
        return func(value)
    return f_parse



_dynamic_parser_class_loockup = {}
def create_parser_class(
       parsers : Union[Callable, Type[BaseParser], Type[_BuiltParser], BaseParser, str, Iterable]
    ) -> Type[_BuiltParser]:
    """ create a new parser class 
    
    From a list of parser class or instance create a new parser class. The parse function of the new
    class will execute each individual parse of the input classes. 
    The Config class of the new parser class is a combination of all Configs
    
    Args:
        parser: A list of type :class:`BaseParser` or :class:`_BuiltParser` or callable or str (recorded parser name) 
    
    Return:
        Cls (Type[_BuiltParser]): A new parser class 
        
    Example:
    
    ::
    
        >>> from pydevmgr_core import create_parser_class
        >>> from pydevmgr_core.parsers import Clipped, Rounded
        >>> FBR = create_parser_class( (float, Rounded, Clipped) )
        >>> FBR.Config()
        FloatRoundedClippedConfig(kind=<KINDS.PARSER: 'Parser'>, type='Rounded', min=-inf, max=inf, ndigits=0)
        >>> f = FBR( min=0.0, max=9.0, ndigits=2)
        >>> f(5.768976976)
        5.77
        >>> f(12.2323)
        9.0    
    
    ... seealso::
        - :func:`parser`
        - :class:`BaseParser`
        
    """
    
    if isinstance(parsers, str):        
        return get_parser_class(parsers)     
    elif isinstance(parsers, type) and issubclass(parsers, (BaseParser, _BuiltParser)): 
        return parsers
    
    try: # this can be the case if parsers is a type like float
        return get_parser_class(parsers) 
    except (ValueError, TypeError):
        pass
        
    if not hasattr(parsers, "__iter__") or isinstance(parsers, type):
        parsers = [parsers]
    
    # convert str to class before checking in loockup
    parsers = tuple(get_parser_class(p) if isinstance(p,str) else p for p in parsers)
    
    try:
        ParserClass = _dynamic_parser_class_loockup[parsers]
    except KeyError:
        pass
    else:
        return ParserClass
    
    
    _cls_parsers = []
    _model_bases = []
    _name = ""
    _type = ""
    
    
    for obj in parsers:  
        if isinstance(obj, (BaseParser, _BuiltParser)):
            ParserCls = obj.__class__
            _cls_parsers.append( ParserCls.parse )
            Tmp_model = create_model( ParserCls.Config.__name__, **obj.config.dict(exclude_unset=True), __base__= ParserCls.Config)
            _model_bases.append(Tmp_model)
            _name += ParserCls.__name__ + str(id(obj.config))
            _type += str(ParserCls.Config.__fields__['type'].default)
        elif isinstance(obj, type) and issubclass(obj, (BaseParser, _BuiltParser)): 
            ParserCls = obj 
            _cls_parsers.append( ParserCls.parse )                                      
            _model_bases.append(obj.Config)
            _name +=  ParserCls.__name__         
            _type += str(ParserCls.Config.__fields__['type'].default)
            
        elif hasattr(obj, "__call__"):
            _cls_parsers.append( func_parser_parse(obj) )
            _name += getattr(obj, "__name__", "F"+str(id(obj))).capitalize()
            _type += getattr(obj, "__name__", "F"+str(id(obj))).capitalize()
        else:
            raise ValueError(f"Expecting valid parser object got a {type(obj)}")  
                
    if _model_bases:                    
        Config = type(_name+"Config", tuple(_model_bases), {'type':_type})
        ParserClass = type(_name, (_BuiltParser,), {'Config':Config, '__parsers__':_cls_parsers})
    else:
        Config = type(_name+"Config", (ParserConfig,), {'type':_type})
        ParserClass = type(_name, (_BuiltParser,), {'__parsers__':_cls_parsers, 'Config':Config})
    _dynamic_parser_class_loockup[parsers] = ParserClass 
    if _type: 
        record_class(ParserClass, overwrite=True)
    return ParserClass

# def parser(parsers, config=None, **kwargs):
#     Parser = create_parser_class(parsers)
#     return Parser(config=config, **kwargs)        

def parser(parsers, config=None, **kwargs):
    """ return a :class:`BaseParser` object 
    
    Args:
       parsers: :class:`BaseParser` or :class:`_BuiltParser` or :class:`BaseParser.Config`
                or dict or string. 
                Definne the parser class used
       config: optional, configuration of the parser 
       * * kwargs:  Additional key/value configuration pairs 
       
    Exemple::
    
    ::
    
        >>> from pydevmgr_core import parser
        >>> from pydevmgr_core.parsers import Bounded, Rounded
        >>> p = parser( (float,Bounded,Rounded), min=0, max=1.0, ndigits=2)
        >>> p('0.223546243')
        0.22
        >>> p(5.0)
        ValueError: 5.0 is higher than 1.0
        
        Note:
        >>>  p = parser( (float,"Bounded","Rounded"), min=0, max=1.0, ndigits=2)
        # works as well as Bounded and Rounded are recorded classes
        
    ::
       
        >>> from pydevmgr_core.parsers import parser, Formula, Clipped
        >>> p = parser( (float, Formula, Clipped), formula="2*x+10", max=100)
        >>> [p(10), p(20), p(30), p(40), p(50), p(60)]
        [30.0, 50.0, 70.0, 90.0, 100.0, 100.0]
        
    
        
    .. seealso::
    
        :func:`create_parser_class`
        
    """ 
    if isinstance(parsers, (BaseParser, _BuiltParser)) and not config and not kwargs:
        return parsers
    
    if isinstance(parsers, AnyParserConfig): # Use for a generic config of parser
        Parser = create_parser_class(parsers.type)
        kwargs = {**kwargs, **parsers.dict(exclude=set(["type"]))}
        
    elif isinstance(parsers, (BaseParser.Config, _BuiltParser.Config)):
        return get_parser_class(parsers.type)(config=parsers, **kwargs)
        
    elif isinstance(parsers, dict):
        type_ = parsers.get('type', None)
        if not type_ :
            raise ValueError('parser type cannot be None')
        Parser = create_parser_class(type_)
        parsers = dict(parsers) # make a copy 
        parsers.pop("type", None) # type shall be inside the class definition (always as a string)
        kwargs = {**parsers, **kwargs}    
    else:    
        Parser = create_parser_class(parsers)
    return Parser(config=config, **kwargs)        


ParserVar = TypeVar('ParserVar')
class _BaseParserTyping(Generic[ParserVar]):
    _parser = None
    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        # __modify_schema__ should mutate the dict it receives in place,
        # the returned value will be ignored
        #field_schema.update()
        pass

    @classmethod
    def validate(cls, v, field: ModelField):
        
        errors = []

        if field.sub_fields:
            if len(field.sub_fields)>1:
                raise ValidationError(['to many field Defaults require and accept only one argument'], cls)
            val_f = field.sub_fields[0]
                       
            valid_value, error = val_f.validate(v, {}, loc='value')
            
            if error:    
                errors.append(error)
        else:
            val_f = v

        if errors:
            raise ValidationError(errors, cls)

        if cls._parser:
            valid_value = cls._parser(val_f)

            # try:
            #     valid_value = cls._parser(val_f)
            # except ValueError as er:
            #     errors.append(er)
        else:
            valid_value = val_f
            
        
        return valid_value
    
    def __repr__(self):
        return f'{self.__class__.__name__}({super().__repr__()})'

def conparser(parsers, **kwargs):
     """ Build a typing anotation parser for pydantic Models 
        
     Example: 

     ::
        
        from pydantic import BaseModel
        from pydevmgr_core import conparser

        class Conf(BaseModel):
            x: conparser( [float, "Bounded"], min=0, max=10) = 5.0
        
        

        # ValidationError
        >>> Conf(x=11.0)
        ValidationError: 1 validation error for Conf
        x
          11.0 is higher than 10.0 (type=value_error)
        
     """
     p = parser( parsers, **kwargs)
     return type( p.__class__.__name__+"Type", (_BaseParserTyping, ), {"_parser": p})



class _BaseModelConfigParse(BaseModel):
    class Config:
        extra = "allow"
@record_class
class ConfigParse(BaseParser):
    class Config(BaseParser.Config):
        type: str = "ConfigParse"
        model: Optional[Type] = _BaseModelConfigParse
        
    @staticmethod
    def parse(value, config):
        if isinstance( value, str):
            value = load_config( value )
        if not isinstance( value, (BaseModel, dict) ):
            raise ValueError("input shall be a file path, a BaseModel or dictionary ")
        if config.model:
            if value is None:
                return config.model()
            return config.model.parse_obj(value)
        if value is None:
            return {}
        return value



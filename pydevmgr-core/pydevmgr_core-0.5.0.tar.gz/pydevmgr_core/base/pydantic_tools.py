from pydevmgr_core.base.class_recorder import get_class, KINDS
from pydantic import BaseModel, ValidationError
from pydantic.fields import ModelField
from typing import Optional, TypeVar, Generic 

from .io import load_config

RecVar= TypeVar('RecVar')
GenVar = TypeVar('GenVar')
GenConfVar = TypeVar('GenConfVar')


def _isdefault(field):
    try:
        return issubclass(field.type_, Defaults)
    except Exception:
        return False
                

def _default_walk_unset(  default: BaseModel, new: BaseModel ):
    
    if not isinstance( new, BaseModel ):
        return 
    
    fields = default.__fields__
    
    for k, v in default:
        if k in fields and _isdefault(fields[k]):
            sub = getattr(new, k)
            _default_walk_unset(v, sub)
        else:
            if not k in new.__fields_set__:
                # add the value directly inside __dict__ 
                # This is necessary otherwhise it will not work recursively 
                # Can be a huge draw back but not sure how to fix it, adding in __fields_set__ break the recursibility
                new.__dict__[k] = v
                # new.__fields_set__.add(k)


def _default_walk_set(  default: BaseModel, new: BaseModel ):
    
    if not isinstance( new, BaseModel ):
        return 
    
    
    # if new.cfgfile:
    #     cfgfile_data = io.load_config(new.cfgfile) 
    #     cfgfile_model = new.__class__.parse_obj(cfgfile_data)
    #     _default_walk_set( default, cfgfile_model )
    #     default =  cfgfile_model 


    fields = default.__fields__
    
    for k, v in default:
        if k in fields and _isdefault(fields[k]):
            sub = getattr(new, k)
            _default_walk_set(v, sub)
        else:
            if not k in new.__fields_set__ or ("__default__"+k) in new.__fields_set__:
                # add the value directly inside __dict__
                new.__dict__[k] = v
                # If the field has been set by the walker the __key shall be also in __fields__set__
                # so we need to update it to keep it recursive. The draw back is keys liek "__key" in __fields__set__
                # but should not be a problem as it is used mostly for excluding stuff 
                new.__fields_set__.add("__default__"+k)
                new.__fields_set__.add(k)


class Defaults(Generic[RecVar]):
    """ Make the value of a default submodel the default values of the incoming payload 
    """
    _walker = _default_walk_set
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
        if not field.sub_fields:
            # Generic parameters were not provided so we don't try to validate
            # them and just return the value as is
            return v
        if len(field.sub_fields)!=1:
            raise ValidationError(['to many field Defaults require and accept only one argument'], cls)
            
        
        val_f = field.sub_fields[0]
        errors = []
        
        valid_value, error = val_f.validate(v, {}, loc='value')
        

        if error:
            errors.append(error)
        if errors:
            raise ValidationError(errors, cls)
        if field.default is not None:
            cls._walker(field.default, valid_value) 
        # Validation passed without errors, return validated value
        return valid_value
    
    def __repr__(self):
        return f'{self.__class__.__name__}({super().__repr__()})'


class Defaults2(Defaults):
    _walker = _default_walk_unset



class GenObject(Generic[GenVar]):
    """ Make the value of a default submodel the default values of the incoming payload 
    """
    _child_kind = None    
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
    def validate_child(cls, kind, type_):
        if kind is not None and kind!=cls._child_kind:
            raise ValueError(f"expecting a {cls._child_kind} configuration got a {kind}")
        if type_ is None:
            raise ValueError(f"{cls.__name__} must define a type")
        return cls._child_kind, type_
    
    @classmethod
    def validate(cls, v, field: ModelField):
                    
        if field.sub_fields:
            if len(field.sub_fields)!=1:
                raise ValidationError(['to many field GenDevice require and accept only one argument'], cls)
        

            val_f = field.sub_fields[0]
            errors = []
        
            valid_value, error = val_f.validate(v, {}, loc='value')
        
        

            if error:
                errors.append(error)
            if errors:
                raise ValidationError(errors, cls)
        else:
            valid_value = v

        if isinstance(valid_value, BaseModel):
            kind = getattr(valid_value, 'kind', None)
            cls.validate_child(kind, getattr(valid_value, 'type', None))

        elif isinstance(valid_value, dict):

            kind, type_ = cls.validate_child( 
                   valid_value.get('kind', None), 
                   valid_value.get('type', None)
            )
            
                
            Obj = get_class(kind, type_)
            valid_value = Obj.Config.parse_obj(valid_value)
        else:
            raise ValueError(f"Unexpected value for {cls.__name__}")
        # Validation passed without errors, return validated value
        return valid_value
    
    def __repr__(self):
        return f'{self.__class__.__name__}({super().__repr__()})'


class GenManager(GenObject):   
    _child_kind = KINDS.MANAGER

class GenDevice(GenObject):
    _child_kind = KINDS.DEVICE

class GenInterface(GenObject):
    _child_kind = KINDS.INTERFACE

class GenNode(GenObject):
    _child_kind = KINDS.NODE

class GenRpc(GenObject):
    _child_kind = KINDS.RPC

class GenParser(GenObject):
    _child_kind = KINDS.PARSER




class _BaseModelGenConf(BaseModel):
    class Config:
        extra = "allow"

class GenConf(Generic[GenConfVar]):
    """ Parse a Model. If the input is a string it is interpreted as a path to a config file 

    The model is loaded from the config file which must have an absolute path or a path relative 
    to one of the path defined in the $CFGPATH env varaible 
    
    A Node input will be interpreted as an empty dictionary (Model built without arguments). It will 
    fail if model has required entries 
    Example: 

    ::
        
        form pydevmgr_core import BaseDevice, GenConf

        class Config(BaseDevice.Config):
            child :  GenConf[BaseDevice.Config] = BaseDevice.Config()

        c = Config( child={})
        c = Config( child="/path/to/my/file.yml")
        

    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        pass
    
    
    @classmethod
    def validate(cls, value, field: ModelField):
                    
        if field.sub_fields:
            if len(field.sub_fields)!=1:
                raise ValidationError(['to many field GenConf require and accept only one argument'], cls)
                
        

            Model = field.sub_fields[0]
            if isinstance( Model, ModelField):
                Model = Model.type_
            
            if not hasattr(Model, "parse_obj"):
                 raise ValueError(f"field of GenConf is not a BaseModel but a {type(Model)}")
        else:
            Model = _BaseModelGenConf
            
        if isinstance( value, str):
            value = load_config( value )
        # if value is None:
        #     return Model()
        return Model.parse_obj(value)

    def __repr__(self):
        return f'{self.__class__.__name__}({super().__repr__()})'



if __name__ == "__main__":
    from pydantic import BaseModel
    from pydevmgr_core import BaseDevice, record_class
    from typing import Dict 
    
    @record_class
    class Toto(BaseDevice):
        class Config(BaseDevice.Config):
            type = "Toto"
            voltage: float = 12.0
    
    class C(BaseModel):
        n1: int = 0
        n2: int = 0

    class B(BaseModel):
        x: float = 0.0
        y: float = 0.0
        c1: Defaults[C] = C(n1=1)
        c2: Defaults[C] = C(n1=2)
        c3: C = C(n1=3)

    RB = Defaults[B]
    class A(BaseModel):
        b1: Defaults[B] = B(y=9)
        b2: Defaults[B] = B(y=8, c1=C(n1=100))
        
        devices: Dict[str,GenDevice] = {}

    a =A(b1={'x':1.0, 'c1':{'n2':10},  'c2':{'n2':20}, 'c3':{'n2':30}},    b2={'c1':{}}, 
            devices={ 'toto':{'type':'Toto'}, 'toto2':Toto.Config()}
    
        )

    print(a)
    
    assert a.b1.x == 1.0
    assert a.b1.y == 9.0 
    assert a.b1.c1.n2 == 10
    assert a.b1.c1.n1 == 1
    assert a.b1.c2.n1 == 2
    assert a.b1.c3.n1 == 0 # c3 is not a Defaults 

    assert a.b2.c1.n1 == 100
    
    assert "y" in a.b1.dict(exclude_unset=True)
  

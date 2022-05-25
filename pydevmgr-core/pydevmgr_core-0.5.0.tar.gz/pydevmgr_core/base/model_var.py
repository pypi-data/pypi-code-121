from pydantic import BaseModel, ValidationError, Field
from pydantic.fields import ModelField
from typing import TypeVar, Generic, Any, Iterable, Dict, List, Type

ValType = TypeVar('ValType')

class NodeVar(Generic[ValType]):
    """
    A Field as NodeVar. Does not do validation by itself but it is used
    as an iddentifier of a node value
    """
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
        if len(field.sub_fields)>1:
            raise ValidationError(['to many field NodeVar accep only one'], cls)
        val_f = field.sub_fields[0]
        errors = []
        
        valid_value, error = val_f.validate(v, {}, loc='value')
        if error:
            errors.append(error)
        if errors:
            raise ValidationError(errors, cls)
        # Validation passed without errors, return validated value
        return valid_value
    
    def __repr__(self):
        return f'{self.__class__.__name__}({super().__repr__()})'

class NodeVar_RW(NodeVar):
    """ Alias of :class:`NodeVar` """
    pass
class NodeVar_W(NodeVar):
    """ Write Only version of :class:`NodeVar`"""
    pass
    
class NodeVar_R(NodeVar):
    """ Read Only version of :class:`NodeVar` """
    pass

class StaticVar(Generic[ValType]):
    """
    A Field as StaticVar. Does not do validation by itself but it is used
    as an iddentifier of a static attribute of the input object of DataLink
    """
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
        if len(field.sub_fields)>1:
            raise ValidationError(['to many field StaticVar accept only one'], cls)
        val_f = field.sub_fields[0]
        errors = []
        
        valid_value, error = val_f.validate(v, {}, loc='value')
        if error:
            errors.append(error)
        if errors:
            raise ValidationError(errors, cls)
        # Validation passed without errors, return validated value
        return valid_value
    
    def __repr__(self):
        return f'{self.__class__.__name__}({super().__repr__()})'


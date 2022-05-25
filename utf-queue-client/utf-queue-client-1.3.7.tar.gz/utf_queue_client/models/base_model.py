from typing import Optional, List, Any
import jsonschema
from ..exceptions import SchemaValidationError, ValidationError
from pydantic import (
    BaseModel as PydanticBaseModel,
    PrivateAttr,
    ValidationError as PydanticValidationError,
)
from .schemas import QueueMessageSchema

__all__ = ["LegacyBaseModel", "BaseModelWithValidation"]


class BaseModelWithValidation(PydanticBaseModel):
    __validator: Optional[Any] = PrivateAttr()

    def __init__(self, dict_: Optional[dict] = None, **kwargs):
        self.__validator = None
        init_kwargs = {**(dict_ or {}), **kwargs}
        try:
            super().__init__(**init_kwargs)
            self._set_schema(QueueMessageSchema.get_schema(), self.__class__.__name__)
        except PydanticValidationError as e:
            raise ValidationError(e)

    def _set_schema(self, schema: dict, class_name: str):
        validator_class = jsonschema.validators.validator_for(schema)
        validator_class.check_schema(schema)
        self.__validator = validator_class(
            schema["definitions"][class_name],
            resolver=jsonschema.RefResolver.from_schema(schema),
        )

    def as_dict(self) -> dict:
        return self.dict()

    def validate_schema(self):
        try:
            d = self.dict(exclude_unset=True, exclude_none=True)
            self.__validator.validate(d)
        except jsonschema.exceptions.ValidationError as e:
            raise SchemaValidationError(e)


class LegacyBaseModel(dict):
    def __init__(self, dict_: Optional[dict] = None, **kwargs):
        self.__validator = None
        super().__init__(dict_ or {})
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])

    def _set_schema(self, schema: dict, class_name: str):
        validator_class = jsonschema.validators.validator_for(schema)
        validator_class.check_schema(schema)
        self.__validator = validator_class(
            schema["definitions"][class_name],
            resolver=jsonschema.RefResolver.from_schema(schema),
        )

    def validate_schema(self):
        try:
            self.__validator.validate(self.as_dict())
        except jsonschema.exceptions.ValidationError as e:
            raise SchemaValidationError(e)

    def __getattribute__(self, name):
        try:
            return self[name]
        except KeyError:
            return dict.__getattribute__(self, name)

    def __setattr__(self, key, value):
        self[key] = value
        return value

    @property
    def __dict__(self) -> dict:
        dict_ = {}
        for key in self:
            if key != "_LegacyBaseModel__validator":
                val = self[key]
                if val is not None:
                    dict_[key] = val
                    if isinstance(val, LegacyBaseModel):
                        dict_[key] = val.as_dict()
        return dict_

    def copy(self) -> "LegacyBaseModel":
        return self.convert_dict_to_model(self.as_dict())

    def apply(self, new_dict) -> bool:
        """
        Apply values from new_dict into self

        Args:
            new_dict:

        Returns:
            True if anything was changed
        """
        anything_changed = False
        for key in new_dict:
            value = new_dict[key]
            if key in self.__dict__:
                curr_value = self[key]
                if type(value) != type(curr_value):
                    raise ValueError()
                if value != curr_value:
                    anything_changed = True
                    self[key] = value
        return anything_changed

    def as_dict(self) -> dict:
        return self.__dict__

    @classmethod
    def get_class_attrs(cls) -> List[str]:
        attrs = set(dir(cls)) - set(dir(cls.__base__))
        return [attr for attr in attrs if not callable(getattr(cls, attr))]

    @classmethod
    def create_model_from_dict(cls, dict_: dict) -> "LegacyBaseModel":
        return cls(LegacyBaseModel.convert_dict_to_model(dict_))

    @staticmethod
    def convert_dict_to_model(dict_: dict) -> "LegacyBaseModel":
        """Given a dictionary, converts it to a LegacyBaseModel instance.

        Converts nested dictionaries (dictionaries in dictionaries and dictionaries in other iterable objects)

        Args:
            dict_ (dict): The JSON dictionary. We don't care what the dictionary is used for, though

        Returns:
            BaseModel: The same dictionary, but with "." access
        """
        dot_dict = LegacyBaseModel(dict_)
        for key in dict_:
            value = dict_[key]
            if isinstance(value, dict):
                setattr(dot_dict, key, LegacyBaseModel.convert_dict_to_model(value))
            if is_list(value):
                encountered_lists = [value]
                for list_value in encountered_lists:
                    for idx, elem in enumerate(list_value):
                        if isinstance(elem, dict):
                            list_value[idx] = LegacyBaseModel.convert_dict_to_model(elem)
                        if is_list(elem):
                            encountered_lists.append(elem)
        return dot_dict


def is_list(suspected_list):
    if isinstance(suspected_list, str):
        return False
    if isinstance(suspected_list, dict):
        return False
    try:
        for _ in suspected_list:
            return True
    except (AttributeError, TypeError):
        return False

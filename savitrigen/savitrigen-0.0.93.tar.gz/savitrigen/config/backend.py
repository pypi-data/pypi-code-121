import typing
from dataclasses import dataclass, field
from savitrigen.guideline import (
    check_module_naming,
    check_field_naming
)

@dataclass
class Module(object):
    fields:dict
    _fields:dict = field(init=False, repr=False)

    unicon:str = ''
    route:bool = False
    report:bool = False
    presets:list = None

    """Those below are unused"""
    documentation:str = 'undocumented'
    translation:dict = None

    @property
    def fields(self) -> dict:
        ms = dict()

        for k, v in self._fields.items():
            ms[k] = {
                f_k: f_v
                for f_k, f_v in v.items()
                if f_v is not None
            }

        return ms

    @fields.setter
    def fields(self, value:dict) -> None:
        self._fields = value

@dataclass
class Field(object):
    label:str
    type:str = None

    description:str = None

    required:bool = False
    readonly:bool = False
    values:list = None
    mask:str = None

    """Module specific properties"""
    module:str = None
    index:typing.Union[str,list[str]] = None


@dataclass
class BackendConfig(object):
    entities:dict
    _entities:dict = field(init=False, repr=False)

    plugins:list[str] = None

    @property
    def entities(self) -> dict:
        return self._entities

    @entities.setter
    def entities(self, value:dict) -> None:
        ms = dict()

        for k, v in value.items():
            ms[k] = module = Module(**v)
            check_module_naming(k)

            for f_k, f_v in module.fields.items():
                module.fields[f_k] = Field(**f_v).__dict__
                check_field_naming(f_k)

        self._entities = ms

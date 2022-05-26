from __future__ import annotations

from typing import List, NamedTuple

from sila2.code_generator.template_objects.basics import Field, Import, Type


class ClientUnobservableProperty(NamedTuple):
    name: str
    type: Type
    docstring: str

    @property
    def imports(self) -> List[Import]:
        return self.type.imports


class ClientObservableProperty(NamedTuple):
    name: str
    type: Type
    docstring: str

    @property
    def imports(self) -> List[Import]:
        return self.type.imports


class ClientUnobservableCommand(NamedTuple):
    name: str
    parameters: List[Field]
    docstring: str

    @property
    def imports(self) -> List[Import]:
        ret = []
        for par in self.parameters:
            ret.extend(par.imports)
        return ret


class ClientObservableCommand(NamedTuple):
    name: str
    parameters: List[Field]
    docstring: str
    has_intermediate_responses: bool

    @property
    def imports(self) -> List[Import]:
        ret = []
        for par in self.parameters:
            ret.extend(par.imports)
        return ret


class ClientMetadata(NamedTuple):
    name: str
    docstring: str
    type: Type

    @property
    def imports(self) -> List[Import]:
        return self.type.imports

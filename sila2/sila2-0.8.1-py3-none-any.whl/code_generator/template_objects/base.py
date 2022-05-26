from typing import List, NamedTuple

from sila2.code_generator.template_objects.basics import Field, Import, Type


class ServerMetadata(NamedTuple):
    name: str
    docstring: str


class ServerUnobservableProperty(NamedTuple):
    name: str
    type: Type
    docstring: str

    @property
    def imports(self) -> List[Import]:
        return self.type.imports


class ServerObservableProperty(NamedTuple):
    name: str
    type: Type
    docstring: str

    @property
    def imports(self) -> List[Import]:
        return self.type.imports


class ServerUnobservableCommand(NamedTuple):
    name: str
    parameters: List[Field]
    responses: List[Field]
    docstring: str

    @property
    def imports(self) -> List[Import]:
        ret = []
        for par in self.parameters:
            ret.extend(par.imports)
        return ret


class ServerObservableCommand(NamedTuple):
    name: str
    parameters: List[Field]
    intermediate_responses: List[Field]
    responses: List[Field]
    docstring: str

    @property
    def imports(self) -> List[Import]:
        ret = []
        for par in self.parameters:
            ret.extend(par.imports)
        return ret
